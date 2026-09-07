"""T040 acceptance: /api/compare honours per-side jurisdiction (India vs International kept apart)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))
    r = client.post("/api/compare", json={
        "option_a": "patent a traditional knowledge formulation Section 3(p)",
        "option_b": "TRIPS patentable subject matter plant varieties sui generis",
        "jurisdiction_a": "india",
        "jurisdiction_b": "international",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["a"]["jurisdiction"] == "india"
    assert body["b"]["jurisdiction"] == "international"

    # answer-sets stay separate: the international side must not cite Indian statutes
    intl = {"trips_art27", "pct_overview", "nagoya_cbd"}
    b_sources = {s["id"].split("#")[0] for s in body["b"]["sources"]}
    assert not (b_sources - intl), f"international side leaked non-intl sources: {b_sources}"

    print("T040 OK: /api/compare keeps India vs International answer-sets separate per side")
    return 0


if __name__ == "__main__":
    sys.exit(main())
