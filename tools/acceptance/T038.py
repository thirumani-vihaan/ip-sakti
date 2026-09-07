"""T038 acceptance: /api/classify resolves all six categories THROUGH the API (incl. plant_derived)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    cases = {
        "Classical": {"in_first_schedule": "yes", "modified": "exact", "novel_actives": "no", "intended_use": "medicine"},
        "Proprietary": {"in_first_schedule": "yes", "modified": "modified", "novel_actives": "no", "intended_use": "medicine"},
        "Phytopharmaceutical": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "yes", "intended_use": "medicine", "plant_derived": "yes"},
        "New drug": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "yes", "intended_use": "medicine"},
        "Nutraceutical": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "no", "intended_use": "food"},
        "Cosmetic": {"in_first_schedule": "no", "modified": "modified", "novel_actives": "no", "intended_use": "cosmetic"},
    }
    for label, facts in cases.items():
        body = client.post("/api/classify", json=facts).json()
        assert body["status"] == "decided", (label, body)
        assert label.lower() in body["obligation"].lower(), (label, body["obligation"])

    print("T038 OK: all six formulation categories resolve through /api/classify (plant_derived wired)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
