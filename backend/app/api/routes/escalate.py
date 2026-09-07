"""POST /api/escalate — prepare a hand-off to a human IP facilitator.

Privacy-first: no account, and any optional contact string is echoed back for the
user's own reference only, never persisted. Returns a reference id, the facilitating
authority, and concrete next steps.
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.utils.security import sanitize_text

router = APIRouter()


class EscalateRequest(BaseModel):
    query: str
    reason: Optional[str] = None
    contact: Optional[str] = None


class EscalateResponse(BaseModel):
    reference_id: str
    facilitator: str
    message: str
    next_steps: list[str]
    contact_echo: Optional[str] = None


@router.post("/api/escalate", response_model=EscalateResponse)
def escalate(req: EscalateRequest) -> EscalateResponse:
    ref = "IPSAKTI-" + uuid.uuid4().hex[:8].upper()
    return EscalateResponse(
        reference_id=ref,
        facilitator="AYUSH IP Facilitation Cell",
        message=(
            "Your question has been prepared for review by a human IP facilitator. "
            "Quote the reference id when you follow up. This tool provides information, "
            "not legal advice."
        ),
        next_steps=[
            "Contact the AYUSH IP Facilitation Cell / a registered patent agent for a formal opinion.",
            "For patents: Office of the Controller General of Patents, Designs and Trade Marks (CGPDTM).",
            "For ABS / biological resources: the National Biodiversity Authority (NBA) or your State Biodiversity Board.",
            "Keep the cited sources shown in the answer for your facilitator to verify.",
        ],
        contact_echo=sanitize_text(req.contact) if req.contact else None,
    )
