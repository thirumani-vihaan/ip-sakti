"""T016 acceptance: /api/abs/check and /api/classify return sourced results + insufficient-info path."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    r = client.post("/api/abs/check", json={
        "resource_origin": "india", "use": "commercial",
        "applicant": "indian_entity", "tk_association": "no",
    })
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["status"] == "decided" and b["source_id"] and b["forms"] == ["Form I"]
    assert "State Biodiversity Board" in b["obligation"]

    b2 = client.post("/api/abs/check", json={"resource_origin": "india", "use": "commercial"}).json()
    assert b2["status"] == "insufficient" and set(b2["missing"]) == {"applicant", "tk_association"}

    b3 = client.post("/api/classify", json={
        "in_first_schedule": "no", "modified": "modified", "novel_actives": "no", "intended_use": "food",
    }).json()
    assert b3["status"] == "decided" and b3["source_id"] and "utraceutical" in b3["obligation"]

    b4 = client.post("/api/classify", json={
        "in_first_schedule": "no", "modified": "modified", "novel_actives": "no",
    }).json()
    assert b4["status"] == "insufficient" and "intended_use" in b4["missing"]

    print("T016 OK: /api/abs/check + /api/classify sourced results + insufficient-info path")
    return 0


if __name__ == "__main__":
    sys.exit(main())
