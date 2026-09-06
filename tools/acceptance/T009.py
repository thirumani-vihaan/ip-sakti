"""T009 acceptance (CORE): unknown ids rejected; section/form mismatch dropped; no-support -> abstain."""
import pathlib
import sys
from datetime import date

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def _hit(eid, title, section, text):
    from app.workflow.schema import RetrievalHit, Source
    src = Source(id=eid, title=title, section=section, local_excerpt=text,
                 status="in_force", authority="statute", as_of=date.today(), document_hash="h")
    return RetrievalHit(evidence_id=eid, text=text, score=1.0, source=src)


def main() -> int:
    from app.integrations.fakes import FakeLLM
    from app.workflow.citation_validator import validate_claims
    from app.workflow.schema import Claim

    e1 = _hit("e1", "Patents Act 1970", "3(p)", "Section 3(p): traditional knowledge is not an invention")
    e2 = _hit("e2", "Biological Diversity Act 2002", "7",
              "Section 7: prior intimation in Form I to the State Biodiversity Board")
    evidence = [e1, e2]

    good_sec = Claim(text="Under Section 3(p), TK is not patentable.", source_ids=["e1"])
    good_form = Claim(text="File Form I with the State Biodiversity Board.", source_ids=["e2"])
    unknown = Claim(text="Some claim.", source_ids=["e999"])
    wrong_sec = Claim(text="Section 5 bars this.", source_ids=["e1"])
    wrong_form = Claim(text="Submit Form II.", source_ids=["e2"])
    uncited = Claim(text="No citation here.", source_ids=[])

    valid, sources, warnings = validate_claims(
        [good_sec, good_form, unknown, wrong_sec, wrong_form, uncited], evidence
    )
    valid_texts = {c.text for c in valid}
    assert valid_texts == {good_sec.text, good_form.text}, f"unexpected valid set: {valid_texts}"
    codes = {w.code for w in warnings}
    assert codes == {"unknown_citation", "reference_mismatch", "uncited"}, f"codes={codes}"
    assert {s.id for s in sources} == {"e1", "e2"}
    # every surviving claim cites only real evidence ids
    ids = {h.evidence_id for h in evidence}
    assert all(set(c.source_ids) <= ids for c in valid)

    # no-support -> abstain (empty valid)
    v2, _, w2 = validate_claims([unknown, uncited], evidence)
    assert v2 == [] and w2, "all-bad input must abstain (no valid claims)"

    # hallucinating LLM output is fully rejected
    halluc = FakeLLM(hallucinate=True).generate("q", evidence)  # cites e999
    v3, _, _ = validate_claims(halluc, evidence)
    assert v3 == [], "fabricated citation must be rejected"

    print("T009 OK: unknown ids rejected; section/form mismatch dropped; fabrication rejected; abstains")
    return 0


if __name__ == "__main__":
    sys.exit(main())
