"""Injectable provider interfaces. Workflow code depends ONLY on these, never on an SDK."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.workflow.schema import Claim, RetrievalHit


class ProviderError(Exception):
    """Raised by providers. `retryable` distinguishes transient (timeout/429) from terminal."""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, prompt: str, evidence: list[RetrievalHit]) -> list[Claim]:
        """Return atomic claims citing ONLY evidence_ids from `evidence`. Never invents ids."""
        ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


@runtime_checkable
class TranslationProvider(Protocol):
    def translate(self, text: str, src: str, tgt: str) -> str:
        """Translate `text` src->tgt, preserving statute names / section numbers verbatim."""
        ...
