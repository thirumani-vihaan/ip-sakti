"""T042 acceptance: the advertised demo/example questions retrieve the expected source."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))
    expect = {
        "Is a traditional-knowledge Ayurvedic formulation patentable under Section 3(p)?": "patents_1970_s3p",
        "Do I need State Biodiversity Board approval to sell a biological resource commercially?": "bda_2002_s7",
        "How do I protect a regional product name with a geographical indication?": "gi_act_1999",
        "What is a patent?": "patents_1970_s3p",
    }
    for q, doc in expect.items():
        body = client.post("/api/chat", json={"query": q}).json()
        assert body["claims"], f"expected an answer for: {q}"
        docs = {s["id"].split("#")[0] for s in body["sources"]}
        assert doc in docs, f"{q!r} -> expected {doc}, got {docs}"

    print("T042 OK: advertised example questions retrieve the expected primary source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
