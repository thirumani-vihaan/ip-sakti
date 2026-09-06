"""T018 acceptance: roadmap + compare reuse validated answers (grounded steps cite their sources)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def _grounded(ans: dict) -> bool:
    ids = {s["id"] for s in ans["sources"]}
    return all(set(c["source_ids"]) <= ids for c in ans["claims"])


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    rr = client.post("/api/roadmap", json={"query": "turmeric formulation traditional knowledge"}).json()
    assert len(rr["steps"]) >= 2, rr
    grounded = [s for s in rr["steps"] if s["answer"]["claims"]]
    assert grounded, "roadmap should have at least one grounded step"
    for s in rr["steps"]:
        assert _grounded(s["answer"]), f"roadmap step not grounded: {s['title']}"

    cr = client.post("/api/compare", json={
        "option_a": "patent for a modified turmeric formulation",
        "option_b": "biological resource commercial prior intimation State Biodiversity Board",
    }).json()
    assert "a" in cr and "b" in cr
    for k in ("a", "b"):
        assert _grounded(cr[k]), f"compare side {k} not grounded"

    print("T018 OK: roadmap + compare reuse validated answers; all steps grounded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
