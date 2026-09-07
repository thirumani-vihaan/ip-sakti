"""Escalation to a human IP facilitator — a required safety path.

Surfaces an escalation option whenever the assistant cannot stand fully behind an
answer: an abstention (no citation-supported answer) or a low-confidence
(LIMITED evidence-strength) result. The actual hand-off is handled by
POST /api/escalate, which prepares a referral without storing personal data.
"""
from __future__ import annotations

from app.models.enums import EvidenceStrength
from app.workflow.schema import ChatResponse, Warning

_CODE = "escalate_available"
_MESSAGE = (
    "Low confidence or out-of-scope for this query — you can escalate to a human "
    "IP facilitator for authoritative guidance."
)


def escalation_warning() -> Warning:
    return Warning(code=_CODE, message=_MESSAGE)


def escalation_warranted(resp: ChatResponse) -> bool:
    return (not resp.claims) or resp.evidence_strength == EvidenceStrength.LIMITED
