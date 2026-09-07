"""POST /api/chat — grounded, validated answer."""
from __future__ import annotations

from fastapi import APIRouter, Request

from app.workflow.query_understanding import detect_language
from app.workflow.schema import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request) -> ChatResponse:
    if req.language == "auto":
        req = req.model_copy(update={"language": detect_language(req.query)})
    return request.app.state.answer_service.answer(req)
