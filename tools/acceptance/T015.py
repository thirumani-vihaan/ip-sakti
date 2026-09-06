"""T015 acceptance: multi-label routing; ABS mandatory trigger; unevaluated domains disclosed."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.models.enums import Domain
    from app.workflow.domain_router import abs_triggered, classify, route

    # cross-domain query -> >= 2 domains, and the ABS trigger fires
    q = "Can I patent a herbal invention and sell the biological resource commercially?"
    labels = classify(q)
    assert Domain.PATENT in labels and Domain.ABS in labels, labels
    assert len(labels) >= 2
    assert abs_triggered(q), "biological resource + commercial must trigger ABS"

    sel, warns = route(q, budget=2)
    assert Domain.ABS in sel and Domain.PATENT in sel

    # 3+ domains with budget 2 -> at least one unevaluated domain disclosed; ABS still kept
    big = ("patent a herbal invention, register a geographical indication, "
           "sell the biological resource commercially, and export internationally under PCT")
    assert len(classify(big)) >= 3
    sel2, warns2 = route(big, budget=2)
    assert warns2 and all(w.code == "domain_not_evaluated" for w in warns2), "extra domains must be disclosed"
    assert Domain.ABS in sel2, "mandatory ABS must always be kept"

    # non-triggering wording does not force ABS
    assert not abs_triggered("what is the novelty requirement for a patent")

    print("T015 OK: multi-label routing; ABS trigger; unevaluated domains disclosed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
