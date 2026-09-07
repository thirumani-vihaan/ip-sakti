"""POST /api/roadmap — a prioritised, cited IP/ABS/regulatory roadmap built from validated answers."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.models.enums import Jurisdiction
from app.workflow.schema import ChatRequest, ChatResponse

router = APIRouter()

_FACETS = [
    ("Patentability & traditional-knowledge risk", "{q} patent traditional knowledge Section 3(p) not an invention"),
    ("Access & Benefit Sharing (ABS)", "{q} biological resource commercial prior intimation State Biodiversity Board Form I"),
    ("Brand / GI protection", "{q} geographical indication registration"),
]


class RoadmapRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1800)
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    language: str = "en"
    as_of: Optional[date] = None
    sensitive: bool = False


class RoadmapStep(BaseModel):
    title: str
    answer: ChatResponse


class RoadmapResponse(BaseModel):
    steps: list[RoadmapStep]


@router.post("/api/roadmap", response_model=RoadmapResponse)
def roadmap(req: RoadmapRequest, request: Request) -> RoadmapResponse:
    svc = request.app.state.answer_service
    steps = []
    for title, tmpl in _FACETS:
        sub = ChatRequest(
            query=tmpl.format(q=req.query)[:2000], jurisdiction=req.jurisdiction,
            language=req.language, as_of=req.as_of, sensitive=req.sensitive,
        )
        steps.append(RoadmapStep(title=title, answer=svc.answer(sub)))
    return RoadmapResponse(steps=steps)
