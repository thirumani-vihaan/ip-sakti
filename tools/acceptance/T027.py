"""T027 acceptance: GET /api/search returns grounded ranked hits; jurisdiction filter; validation."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    r = client.get("/api/search", params={"q": "traditional knowledge patent Section 3(p)", "k": 3})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["results"], "expected search hits"
    for hit in body["results"]:
        assert hit["evidence_id"] == hit["source"]["id"], "grounding invariant: evidence_id == source.id"
        assert isinstance(hit["score"], (int, float))

    # international jurisdiction returns only international instruments
    ri = client.get("/api/search", params={"q": "patent cooperation treaty", "jurisdiction": "international"})
    ids = {h["evidence_id"].split("#")[0] for h in ri.json()["results"]}
    assert ids and ids <= {"trips_art27", "pct_overview", "nagoya_cbd"}, f"unexpected intl ids: {ids}"

    # validation: missing q -> 422
    assert client.get("/api/search").status_code == 422

    print("T027 OK: /api/search grounded ranked hits; jurisdiction filter; validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
