"""T030 acceptance: GET /api/sources returns the corpus provenance registry."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))
    r = client.get("/api/sources")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["count"] == len(body["sources"]) >= 13, body["count"]

    by_id = {s["id"]: s for s in body["sources"]}
    assert "patents_1970_s3p" in by_id and by_id["patents_1970_s3p"]["status"] == "in_force"
    # every entry carries provenance fields
    for s in body["sources"]:
        assert s["title"] and s["url"] and s["version"] and s["authority_level"] and s["jurisdiction"]
    # international instruments are present and tagged
    assert by_id["trips_art27"]["jurisdiction"] == "international"

    print("T030 OK: /api/sources provenance registry with versions + status")
    return 0


if __name__ == "__main__":
    sys.exit(main())
