"""Composite 'evidence strength' — a labelled indicator, never a fake probability."""
from __future__ import annotations

from app.models.enums import EvidenceStrength
from app.workflow.schema import Claim, Source

_AUTH_RANK = {"statute": 0, "rule": 1, "notification": 2, "guideline": 3, "treaty": 4, "article": 5}


def _norm(s: str | None) -> str:
    return (s or "").lower().replace(" ", "")


def score_strength(
    valid_claims: list[Claim], sources: list[Source], query_section_refs: set[str]
) -> EvidenceStrength:
    if not valid_claims or not sources:
        return EvidenceStrength.LIMITED
    exact = any(_norm(s.section) and _norm(s.section) in query_section_refs for s in sources)
    best_auth = min(_AUTH_RANK.get(s.authority, 9) for s in sources)
    agreement = len({s.id for s in sources})
    if best_auth == 0 and (exact or agreement >= 2):
        return EvidenceStrength.HIGH
    if best_auth == 0 or exact or agreement >= 1:
        return EvidenceStrength.MODERATE
    return EvidenceStrength.LIMITED
