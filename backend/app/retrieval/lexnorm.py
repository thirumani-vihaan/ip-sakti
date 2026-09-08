"""Shared lexical tokenisation with a small legal-alias map.

BM25, the relevance gate, and the fixture LLM all tokenise through this, so they agree
on token identity for the common legal variants (patent/patents/patentable, trade
mark/marks, geographical/indication -> gi, drug/medicine, ...). This lifts offline
retrieval quality on a small corpus without a heavy stemmer.
"""
from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_ALIASES = {
    "patents": "patent", "patentable": "patent", "patented": "patent", "patenting": "patent",
    "trademarks": "trademark", "marks": "trademark", "mark": "trademark",
    "designs": "design",
    "cosmetics": "cosmetic",
    "formulations": "formulation", "formulate": "formulation",
    "drugs": "drug", "medicine": "drug", "medicines": "drug", "medicinal": "drug",
    "copyrights": "copyright",
    "inventions": "invention", "inventive": "invention",
    "geographical": "gi", "indication": "gi", "indications": "gi",
    "biodiversity": "biological", "biological": "biological",
}


def norm_token(t: str) -> str:
    return _ALIASES.get(t, t)


def norm_tokens(text: str) -> list[str]:
    return [norm_token(t) for t in _TOKEN_RE.findall(text.lower())]
