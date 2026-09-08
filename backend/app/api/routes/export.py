"""POST /api/export/pdf — render a PDF from an already-validated ChatResponse."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from app.utils.pdf_generator import render_pdf
from app.workflow.schema import ChatResponse

router = APIRouter()


@router.post("/api/export/pdf")
def export_pdf(resp: ChatResponse, request: Request) -> Response:
    # Authenticate every source against the server's real corpus (id + provenance hash),
    # so a client cannot fabricate a source and cite it in a forged "IP-SAKTI report".
    known: dict[str, str] = request.app.state.evidence_hashes
    for s in resp.sources:
        if known.get(s.id) != s.document_hash:
            raise HTTPException(status_code=422, detail=f"unrecognised or tampered source: {s.id}")
    # Grounding: every claim must cite one of those authenticated sources.
    source_ids = {s.id for s in resp.sources}
    for c in resp.claims:
        if not c.source_ids or not set(c.source_ids) <= source_ids:
            raise HTTPException(status_code=422, detail="ungrounded claim cannot be exported")
    return Response(content=render_pdf(resp), media_type="application/pdf")
