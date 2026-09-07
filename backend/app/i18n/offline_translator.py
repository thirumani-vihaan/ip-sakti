"""Offline, deterministic translation via the locked legal glossary.

No network and no API key: this is the credential-free fallback so the multilingual
feature works with nothing configured. It localises known legal/AYUSH terms (longest
phrases first) into the target language and leaves everything else — crucially,
statute/section references — untouched. When Bhashini credentials are provided,
`BhashiniTranslation` replaces this automatically with full neural translation.
"""
from __future__ import annotations

import re

from app.i18n.glossary import glossary_for


class OfflineGlossaryTranslation:
    def translate(self, text: str, src: str, tgt: str) -> str:
        if src == tgt:
            return text
        gloss = glossary_for(src, tgt)
        if not gloss:
            return text
        out = text
        # longest phrases first so multi-word terms win over their substrings
        for en in sorted(gloss, key=len, reverse=True):
            out = re.compile(re.escape(en), re.IGNORECASE).sub(gloss[en], out)
        return out
