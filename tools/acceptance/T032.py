"""T032 acceptance: escalation-to-human-facilitator path (required safety feature)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    # an out-of-corpus abstention must offer escalation
    r = client.post("/api/chat", json={"query": "monsoon heatwave weather forecast cricket score tonight"})
    codes = {w["code"] for w in r.json()["warnings"]}
    assert "out_of_corpus" in codes and "escalate_available" in codes, codes

    # the escalate endpoint prepares a facilitator hand-off
    e = client.post("/api/escalate", json={"query": "Can I patent X?", "contact": "me@example.com"})
    assert e.status_code == 200, e.text
    body = e.json()
    assert body["reference_id"].startswith("IPSAKTI-")
    assert body["facilitator"] and len(body["next_steps"]) >= 2
    assert body["contact_echo"] == "me@example.com"

    print("T032 OK: abstention offers escalation; /api/escalate prepares facilitator hand-off")
    return 0


if __name__ == "__main__":
    sys.exit(main())
