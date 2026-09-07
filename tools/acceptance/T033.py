"""T033 acceptance: the classifier resolves all six formulation categories; extra fact is optional."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.rules.classification_rules import CLASSIFICATION
    from app.rules.engine import evaluate

    cases = {
        "classical": {"in_first_schedule": "yes", "modified": "exact", "novel_actives": "no", "intended_use": "medicine"},
        "proprietary": {"in_first_schedule": "yes", "modified": "modified", "novel_actives": "no", "intended_use": "medicine"},
        "phytopharmaceutical": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "yes", "intended_use": "medicine", "plant_derived": "yes"},
        "new_drug": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "yes", "intended_use": "medicine"},
        "nutraceutical": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "no", "intended_use": "food"},
        "cosmetic": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "no", "intended_use": "cosmetic"},
    }
    expect = {
        "classical": "Classical",
        "proprietary": "Proprietary",
        "phytopharmaceutical": "Phytopharmaceutical",
        "new_drug": "New drug",
        "nutraceutical": "Nutraceutical",
        "cosmetic": "Cosmetic",
    }
    for name, facts in cases.items():
        r = evaluate(CLASSIFICATION, facts)
        assert r.status == "decided", (name, r)
        assert expect[name].lower() in r.obligation.lower(), (name, r.obligation)
        assert r.source_id and r.rule_version, (name, r)

    # phytopharmaceutical vs new_drug is distinguished ONLY by the optional plant_derived fact;
    # without it the same facts fall through to new_drug (minimal questions, no forced 5th input)
    without = evaluate(CLASSIFICATION, cases["new_drug"])
    assert "New drug" in without.obligation and "plant_derived" not in CLASSIFICATION.required

    print("T033 OK: all six formulation categories resolve; extra distinguishing fact stays optional")
    return 0


if __name__ == "__main__":
    sys.exit(main())
