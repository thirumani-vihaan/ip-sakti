"""Exact legal-reference resolution from a query (Section/Form ids)."""
from __future__ import annotations

import re

_SECTION_RE = re.compile(r"section\s+(\d+[a-z]*(?:\([a-z0-9]+\))?)", re.I)


def _norm(ref: str) -> str:
    return ref.lower().replace(" ", "")


def extract_section_refs(query: str) -> set[str]:
    """Return normalised section identifiers mentioned in the query, e.g. {"3(p)"}."""
    return {_norm(m.group(1)) for m in _SECTION_RE.finditer(query)}
