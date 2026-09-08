"""POST /api/export/pdf — render a PDF from a server-authenticated answer.

The endpoint does NOT trust a client-submitted ChatResponse as authoritative. It:
  1. authenticates every source against the canonical corpus (id + all immutable fields),
  2. requires every claim to cite one of those authenticated sources,
  3. renders only server-authoritative report metadata: warning messages are replaced by
     canonical text keyed on a known code (unknown codes dropped), corpus_version is the
     server value, and evidence strength is clamped to LIMITED when there are no claims.
Claim wording remains the (grounded) synthesized text; full semantic entailment is roadmap.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from app.models.enums import EvidenceStrength
from app.utils.pdf_generator import render_pdf
from app.workflow.schema import ChatResponse, Warning

router = APIRouter()

_IMMUTABLE = ("title", "section", "url", "local_excerpt", "status", "authority",
              "effective_date", "document_hash")

# canonical, server-owned warning text so a forged report cannot show arbitrary "Notes"
_WARNING_MESSAGES = {
    "out_of_corpus": "No supporting source was found in the corpus.",
    "unsupported": "Could not produce a citation-supported answer.",
    "conflict": "Sources conflict on the current position; verify with an official source.",
    "escalate_available": "Low confidence or out-of-scope; a human IP facilitator can help.",
    "degraded": "LLM unavailable; showing source passages without synthesis.",
    "sensitive_local": "Sensitive-Invention mode: processed locally.",
    "domain_not_evaluated": "One or more domains were not evaluated (scope/latency budget).",
    "abs_mandatory": "ABS obligations may apply to commercial use of a biological resource.",
    "translation_skipped": "Some text kept in English to preserve legal references.",
    "translation_skipped_sensitive": "Sensitive mode: kept English to avoid external translation.",
    "offline_translation": "Offline mode: legal terms localised via glossary.",
    "unknown_citation": "A claim was dropped for citing an unknown source.",
    "uncited": "A claim was dropped for lacking a citation.",
    "reference_mismatch": "A claim was dropped for a section/form mismatch.",
}


def _safe_response(resp: ChatResponse, corpus_version: str) -> ChatResponse:
    warnings = [Warning(code=w.code, message=_WARNING_MESSAGES[w.code])
                for w in resp.warnings if w.code in _WARNING_MESSAGES]
    strength = resp.evidence_strength if resp.claims else EvidenceStrength.LIMITED
    return resp.model_copy(update={
        "corpus_version": corpus_version,
        "warnings": warnings,
        "evidence_strength": strength,
    })


@router.post("/api/export/pdf")
def export_pdf(resp: ChatResponse, request: Request) -> Response:
    canonical: dict = request.app.state.evidence_sources
    for s in resp.sources:
        c = canonical.get(s.id)
        if c is None:
            raise HTTPException(status_code=422, detail=f"unrecognised source: {s.id}")
        for field in _IMMUTABLE:
            if getattr(s, field) != getattr(c, field):
                raise HTTPException(status_code=422, detail=f"tampered source field '{field}' for {s.id}")
    source_ids = {s.id for s in resp.sources}
    for claim in resp.claims:
        if not claim.source_ids or not set(claim.source_ids) <= source_ids:
            raise HTTPException(status_code=422, detail="ungrounded claim cannot be exported")
    safe = _safe_response(resp, request.app.state.settings.corpus_version)
    return Response(content=render_pdf(safe), media_type="application/pdf")
