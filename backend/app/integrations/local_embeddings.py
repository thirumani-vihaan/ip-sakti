"""Optional offline semantic embeddings via sentence-transformers.

A credential-free middle tier between Gemini (needs an API key) and the
deterministic FakeEmbeddings test double: when sentence-transformers is installed
and enabled, this gives real semantic retrieval with no network at query time
(the model is cached locally). If the package is absent, callers fall back to
FakeEmbeddings, so the system still runs. Vectors are L2-normalised so dot == cosine.
"""
from __future__ import annotations

import importlib.util

from app.integrations.provider import ProviderError


def sentence_transformers_available() -> bool:
    return importlib.util.find_spec("sentence_transformers") is not None


class LocalEmbeddings:
    def __init__(self, model: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model
        self._model = None

    def _get(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # lazy, heavy
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vecs = self._get().encode(list(texts), normalize_embeddings=True)
            return [[float(x) for x in v] for v in vecs]
        except Exception as e:
            raise ProviderError(f"local embeddings failed: {e}", retryable=False) from e
