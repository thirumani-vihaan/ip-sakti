"""One-command demo smoke test: exercises the full API path on fixtures (no credentials)."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    assert client.get("/api/health").json()["status"] == "ok"

    chat = client.post("/api/chat", json={
        "query": "Under Section 3(p), can I patent a traditional formulation?"
    }).json()
    assert chat["claims"], "chat should be grounded"

    ooc = client.post("/api/chat", json={"query": "weather forecast cricket score tonight"}).json()
    assert ooc["claims"] == [], "out-of-scope must abstain"

    abs_r = client.post("/api/abs/check", json={
        "resource_origin": "india", "use": "commercial", "applicant": "indian_entity", "tk_association": "no",
    }).json()
    assert abs_r["status"] == "decided"

    cls = client.post("/api/classify", json={
        "in_first_schedule": "no", "modified": "modified", "novel_actives": "no", "intended_use": "food",
    }).json()
    assert cls["status"] == "decided"

    rm = client.post("/api/roadmap", json={"query": "turmeric formulation"}).json()
    assert rm["steps"]

    cmp = client.post("/api/compare", json={
        "option_a": "patent modified formulation",
        "option_b": "biological resource commercial prior intimation",
    }).json()
    assert "a" in cmp and "b" in cmp

    pdf = client.post("/api/export/pdf", json=chat)
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"

    # newer surfaces: search, sources registry, ephemeral upload analysis, escalation
    srch = client.get("/api/search", params={"q": "Section 3(p) traditional knowledge", "k": 3}).json()
    assert srch["results"], "search should return grounded hits"

    srcs = client.get("/api/sources").json()
    assert srcs["count"] >= 13 and srcs["sources"], "sources registry should list the corpus"

    up = client.post("/api/analyze", files={"file": (
        "label.txt", b"Ayurvedic traditional knowledge formulation patent Section 3(p)", "text/plain")})
    assert up.status_code == 200 and "analysis" in up.json(), "upload analysis should return an answer"

    esc = client.post("/api/escalate", json={"query": "Can I patent X?"}).json()
    assert esc["reference_id"].startswith("IPSAKTI-"), "escalation should return a reference id"

    print("smoke_demo OK: health, chat(grounded+abstain), abs, classify, roadmap, compare, "
          "pdf, search, sources, analyze, escalate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
