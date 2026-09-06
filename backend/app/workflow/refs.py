"""Shared legal-reference parsing (single source of truth).

Section/Form patterns and normalisation live here so citation validation,
reference resolution, and evidence scoring can never drift apart.
"""
from __future__ import annotations

import re

SECTION_RE = re.compile(r"section\s+(\d+[a-z]*(?:\([a-z0-9]+\))?)", re.I)
FORM_RE = re.compile(r"\bform\s+([ivx]+)\b", re.I)


def norm(s: str | None) -> str:
    return (s or "").lower().replace(" ", "")


def extract_section_refs(text: str) -> set[str]:
    """Normalised section identifiers mentioned in the text, e.g. {"3(p)"}."""
    return {norm(m.group(1)) for m in SECTION_RE.finditer(text)}


def refs_in(text: str) -> set[str]:
    """Namespaced Section/Form references in the text, e.g. {"s:3(p)", "f:i"}."""
    out: set[str] = set()
    for m in SECTION_RE.finditer(text):
        out.add("s:" + norm(m.group(1)))
    for m in FORM_RE.finditer(text):
        out.add("f:" + m.group(1).lower())
    return out
