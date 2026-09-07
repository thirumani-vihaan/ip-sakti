"""Injectable provider interfaces. Workflow code depends ONLY on these, never on an SDK."""
from __future__ import annotations

import time
from typing import Protocol, runtime_checkable

from app.workflow.schema import Claim, RetrievalHit


class ProviderError(Exception):
    """Raised by providers. `retryable` distinguishes transient (timeout/429) from terminal."""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class CircuitBreaker:
    """Opens after `threshold` consecutive failures; after `cooldown_seconds` it goes
    half-open (allows one trial call). A success closes it; a failure re-opens it. This
    lets the service recover automatically once the provider comes back."""

    def __init__(self, threshold: int = 3, cooldown_seconds: float = 30.0):
        self.threshold = threshold
        self.cooldown = cooldown_seconds
        self.failures = 0
        self.opened_at: float | None = None

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = time.monotonic()

    @property
    def open(self) -> bool:
        if self.opened_at is None:
            return False
        # after the cooldown, report closed so the caller makes one trial attempt (half-open)
        return (time.monotonic() - self.opened_at) < self.cooldown

    @property
    def healthy(self) -> bool:
        return not self.open


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
