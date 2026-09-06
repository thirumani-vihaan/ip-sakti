"""Fail-closed abstention responses."""
from __future__ import annotations

from datetime import date

from app.models.enums import AnswerMode, EvidenceStrength
from app.workflow.schema import ChatRequest, ChatResponse, Warning

_MESSAGES = {
    "out_of_corpus": "No supporting source found in the corpus; unable to answer.",
    "unsupported": "Could not produce a citation-supported answer; please consult a qualified professional.",
    "conflict": "Sources conflict on the current position; please verify with an official source.",
}


def abstention_response(
    reason: str,
    req: ChatRequest,
    as_of: date,
    corpus_version: str,
    extra_warnings: list[Warning] | None = None,
) -> ChatResponse:
    warns = list(extra_warnings or []) + [Warning(code=reason, message=_MESSAGES.get(reason, reason))]
    return ChatResponse(
        claims=[], sources=[], warnings=warns,
        answer_mode=AnswerMode.LIVE, evidence_strength=EvidenceStrength.LIMITED,
        jurisdiction=req.jurisdiction, language=req.language,
        as_of=as_of, corpus_version=corpus_version,
    )
