"""T044 acceptance: sensitive non-English runs the LOCAL glossary (never external), with disclosure."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))
    r = client.post("/api/chat", json={
        "query": "Under Section 3(p), can I patent a traditional formulation?",
        "language": "hi", "sensitive": True,
    }).json()
    codes = {w["code"] for w in r["warnings"]}
    assert "sensitive_local" in codes, codes
    # the offline glossary is local, so it runs even in sensitive mode and discloses itself
    assert "offline_translation" in codes, codes
    assert r["language"] == "hi"

    print("T044 OK: sensitive non-English uses local glossary translation with disclosure (no external call)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
