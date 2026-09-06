"""POST /api/export/pdf — render a PDF from an already-validated ChatResponse."""
from __future__ import annotations

from fastapi import APIRouter, Response

from app.utils.pdf_generator import render_pdf
from app.workflow.schema import ChatResponse

router = APIRouter()


@router.post("/api/export/pdf")
def export_pdf(resp: ChatResponse) -> Response:
    return Response(content=render_pdf(resp), media_type="application/pdf")
