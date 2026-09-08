"""Fixture-backed fake providers. Deterministic, offline, no credentials.

Design choices that matter:
- FakeLLM cites ONLY the evidence ids it is given (grounded by construction), so
  citation-validator tests can rely on it. Explicit hallucinate/malformed modes
  exist to exercise the validator's rejection paths.
- FakeEmbeddings uses a hashed bag-of-words vector, so cosine similarity reflects
  lexical overlap -> deterministic, reproducible retrieval in tests with no model.
- FakeTranslation preserves statute/section tokens verbatim.
"""
from __future__ import annotations

import hashlib
import math
import re

from app.integrations.provider import ProviderError
from app.retrieval.lexnorm import norm_tokens
from app.workflow.schema import Claim, RetrievalHit

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_LEGAL_TOKEN_RE = re.compile(r"(Section\s+\d+\([a-z]\)|Form\s+[IVX]+|s\.\s?\d+\([a-z]\)|s\.\s?\d+)", re.I)
_DIM = 256
_SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _best_sentence(query: str, text: str) -> str:
    """Pick the sentence of `text` with the most query-token overlap, so the fixture
    answer shows a passage relevant to the question rather than an arbitrary prefix."""
    qt = set(norm_tokens(query))
    sentences = [s.strip() for s in _SENT_RE.split(text) if s.strip()]
    if not sentences:
        return text.strip()
    return max(sentences, key=lambda s: len(qt & set(norm_tokens(s))))


class FakeLLM:
    def __init__(self, force_error: str | None = None, hallucinate: bool = False):
        self.force_error = force_error
        self.hallucinate = hallucinate

    def generate(self, prompt: str, evidence: list[RetrievalHit]) -> list[Claim]:
        if self.force_error in ("timeout", "rate_limit"):
            raise ProviderError(self.force_error, retryable=True)
        if self.force_error == "malformed":
            # cite an id that was never supplied -> validator must reject
            return [Claim(text="unsupported claim", source_ids=["e_missing"])]
        if not evidence:
            return []
        if self.hallucinate:
            return [Claim(text="Fabricated claim", source_ids=["e999"])]
        m = re.search(r"Question:\s*(.*)", prompt)
        query = m.group(1) if m else prompt
        return [
            Claim(
                text=f"Per {h.source.title} {h.source.section or ''}: {_best_sentence(query, h.text)}".strip(),
                source_ids=[h.evidence_id],
            )
            for h in evidence[:2]
        ]


class FakeEmbeddings:
    def __init__(self, dim: int = _DIM):
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for t in texts:
            v = [0.0] * self.dim
            for tok in _tokens(t):
                bucket = int(hashlib.md5(tok.encode(), usedforsecurity=False).hexdigest(), 16) % self.dim
                v[bucket] += 1.0
            norm = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / norm for x in v])
        return out


class FakeTranslation:
    def __init__(self, force_error: str | None = None):
        self.force_error = force_error

    def translate(self, text: str, src: str, tgt: str) -> str:
        if self.force_error in ("timeout", "rate_limit"):
            raise ProviderError(self.force_error, retryable=True)
        if src == tgt:
            return text
        # statute/section tokens are preserved verbatim (they remain inside `text`)
        return f"[{tgt}] {text}"
