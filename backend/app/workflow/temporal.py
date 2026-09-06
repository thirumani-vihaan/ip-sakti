"""Temporal current-law eligibility: a source is usable iff it is in force as of a date."""
from __future__ import annotations

from datetime import date

from app.models.enums import ForceState
from app.workflow.schema import RetrievalHit


def is_in_force_as_of(hit: RetrievalHit, as_of: date) -> bool:
    if hit.source.status != ForceState.IN_FORCE:
        return False
    ed = hit.source.effective_date
    return ed is None or ed <= as_of
