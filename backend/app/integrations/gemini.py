"""Real Google Gemini providers. SDK is imported lazily so constructors are cheap and
offline-safe; only the actual generate()/embed() calls need the SDK + network + a key.
"""
from __future__ import annotations

import re

from app.workflow.schema import Claim, RetrievalHit


class GeminiLLM:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, evidence: list[RetrievalHit]) -> list[Claim]:
        import google.generativeai as genai  # lazy
        genai.configure(api_key=self.api_key)
        resp = genai.GenerativeModel(self.model).generate_content(prompt)
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
        import google.generativeai as genai  # lazy
        genai.configure(api_key=self.api_key)
        out: list[list[float]] = []
        for t in texts:
            r = genai.embed_content(model=self.model, content=t)
            out.append(list(r["embedding"]))
        return out
