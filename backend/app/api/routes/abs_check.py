"""POST /api/abs/check — deterministic ABS obligation (or insufficient-info)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.rules.abs_rules import ABS
from app.rules.engine import evaluate
from app.workflow.schema import RuleResult

router = APIRouter()


class AbsCheckRequest(BaseModel):
    resource_origin: Optional[str] = None
    use: Optional[str] = None
    applicant: Optional[str] = None
    tk_association: Optional[str] = None


@router.post("/api/abs/check", response_model=RuleResult)
def abs_check(req: AbsCheckRequest) -> RuleResult:
    return evaluate(ABS, req.model_dump(exclude_none=True))
