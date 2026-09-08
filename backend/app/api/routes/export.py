"""POST /api/export/pdf — render a PDF from a server-authenticated answer.

The endpoint does NOT trust a client-submitted ChatResponse as authoritative. It:
  1. authenticates every source against the canonical corpus (id + all immutable fields),
  2. requires every claim to cite one of those authenticated sources,
  3. renders only server-derived report metadata: client warnings are dropped, evidence
     strength is recomputed server-side, and corpus_version is the server value.
Remaining fields (jurisdiction, answer_mode) are bounded enums; a per-answer signed token
for byte-exact provenance is a documented roadmap item.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from app.utils.pdf_generator import render_pdf
from app.workflow.evidence_strength import score_strength
from app.workflow.schema import ChatResponse

router = APIRouter()

_IMMUTABLE = ("title", "section", "url", "local_excerpt", "status", "authority",
              "effective_date", "document_hash")


def _safe_response(resp: ChatResponse, corpus_version: str) -> ChatResponse:
    # server-authoritative metadata only: drop client warnings, recompute strength
    # conservatively (no query -> no exact-section HIGH), pin the real corpus version.
    strength = score_strength(resp.claims, resp.sources, set())
    return resp.model_copy(update={
        "corpus_version": corpus_version,
        "warnings": [],
        "evidence_strength": strength,
    })


@router.post("/api/export/pdf")
def export_pdf(resp: ChatResponse, request: Request) -> Response:
    canonical: dict = request.app.state.evidence_sources
    for s in resp.sources:
        c = canonical.get(s.id)
        if c is None:
            raise HTTPException(status_code=422, detail=f"unrecognised source: {s.id}")
        for field in _IMMUTABLE:
            if getattr(s, field) != getattr(c, field):
                raise HTTPException(status_code=422, detail=f"tampered source field '{field}' for {s.id}")
    source_ids = {s.id for s in resp.sources}
    for claim in resp.claims:
        if not claim.source_ids or not set(claim.source_ids) <= source_ids:
            raise HTTPException(status_code=422, detail="ungrounded claim cannot be exported")
    safe = _safe_response(resp, request.app.state.settings.corpus_version)
    return Response(content=render_pdf(safe), media_type="application/pdf")
