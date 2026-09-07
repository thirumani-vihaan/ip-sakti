"""GET /api/sources — corpus provenance registry (versions, status, authority)."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.corpus.sources import SourceInfo, source_registry

router = APIRouter()


class SourcesResponse(BaseModel):
    corpus_version: str
    count: int
    sources: list[SourceInfo]


@router.get("/api/sources", response_model=SourcesResponse)
def sources(request: Request) -> SourcesResponse:
    entries = request.app.state.corpus_manifest
    registry = source_registry(entries)
    return SourcesResponse(
        corpus_version=request.app.state.settings.corpus_version,
        count=len(registry),
        sources=registry,
    )
