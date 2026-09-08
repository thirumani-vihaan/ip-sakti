"""POST /api/export/pdf — render a PDF from an already-validated ChatResponse."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from app.utils.pdf_generator import render_pdf
from app.workflow.schema import ChatResponse

router = APIRouter()


_IMMUTABLE = ("title", "section", "url", "local_excerpt", "status", "authority",
              "effective_date", "document_hash")


@router.post("/api/export/pdf")
def export_pdf(resp: ChatResponse, request: Request) -> Response:
    # Authenticate every source against the server's canonical corpus record: reject unknown
    # ids and any tampered immutable field (title/section/url/excerpt/status/authority/date/hash),
    # so a forged "IP-SAKTI report" cannot show fabricated source metadata or quoted evidence.
    canonical: dict = request.app.state.evidence_sources
    for s in resp.sources:
        c = canonical.get(s.id)
        if c is None:
            raise HTTPException(status_code=422, detail=f"unrecognised source: {s.id}")
        for field in _IMMUTABLE:
            if getattr(s, field) != getattr(c, field):
                raise HTTPException(status_code=422, detail=f"tampered source field '{field}' for {s.id}")
    # Grounding: every claim must cite one of those authenticated sources.
    source_ids = {s.id for s in resp.sources}
    for claim in resp.claims:
        if not claim.source_ids or not set(claim.source_ids) <= source_ids:
            raise HTTPException(status_code=422, detail="ungrounded claim cannot be exported")
    return Response(content=render_pdf(resp), media_type="application/pdf")
