"""POST /api/classify — deterministic formulation classification (or insufficient-info)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.rules.classification_rules import CLASSIFICATION
from app.rules.engine import evaluate
from app.workflow.schema import RuleResult

router = APIRouter()


class ClassifyRequest(BaseModel):
    in_first_schedule: Optional[str] = None
    modified: Optional[str] = None
    novel_actives: Optional[str] = None
    intended_use: Optional[str] = None


@router.post("/api/classify", response_model=RuleResult)
def classify(req: ClassifyRequest) -> RuleResult:
    return evaluate(CLASSIFICATION, req.model_dump(exclude_none=True))
