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
    agreement = len({s.id for s in sources})
    # HIGH: a primary source (statute) that is either the exact section asked, or corroborated.
    if best_auth == 0 and (exact or agreement >= 2):
        return EvidenceStrength.HIGH
    # MODERATE: primary/secondary authority (statute/rule/notification), an exact-section hit,
    # or multiple corroborating sources.
    if best_auth <= 2 or exact or agreement >= 2:
        return EvidenceStrength.MODERATE
    # LIMITED: a single low-authority source (guideline/treaty/article/unknown) with no exact match.
    return EvidenceStrength.LIMITED
