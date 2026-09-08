"""Temporal current-law eligibility: a source is usable iff it is in force as of a date."""
from __future__ import annotations

from datetime import date

from app.models.enums import ForceState
from app.workflow.schema import RetrievalHit


def is_in_force_as_of(hit: RetrievalHit, as_of: date) -> bool:
    status = hit.source.status
    # A repealed source is excluded (conservative: we do not carry a repeal date).
    if status == ForceState.REPEALED:
        return False
    ed = hit.source.effective_date
    # A not-yet-in-force source needs a known effective date and only becomes usable
    # once that date has passed; an undated future provision stays excluded.
    if status == ForceState.NOT_YET_IN_FORCE:
        return ed is not None and ed <= as_of
    # In-force material is governed by its effective date when present.
    return ed is None or ed <= as_of
