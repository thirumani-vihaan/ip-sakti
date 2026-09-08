"""POST /api/export/pdf — render a PDF from an already-validated ChatResponse."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response

from app.utils.pdf_generator import render_pdf
from app.workflow.schema import ChatResponse

router = APIRouter()


@router.post("/api/export/pdf")
def export_pdf(resp: ChatResponse) -> Response:
    # Grounding on export: refuse to render a claim that is not backed by a citation to
    # this response's own sources, so a client cannot forge an uncited "IP-SAKTI report".
    source_ids = {s.id for s in resp.sources}
    for c in resp.claims:
        if not c.source_ids or not set(c.source_ids) <= source_ids:
            raise HTTPException(status_code=422, detail="ungrounded claim cannot be exported")
    return Response(content=render_pdf(resp), media_type="application/pdf")
