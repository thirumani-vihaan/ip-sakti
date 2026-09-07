"""T037 acceptance: oversized roadmap/compare input is rejected at the boundary (422, not 500)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))
    huge = "a " * 1500  # ~3000 chars, exceeds the 2000-char query bound

    r = client.post("/api/roadmap", json={"query": huge})
    assert r.status_code == 422, f"oversized roadmap query must be 422, got {r.status_code}"

    c = client.post("/api/compare", json={"option_a": huge, "option_b": "patent"})
    assert c.status_code == 422, f"oversized compare option must be 422, got {c.status_code}"

    # normal-sized requests still succeed
    assert client.post("/api/roadmap", json={"query": "turmeric formulation"}).status_code == 200
    assert client.post("/api/compare", json={"option_a": "patent", "option_b": "gi"}).status_code == 200

    print("T037 OK: oversized roadmap/compare input rejected as 422; normal input still 200")
    return 0


if __name__ == "__main__":
    sys.exit(main())
