"""GET /api/search — transparent retrieval over the corpus (no generation).

Returns the ranked evidence the answer pipeline would ground on, so users can
inspect the sources directly. Same grounding invariant: every hit is a real,
server-assigned evidence id backed by a Source.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.models.enums import Jurisdiction
from app.workflow.schema import Source

router = APIRouter()


class SearchHit(BaseModel):
    evidence_id: str
    score: float
    source: Source


class SearchResponse(BaseModel):
    query: str
    jurisdiction: Jurisdiction
    results: list[SearchHit]


@router.get("/api/search", response_model=SearchResponse)
def search(
    request: Request,
    q: str = Query(min_length=1, max_length=2000),
    jurisdiction: Jurisdiction = Jurisdiction.INDIA,
    k: int = Query(5, ge=1, le=20),
) -> SearchResponse:
    svc = request.app.state.answer_service
    hits = svc.retriever.retrieve(q, k=k, jurisdiction=jurisdiction.value, as_of=date.today())
    return SearchResponse(
        query=q,
        jurisdiction=jurisdiction,
        results=[SearchHit(evidence_id=h.evidence_id, score=h.score, source=h.source) for h in hits],
    )
