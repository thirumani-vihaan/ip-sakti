"""Source registry: a provenance-first, public view of the corpus manifest.

Powers the "sources / changelog" surface — every document with its version,
in-force status, effective date and issuing authority, so users can audit what
the assistant is grounded on and see which laws are current vs superseded.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.corpus.manifest import ManifestEntry


class SourceInfo(BaseModel):
    id: str
    title: str
    url: str
    publisher: str
    version: str
    status: str
    authority_level: str
    jurisdiction: str
    effective_date: Optional[date] = None
    domains: list[str] = []


def source_registry(entries: list[ManifestEntry]) -> list[SourceInfo]:
    return [
        SourceInfo(
            id=e.id, title=e.title, url=e.url, publisher=e.publisher, version=e.version,
            status=e.status.value, authority_level=e.authority_level,
            jurisdiction=e.jurisdiction.value, effective_date=e.effective_date, domains=e.domains,
        )
        for e in entries
    ]
