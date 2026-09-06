"""POST /api/compare — two validated answers side by side (no second generation)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.enums import Jurisdiction
from app.workflow.schema import ChatRequest, ChatResponse

router = APIRouter()


class CompareRequest(BaseModel):
    option_a: str
    option_b: str
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    language: str = "en"
    as_of: Optional[date] = None
    sensitive: bool = False


class CompareResponse(BaseModel):
    a: ChatResponse
    b: ChatResponse


@router.post("/api/compare", response_model=CompareResponse)
def compare(req: CompareRequest, request: Request) -> CompareResponse:
    svc = request.app.state.answer_service

    def _ans(q: str) -> ChatResponse:
        return svc.answer(ChatRequest(
            query=q, jurisdiction=req.jurisdiction, language=req.language,
            as_of=req.as_of, sensitive=req.sensitive,
        ))

    return CompareResponse(a=_ans(req.option_a), b=_ans(req.option_b))
