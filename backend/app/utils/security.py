"""Input sanitization + a light prompt-injection heuristic.

Grounding already neutralises most injection (the model can only cite retrieved
evidence ids, never invent sources), but we still scrub control characters and
normalise whitespace on the query boundary, and expose a heuristic flag.
"""
from __future__ import annotations

import re

_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WS = re.compile(r"\s+")
_INJECTION = re.compile(
    r"(?i)\b(ignore\s+(all|the|previous|prior)\s+(instructions|prompts)"
    r"|disregard\s+(all|the|previous|prior)"
    r"|system\s+prompt"
    r"|you\s+are\s+now"
    r"|reveal\s+your\s+(instructions|prompt))\b"
)


def sanitize_text(text: str) -> str:
    return _WS.sub(" ", _CTRL.sub("", text)).strip()


def looks_like_injection(text: str) -> bool:
    return bool(_INJECTION.search(text))
