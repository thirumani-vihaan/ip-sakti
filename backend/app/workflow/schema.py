"""Immutable domain contract for IP-SAKTI (pydantic v2).

Invariant: Source.id == the server-assigned evidence_id from RetrievalHit.
The model only ever sees/cites these ids; it can never invent new ones.
Do not change this file without a flagged, high-visibility candidate.
"""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models.enums import (
    AnswerMode,
    EvidenceStrength,
    ForceState,
    Jurisdiction,
)


class Source(BaseModel):
    id: str  # == RetrievalHit.evidence_id
    title: str
    section: Optional[str] = None
    page: Optional[int] = None
    url: Optional[str] = None
    local_excerpt: str
    status: ForceState
    authority: str
    effective_date: Optional[date] = None
    as_of: date
    document_hash: str


class Claim(BaseModel):
    text: str
    source_ids: list[str] = Field(default_factory=list)


class RetrievalHit(BaseModel):
    evidence_id: str
    text: str
    score: float
    source: Source


class RuleResult(BaseModel):
    obligation: Optional[str] = None
    authority: Optional[str] = None
    forms: list[str] = Field(default_factory=list)
    source_id: Optional[str] = None
    rule_version: Optional[str] = None
    status: Literal["decided", "insufficient"] = "insufficient"
    missing: list[str] = Field(default_factory=list)


class NextStep(BaseModel):
    label: str
    description: str
    url: str

class Warning(BaseModel):
    code: str
    message: str


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    language: str = "en"
    as_of: Optional[date] = None
    sensitive: bool = False


class ChatResponse(BaseModel):
    claims: list[Claim] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    warnings: list[Warning] = Field(default_factory=list)
    next_steps: list[NextStep] = Field(default_factory=list)
    answer_mode: AnswerMode = AnswerMode.LIVE
    evidence_strength: EvidenceStrength = EvidenceStrength.LIMITED
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    language: str = "en"
    as_of: date
    corpus_version: str
