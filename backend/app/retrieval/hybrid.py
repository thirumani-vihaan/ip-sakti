"""Hybrid retrieval: exact-ref resolution + reciprocal-rank fusion of vector & keyword.

Order of operations (matters):
  1. resolve exact Section/Form references in the query,
  2. gather vector + keyword candidates (each already jurisdiction-filtered),
  3. reciprocal-rank fuse,
  4. drop non-in-force sources (temporal eligibility; full as_of logic in T012),
  5. rank: exact-ref first, then fused score, then authority tie-break, then id.
"""
from __future__ import annotations

from typing import Optional

from app.integrations.provider import EmbeddingProvider
from app.models.enums import ForceState
from app.retrieval.keyword_index import KeywordIndex
from app.retrieval.vector_store import VectorStore
from app.workflow.reference_resolver import extract_section_refs
from app.workflow.schema import RetrievalHit

_RRF_K = 60
_AUTHORITY_RANK = {
    "statute": 0, "rule": 1, "notification": 2, "guideline": 3, "treaty": 4, "article": 5,
}


class HybridRetriever:
    def __init__(self, vector_store: VectorStore, keyword_index: KeywordIndex, embedder: EmbeddingProvider):
        self.vs = vector_store
        self.ki = keyword_index
        self.emb = embedder

    def retrieve(self, query: str, k: int = 5, jurisdiction: Optional[str] = None) -> list[RetrievalHit]:
        pool = max(k * 4, 12)
        vhits = self.vs.query(self.emb.embed([query])[0], k=pool, jurisdiction=jurisdiction)
        khits = self.ki.search(query, k=pool, jurisdiction=jurisdiction)

        scores: dict[str, float] = {}
        meta: dict[str, RetrievalHit] = {}
        for hits in (vhits, khits):
            for rank, h in enumerate(hits):
                scores[h.evidence_id] = scores.get(h.evidence_id, 0.0) + 1.0 / (_RRF_K + rank + 1)
                meta.setdefault(h.evidence_id, h)

        refs = extract_section_refs(query)

        def is_exact(h: RetrievalHit) -> int:
            sec = (h.source.section or "").lower().replace(" ", "")
            return 1 if sec and sec in refs else 0

        eligible = [h for h in meta.values() if h.source.status == ForceState.IN_FORCE]
        eligible.sort(
            key=lambda h: (
                -is_exact(h),
                -scores[h.evidence_id],
                _AUTHORITY_RANK.get(h.source.authority, 9),
                h.evidence_id,
            )
        )
        # fused RRF score is exposed on the hit for downstream evidence-strength
        return [h.model_copy(update={"score": scores[h.evidence_id]}) for h in eligible[:k]]
