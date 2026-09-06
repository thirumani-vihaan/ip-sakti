"""BM25 keyword index for exact statute/section/form matching."""
from __future__ import annotations

import re
from typing import Optional, Protocol, runtime_checkable

from rank_bm25 import BM25Okapi

from app.retrieval.chunking import Chunk
from app.retrieval.vector_store import chunk_to_source
from app.workflow.schema import RetrievalHit

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tok(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


@runtime_checkable
class KeywordIndex(Protocol):
    def add(self, chunks: list[Chunk]) -> None:
        ...

    def search(self, query: str, k: int = 5, jurisdiction: Optional[str] = None) -> list[RetrievalHit]:
        ...


class BM25Index:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._tokens: list[list[str]] = []
        self._bm25: Optional[BM25Okapi] = None
        self._dirty: bool = False

    def add(self, chunks: list[Chunk]) -> None:
        # accumulate incrementally; defer the (expensive) index build to first search
        for c in chunks:
            self._chunks.append(c)
            self._tokens.append(_tok(c.text + " " + (c.section or "")))
        self._dirty = True

    def _ensure_built(self) -> None:
        if self._dirty:
            self._bm25 = BM25Okapi(self._tokens) if self._tokens else None
            self._dirty = False

    def search(self, query: str, k: int = 5, jurisdiction: Optional[str] = None) -> list[RetrievalHit]:
        self._ensure_built()
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tok(query))
        ranked = sorted(zip(scores, self._chunks), key=lambda x: (-x[0], x[1].id))
        hits: list[RetrievalHit] = []
        for s, c in ranked:
            if jurisdiction and c.jurisdiction != jurisdiction:
                continue
            if s <= 0:
                continue
            hits.append(
                RetrievalHit(evidence_id=c.id, text=c.text, score=float(s), source=chunk_to_source(c))
            )
            if len(hits) >= k:
                break
        return hits
