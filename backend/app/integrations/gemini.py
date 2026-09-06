"""Real Google Gemini providers. SDK is imported lazily so constructors are cheap and
offline-safe; only the actual generate()/embed() calls need the SDK + network + a key.
"""
from __future__ import annotations

import math
import re

from app.integrations.provider import ProviderError
from app.workflow.schema import Claim, RetrievalHit


class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, evidence: list[RetrievalHit]) -> list[Claim]:
        try:
            import google.generativeai as genai  # lazy
            genai.configure(api_key=self.api_key)
            resp = genai.GenerativeModel(self.model).generate_content(prompt)
        except Exception as e:  # translate SDK/network errors so the pipeline can degrade
            raise ProviderError(f"gemini generate failed: {e}", retryable=True) from e
        text = (getattr(resp, "text", "") or "").strip()
        if not text:
            return []
        allowed = {h.evidence_id for h in evidence}
        cited = [m for m in re.findall(r"\[([^\]]+)\]", text) if m in allowed]
        return [Claim(text=text, source_ids=cited)]


class GeminiEmbeddings:
    def __init__(self, api_key: str, model: str = "text-embedding-004"):
        self.api_key = api_key
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            import google.generativeai as genai  # lazy
            genai.configure(api_key=self.api_key)
            out: list[list[float]] = []
            for t in texts:
                r = genai.embed_content(model=self.model, content=t)
                v = list(r["embedding"])
                norm = math.sqrt(sum(x * x for x in v)) or 1.0
                out.append([x / norm for x in v])  # L2-normalise so dot == cosine downstream
            return out
        except Exception as e:
            raise ProviderError(f"gemini embed failed: {e}", retryable=True) from e
