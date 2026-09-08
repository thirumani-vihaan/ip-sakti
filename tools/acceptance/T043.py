"""T043 acceptance: temporal eligibility handles not-yet-in-force + undated future safely."""
import pathlib
import sys
from datetime import date, timedelta

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.workflow.schema import RetrievalHit, Source
    from app.workflow.temporal import is_in_force_as_of

    today = date.today()

    def hit(status, ed):
        s = Source(id="x", title="t", section=None, local_excerpt="x", status=status,
                   authority="statute", as_of=today, document_hash="h", effective_date=ed)
        return RetrievalHit(evidence_id="x", text="x", score=1.0, source=s)

    # not-yet-in-force, undated -> excluded (never silently eligible)
    assert not is_in_force_as_of(hit("not_yet_in_force", None), today)
    # not-yet-in-force, future date -> excluded until it arrives
    assert not is_in_force_as_of(hit("not_yet_in_force", today + timedelta(days=10)), today)
    # not-yet-in-force whose effective date has passed -> now eligible
    assert is_in_force_as_of(hit("not_yet_in_force", today - timedelta(days=10)), today)
    # repealed -> excluded; in-force undated -> eligible
    assert not is_in_force_as_of(hit("repealed", None), today)
    assert is_in_force_as_of(hit("in_force", None), today)

    print("T043 OK: not-yet-in-force + undated-future temporal edges handled safely")
    return 0


if __name__ == "__main__":
    sys.exit(main())
