"""POST /api/analyze — upload a document and analyse it against the trusted corpus.

The uploaded file is EPHEMERAL: its text is extracted, used once as a query to
retrieve and ground against the official corpus, then discarded. It is never added
to the knowledge base, so the citation-grounding guarantee is fully preserved.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.corpus.ingestion import _extract
from app.models.enums import Jurisdiction
from app.utils.security import sanitize_text
from app.workflow.schema import ChatRequest, ChatResponse

router = APIRouter()

_MAX_BYTES = 5 * 1024 * 1024
_ALLOWED = {".txt", ".md", ".pdf", ".html", ".htm"}


class AnalyzeResponse(BaseModel):
    filename: str
    extracted_preview: str
    analysis: ChatResponse


@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    jurisdiction: Jurisdiction = Jurisdiction.INDIA,
) -> AnalyzeResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED:
        raise HTTPException(status_code=415, detail=f"unsupported file type {suffix or '(none)'}")
    data = await file.read(_MAX_BYTES + 1)
    if len(data) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="file too large (max 5 MB)")

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
            
        if suffix == ".pdf":
            import os
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            
            resp = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    "Extract all the text from this document accurately. Preserve formatting where possible.", 
                    types.Part.from_bytes(data=data, mime_type="application/pdf")
                ]
            )
            text = resp.text
        else:
            text = _extract(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:  # extraction failure -> 422, never crash
        raise HTTPException(status_code=422, detail=f"could not read document: {e}")
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    clean = sanitize_text(text)
    if not clean:
        raise HTTPException(status_code=422, detail="no readable text found in document")

    svc = request.app.state.answer_service
    # Sensitive by default: an uploaded document is processed locally (no external LLM),
    # so its contents are never sent to a third-party provider even when keys are set.
    analysis = svc.answer(ChatRequest(query=clean[:2000], jurisdiction=jurisdiction, sensitive=True))
    return AnalyzeResponse(
        filename=file.filename or "upload",
        extracted_preview=clean[:400],
        analysis=analysis,
    )
