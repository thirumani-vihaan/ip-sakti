"""Real Google Gemini providers (instance-scoped `google-genai` client).

The client is created lazily on first use and cached on the instance, so there is
NO global module state to race under FastAPI's threadpool. Constructors stay cheap
and offline-safe; only the first real generate()/embed() call needs the SDK + network.
"""
from __future__ import annotations

import math
import re

from app.integrations.provider import ProviderError
from app.workflow.schema import Claim, RetrievalHit

# split a paragraph into sentences on end punctuation followed by whitespace
_SENT_RE = re.compile(r"(?<=[.!?])\s+")
_CITE_RE = re.compile(r"\[([^\]]+)\]")


class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-flash-latest"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai  # lazy
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str, evidence: list[RetrievalHit]) -> list[Claim]:
        try:
            client = self._get_client()
            resp = client.models.generate_content(model=self.model, contents=prompt)
        except Exception as e:  # translate SDK/network errors so the pipeline can degrade
            raise ProviderError(f"gemini generate failed: {e}", retryable=True) from e
        text = (getattr(resp, "text", "") or "").strip()
        if not text:
            return []
        allowed = {h.evidence_id for h in evidence}
        return _to_claims(text, allowed)


class GeminiEmbeddings:
    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai  # lazy
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            client = self._get_client()
            resp = client.models.embed_content(model=self.model, contents=texts)  # batched
            return [_l2_normalise(list(e.values)) for e in resp.embeddings]
        except Exception as e:
            raise ProviderError(f"gemini embed failed: {e}", retryable=True) from e


def _l2_normalise(v: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]  # so dot == cosine downstream


def _to_claims(text: str, allowed: set[str]) -> list[Claim]:
    """Break the response into atomic sentence-level claims, each carrying only the
    server-assigned citation ids found within it. Falls back to a single pooled claim
    if the model did not cite per-sentence, so we never lose content."""
    claims: list[Claim] = []
    for sentence in _SENT_RE.split(text):
        s = sentence.strip()
        if not s:
            continue
        cited = [m for m in _CITE_RE.findall(s) if m in allowed]
        if cited:
            claims.append(Claim(text=s, source_ids=cited))
    if claims:
        return claims
    # no per-sentence citations: keep the whole answer as one claim with pooled ids
    pooled = [m for m in _CITE_RE.findall(text) if m in allowed]
    return [Claim(text=text, source_ids=pooled)]

