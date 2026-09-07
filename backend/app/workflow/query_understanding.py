"""Lightweight, offline query understanding.

Deterministic script-based language detection plus reference/domain hints. No model
or network required. Used to support `language: "auto"` (detect Hindi/Telugu input)
and to expose the section/domain signals the pipeline already derives.
"""
from __future__ import annotations

import re

from app.workflow.domain_router import classify
from app.workflow.refs import extract_section_refs

_DEVANAGARI = re.compile(r"[\u0900-\u097F]")  # Hindi
_TELUGU = re.compile(r"[\u0C00-\u0C7F]")


def detect_language(text: str) -> str:
    if _TELUGU.search(text):
        return "te"
    if _DEVANAGARI.search(text):
        return "hi"
    return "en"


def understand(query: str) -> dict:
    return {
        "language": detect_language(query),
        "section_refs": sorted(extract_section_refs(query)),
        "domains": sorted(d.value for d in classify(query)),
    }
