"""AnswerService: orchestrates retrieve -> relevance-gate -> generate -> validate -> strength/abstain."""
from __future__ import annotations

import re
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

_STOP = {
    "a", "an", "the", "to", "of", "in", "on", "at", "for", "and", "or", "is", "are",
    "be", "can", "i", "my", "how", "do", "does", "what", "about", "with", "you", "your",
    "this", "that", "it", "as", "by", "from", "was", "were", "will", "shall", "any", "such",
    "under", "say", "says", "use", "used",
}
_WORD_RE = re.compile(r"[a-z0-9]+")


def _content_tokens(text: str) -> set[str]:
    return {t for t in _WORD_RE.findall(text.lower()) if t not in _STOP and len(t) > 1}


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

        # relevance gate: out-of-corpus if the query shares no content word with any hit
        q_terms = _content_tokens(req.query)
        if not any(q_terms & _content_tokens(h.text) for h in hits):
            return abstention_response("out_of_corpus", req, as_of, self.corpus_version)

        # Sensitive-Invention mode: never call an external LLM; process locally only.
        if req.sensitive:
            return self._extractive(
                req, hits, as_of, code="sensitive_local",
                message="Sensitive-Invention mode: processed locally; no external LLM call.",
            )

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

    def _extractive(self, req: ChatRequest, hits, as_of, code: str = "degraded",
                    message: str = "LLM unavailable; showing source passages without synthesis.") -> ChatResponse:
        # top passages become claims that cite themselves -> grounded by construction
        claims = [Claim(text=h.text, source_ids=[h.evidence_id]) for h in hits[:3]]
        valid, sources, warnings = validate_claims(claims, hits)
        strength = score_strength(valid, sources, extract_section_refs(req.query))
        warnings = warnings + [Warning(code=code, message=message)]
        return ChatResponse(
            claims=valid, sources=sources, warnings=warnings,
            answer_mode=AnswerMode.EXTRACTIVE, evidence_strength=strength,
            jurisdiction=req.jurisdiction, language=req.language,
            as_of=as_of, corpus_version=self.corpus_version,
        )
