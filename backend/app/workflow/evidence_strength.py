"""Composite 'evidence strength' — a labelled indicator, never a fake probability."""
from __future__ import annotations

from app.models.enums import EvidenceStrength
from app.workflow.refs import norm as _norm
from app.workflow.schema import Claim, Source

_AUTH_RANK = {"statute": 0, "rule": 1, "notification": 2, "guideline": 3, "treaty": 4, "article": 5}


def score_strength(
    valid_claims: list[Claim], sources: list[Source], query_section_refs: set[str]
) -> EvidenceStrength:
    if not valid_claims or not sources:
        return EvidenceStrength.LIMITED
    exact = any(_norm(s.section) and _norm(s.section) in query_section_refs for s in sources)
    best_auth = min(_AUTH_RANK.get(s.authority, 9) for s in sources)
    # HIGH only when a primary source (statute) is the exact section the user asked about —
    # distinct unrelated sources are NOT treated as corroboration.
    if best_auth == 0 and exact:
        return EvidenceStrength.HIGH
    # MODERATE: a primary/secondary authority (statute/rule/notification) or an exact-section hit.
    if best_auth <= 2 or exact:
        return EvidenceStrength.MODERATE
    # LIMITED: only lower-authority material (guideline/treaty/article) with no exact match.
    return EvidenceStrength.LIMITED
