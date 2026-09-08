"""T041 acceptance: PDF export enforces grounding (ungrounded/forged responses rejected)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))
    good = client.post("/api/chat", json={"query": "Under Section 3(p), can I patent a traditional formulation?"}).json()
    assert good["claims"], "precondition: grounded answer"

    # grounded answer exports fine
    assert client.post("/api/export/pdf", json=good).status_code == 200

    # forged: a high-confidence claim with NO citation must be rejected
    forged = {**good, "claims": [{"text": "Patents are automatically granted.", "source_ids": []}], "sources": []}
    assert client.post("/api/export/pdf", json=forged).status_code == 422

    # forged: a claim citing an id that is not in the response's sources must be rejected
    forged2 = {**good, "claims": [{"text": "x", "source_ids": ["not_a_real_source"]}]}
    assert client.post("/api/export/pdf", json=forged2).status_code == 422

    print("T041 OK: PDF export refuses ungrounded/forged claims; grounded answers export")
    return 0


if __name__ == "__main__":
    sys.exit(main())
