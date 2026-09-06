"""Term-preserving translation: statute names + section/form ids must survive verbatim.

If a translation drops a statute/section reference, that is a compliance-affecting
change -> raise, so the caller abstains rather than serve altered legal text.
"""
from __future__ import annotations

import re

from app.integrations.provider import TranslationProvider

_PRESERVE_RE = re.compile(r"(Section\s+\d+[A-Za-z]*(?:\([a-z0-9]+\))?|Form\s+[IVX]+)", re.I)


def preserve_tokens(text: str) -> list[str]:
    return _PRESERVE_RE.findall(text)


def translate_preserving(provider: TranslationProvider, text: str, src: str, tgt: str) -> str:
    tokens = preserve_tokens(text)
    out = provider.translate(text, src, tgt)
    for tok in tokens:
        if tok not in out:
            raise ValueError(f"translation altered a statute/section reference: {tok!r}")
    return out
