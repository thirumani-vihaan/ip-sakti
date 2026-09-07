"""Temporal current-law eligibility: a source is usable iff it is in force as of a date."""
from __future__ import annotations

from datetime import date

from app.models.enums import ForceState
from app.workflow.schema import RetrievalHit


def is_in_force_as_of(hit: RetrievalHit, as_of: date) -> bool:
    # A repealed source is excluded (conservative: we do not carry a repeal date).
    if hit.source.status == ForceState.REPEALED:
        return False
    # Otherwise eligibility is governed by the effective date: a not-yet-in-force source
    # becomes usable once its effective date has passed, and a future-dated one is excluded.
    ed = hit.source.effective_date
    return ed is None or ed <= as_of
