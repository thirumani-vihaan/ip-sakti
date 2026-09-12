"""Citation validator — the grounding core.

Enforces, deterministically:
  1. every cited id must be a real server-assigned evidence id (unknown -> drop),
  2. any Section/Form reference asserted in a claim must appear in a cited source
     (mismatch -> drop),
  3. claims with no valid citation are dropped.
If nothing survives, the caller abstains. The model can never smuggle a source in.
"""
from __future__ import annotations

from app.workflow.refs import norm as _norm
from app.workflow.refs import refs_in as _refs_in
from app.workflow.schema import Claim, RetrievalHit, Source, Warning


def validate_claims(
    claims: list[Claim], evidence: list[RetrievalHit], allow_external: bool = False
) -> tuple[list[Claim], list[Source], list[Warning]]:
    """Validate claims against server-assigned evidence.

    Strict by default: a Section/Form reference not present in a cited source drops
    the claim (the grounding guarantee). When ``allow_external`` is True (demo
    enrichment mode), such a claim is kept but flagged with an ``external_context``
    warning so the UI can label it transparently rather than passing it off as
    strictly grounded.
    """
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
                if allow_external:
                    warnings.append(Warning(
                        code="external_context",
                        message=f"claim retained with external context: {sorted(missing)} "
                                "not found verbatim in the cited source"))
                else:
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
