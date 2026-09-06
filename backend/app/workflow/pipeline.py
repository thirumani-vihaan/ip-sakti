"""AnswerService: orchestrates retrieve -> relevance-gate -> generate -> validate -> strength/abstain."""
from __future__ import annotations

from datetime import date

from typing import Optional

from app.integrations.provider import (
    CircuitBreaker, EmbeddingProvider, LLMProvider, ProviderError,
)
from app.models.enums import AnswerMode
from app.offline.cache import DemoCache
from app.retrieval.hybrid import HybridRetriever
from app.workflow.abstention import abstention_response
from app.workflow.citation_validator import validate_claims
from app.workflow.evidence_strength import score_strength
from app.workflow.generation import generate_grounded
from app.workflow.reference_resolver import extract_section_refs
from app.workflow.schema import ChatRequest, ChatResponse, Claim, Warning

_RELEVANCE_MIN = 0.05


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class AnswerService:
    def __init__(
        self,
        retriever: HybridRetriever,
        llm: LLMProvider,
        embedder: EmbeddingProvider,
        corpus_version: str = "v0",
        cache: Optional[DemoCache] = None,
        breaker: Optional[CircuitBreaker] = None,
    ):
        self.retriever = retriever
        self.llm = llm
        self.emb = embedder
        self.corpus_version = corpus_version
        self.cache = cache
        self.breaker = breaker or CircuitBreaker()

    def answer(self, req: ChatRequest) -> ChatResponse:
        as_of = req.as_of or date.today()
        hits = self.retriever.retrieve(req.query, k=5, jurisdiction=req.jurisdiction.value, as_of=as_of)
        if not hits:
            return abstention_response("out_of_corpus", req, as_of, self.corpus_version)

        # relevance gate: reject out-of-corpus queries before generating anything
        qv = self.emb.embed([req.query])[0]
        top_rel = max(_cosine(qv, self.emb.embed([h.text])[0]) for h in hits)
        if top_rel < _RELEVANCE_MIN:
            return abstention_response("out_of_corpus", req, as_of, self.corpus_version)

        if self.breaker.open:
            return self._fallback(req, hits, as_of)
        try:
            claims = generate_grounded(self.llm, req.query, hits)
            self.breaker.record_success()
        except ProviderError:
            self.breaker.record_failure()
            return self._fallback(req, hits, as_of)

        valid, sources, warnings = validate_claims(claims, hits)
        if not valid:
            return abstention_response("unsupported", req, as_of, self.corpus_version, warnings)

        strength = score_strength(valid, sources, extract_section_refs(req.query))
        return ChatResponse(
            claims=valid, sources=sources, warnings=warnings,
            answer_mode=AnswerMode.LIVE, evidence_strength=strength,
            jurisdiction=req.jurisdiction, language=req.language,
            as_of=as_of, corpus_version=self.corpus_version,
        )

    def _fallback(self, req: ChatRequest, hits, as_of) -> ChatResponse:
        # outage: prefer an approved cached answer, else extractive (no-generation)
        if self.cache is not None:
            cached = self.cache.get(req.query)
            if cached is not None:
                return cached
        return self._extractive(req, hits, as_of)

    def _extractive(self, req: ChatRequest, hits, as_of) -> ChatResponse:
        # top passages become claims that cite themselves -> grounded by construction
        claims = [Claim(text=h.text, source_ids=[h.evidence_id]) for h in hits[:3]]
        valid, sources, warnings = validate_claims(claims, hits)
        strength = score_strength(valid, sources, extract_section_refs(req.query))
        warnings = warnings + [
            Warning(code="degraded", message="LLM unavailable; showing source passages without synthesis.")
        ]
        return ChatResponse(
            claims=valid, sources=sources, warnings=warnings,
            answer_mode=AnswerMode.EXTRACTIVE, evidence_strength=strength,
            jurisdiction=req.jurisdiction, language=req.language,
            as_of=as_of, corpus_version=self.corpus_version,
        )
