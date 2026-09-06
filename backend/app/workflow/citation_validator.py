"""Citation validator — the grounding core.

Enforces, deterministically:
  1. every cited id must be a real server-assigned evidence id (unknown -> drop),
  2. any Section/Form reference asserted in a claim must appear in a cited source
     (mismatch -> drop),
  3. claims with no valid citation are dropped.
If nothing survives, the caller abstains. The model can never smuggle a source in.
"""
from __future__ import annotations

import re

from app.workflow.schema import Claim, RetrievalHit, Source, Warning

_SECTION_RE = re.compile(r"section\s+(\d+[a-z]*(?:\([a-z0-9]+\))?)", re.I)
_FORM_RE = re.compile(r"\bform\s+([ivx]+)\b", re.I)


def _norm(s: str) -> str:
    return s.lower().replace(" ", "")


def _refs_in(text: str) -> set[str]:
    out: set[str] = set()
    for m in _SECTION_RE.finditer(text):
        out.add("s:" + _norm(m.group(1)))
    for m in _FORM_RE.finditer(text):
        out.add("f:" + m.group(1).lower())
    return out


def validate_claims(
    claims: list[Claim], evidence: list[RetrievalHit]
) -> tuple[list[Claim], list[Source], list[Warning]]:
    by_id = {h.evidence_id: h for h in evidence}
    valid: list[Claim] = []
    warnings: list[Warning] = []

    for c in claims:
        unknown = [sid for sid in c.source_ids if sid not in by_id]
        known = [sid for sid in c.source_ids if sid in by_id]
        if unknown:
            warnings.append(Warning(code="unknown_citation",
                                    message=f"claim dropped: unknown evidence id(s) {unknown}"))
            continue
        if not known:
            warnings.append(Warning(code="uncited", message="claim dropped: no citation"))
            continue

        claim_refs = _refs_in(c.text)
        if claim_refs:
            supported: set[str] = set()
            for sid in known:
                h = by_id[sid]
                supported |= _refs_in(h.text)
                if h.source.section:
                    supported.add("s:" + _norm(h.source.section))
            missing = claim_refs - supported
            if missing:
                warnings.append(Warning(code="reference_mismatch",
                                        message=f"claim dropped: {sorted(missing)} not in cited source"))
                continue

        valid.append(Claim(text=c.text, source_ids=known))

    seen: list[str] = []
    sources: list[Source] = []
    for c in valid:
        for sid in c.source_ids:
            if sid not in seen:
                seen.append(sid)
                sources.append(by_id[sid].source)
    return valid, sources, warnings
