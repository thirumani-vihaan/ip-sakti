"""POST /api/compare — two validated answers side by side (no second generation)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.models.enums import Jurisdiction
from app.workflow.schema import ChatRequest, ChatResponse

router = APIRouter()


class CompareRequest(BaseModel):
    option_a: str = Field(min_length=1, max_length=2000)
    option_b: str = Field(min_length=1, max_length=2000)
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    jurisdiction_a: Optional[Jurisdiction] = None
    jurisdiction_b: Optional[Jurisdiction] = None
    language: str = "en"
    as_of: Optional[date] = None
    sensitive: bool = False


class CompareResponse(BaseModel):
    a: ChatResponse
    b: ChatResponse


@router.post("/api/compare", response_model=CompareResponse)
def compare(req: CompareRequest, request: Request) -> CompareResponse:
    svc = request.app.state.answer_service
    jur_a = req.jurisdiction_a or req.jurisdiction
    jur_b = req.jurisdiction_b or req.jurisdiction

    def _ans(q: str, jur: Jurisdiction) -> ChatResponse:
        return svc.answer(ChatRequest(
            query=q, jurisdiction=jur, language=req.language,
            as_of=req.as_of, sensitive=req.sensitive,
        ))

    return CompareResponse(a=_ans(req.option_a, jur_a), b=_ans(req.option_b, jur_b))
