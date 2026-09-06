"""T014 acceptance: deterministic obligations (x100), each cites a source; missing fact -> insufficient."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.rules.abs_rules import ABS
    from app.rules.classification_rules import CLASSIFICATION
    from app.rules.engine import evaluate

    facts = {"resource_origin": "india", "use": "commercial", "applicant": "indian_entity", "tk_association": "no"}
    runs = [evaluate(ABS, facts) for _ in range(100)]
    first = runs[0]
    assert first.status == "decided", first
    assert all(r == first for r in runs), "engine must be deterministic across 100 runs"
    assert "State Biodiversity Board" in first.obligation and first.forms == ["Form I"]
    assert first.source_id and first.rule_version, "obligation must cite source + rule_version"

    foreign = evaluate(ABS, {**facts, "applicant": "foreign"})
    assert "National Biodiversity Authority" in foreign.obligation and foreign.source_id

    missing = evaluate(ABS, {"resource_origin": "india", "use": "commercial"})
    assert missing.status == "insufficient" and set(missing.missing) == {"applicant", "tk_association"}, missing

    food = evaluate(CLASSIFICATION, {"in_first_schedule": "no", "modified": "modified",
                                     "novel_actives": "no", "intended_use": "food"})
    assert food.status == "decided" and food.source_id and "utraceutical" in food.obligation

    ask = evaluate(CLASSIFICATION, {"in_first_schedule": "no", "modified": "modified", "novel_actives": "no"})
    assert ask.status == "insufficient" and "intended_use" in ask.missing

    print("T014 OK: deterministic obligations cite source+version; missing facts -> insufficient")
    return 0


if __name__ == "__main__":
    sys.exit(main())
