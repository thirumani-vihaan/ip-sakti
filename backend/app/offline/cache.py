"""Approved demo-scenario cache — an OUTAGE fallback only, always labelled answer_mode=cached."""
from __future__ import annotations

import re
from typing import Optional

from app.workflow.schema import ChatResponse


def _norm(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())


class DemoCache:
    def __init__(self, entries: Optional[dict[str, ChatResponse]] = None):
        self._d: dict[str, ChatResponse] = {}
        for k, v in (entries or {}).items():
            self.put(k, v)

    def put(self, query: str, response: ChatResponse) -> ChatResponse:
        labelled = response.model_copy(update={"answer_mode": "cached"})
        self._d[_norm(query)] = labelled
        return labelled

    def get(self, query: str) -> Optional[ChatResponse]:
        return self._d.get(_norm(query))
