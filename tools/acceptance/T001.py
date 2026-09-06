"""T001 acceptance: contracts import, instantiate, round-trip serialize; grounding invariant holds."""
import pathlib
import sys
from datetime import date

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.models import enums
    from app.workflow import schema

    # enum members are exactly as specified
    assert enums.Jurisdiction.INDIA.value == "india"
    assert enums.ForceState.REPEALED.value == "repealed"
    assert {m.value for m in enums.Domain} == {
        "patent", "gi_trademark", "abs", "regulatory", "tk_risk", "international",
    }
    assert {m.value for m in enums.AnswerMode} == {"live", "extractive", "cached"}
    assert {m.value for m in enums.FormulationType} == {
        "classical", "proprietary", "new_drug",
        "phytopharmaceutical", "nutraceutical", "cosmetic",
    }

    src = schema.Source(
        id="e1", title="Patents Act 1970", section="3(p)",
        local_excerpt="...traditional knowledge...", status=enums.ForceState.IN_FORCE,
        authority="statute", as_of=date.today(), document_hash="sha256:abc",
    )
    hit = schema.RetrievalHit(evidence_id="e1", text="s3(p)", score=0.9, source=src)
    assert hit.source.id == hit.evidence_id, "grounding invariant: Source.id must equal evidence_id"

    claim = schema.Claim(text="TK-based inventions are barred under s.3(p).", source_ids=["e1"])
    rule = schema.RuleResult(status="insufficient", missing=["applicant"])
    warn = schema.Warning(code="scope", message="central-law guidance only")
    req = schema.ChatRequest(query="Can I patent a turmeric formulation?")
    resp = schema.ChatResponse(
        claims=[claim], sources=[src], warnings=[warn],
        answer_mode=enums.AnswerMode.LIVE, evidence_strength=enums.EvidenceStrength.HIGH,
        jurisdiction=enums.Jurisdiction.INDIA, language="en",
        as_of=date.today(), corpus_version="v0",
    )

    # round-trip serialize every contract type
    for obj in (src, hit, claim, rule, warn, req, resp):
        restored = type(obj).model_validate_json(obj.model_dump_json())
        assert restored == obj, f"round-trip failed for {type(obj).__name__}"

    print("T001 OK: contracts import + instantiate + round-trip; grounding invariant holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
