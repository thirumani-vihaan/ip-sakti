"""T028 acceptance: offline query understanding — script language detection + auto-language route."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app
    from app.workflow.query_understanding import detect_language, understand

    assert detect_language("Can I patent a formulation?") == "en"
    assert detect_language("क्या मैं पेटेंट कर सकता हूँ") == "hi"
    assert detect_language("నేను పేటెంట్ చేయవచ్చా") == "te"

    u = understand("Under Section 3(p), can I patent traditional knowledge?")
    assert "3(p)" in u["section_refs"], u
    assert "patent" in u["domains"] and "tk_risk" in u["domains"], u
    assert u["language"] == "en"

    # the chat route resolves language: "auto" from the query script
    client = TestClient(build_app(Settings()))
    r = client.post("/api/chat", json={"query": "पेटेंट कानून", "language": "auto"})
    assert r.status_code == 200, r.text
    assert r.json()["language"] == "hi", "auto-detect should set Hindi from Devanagari input"

    print("T028 OK: script language detection; understanding hints; auto-language routing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
