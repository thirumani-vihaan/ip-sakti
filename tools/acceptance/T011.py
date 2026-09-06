"""T011 acceptance: /api/chat grounded + abstain; /api/health; real provider factories reachable."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app, make_embeddings, make_llm, make_translation

    app = build_app(Settings())  # no creds -> fixture mode
    client = TestClient(app)

    assert client.get("/api/health").json()["status"] == "ok"

    r = client.post("/api/chat", json={"query": "Under Section 3(p), can I patent a traditional formulation?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["claims"], "expected grounded claims"
    src_ids = {s["id"] for s in body["sources"]}
    assert all(set(c["source_ids"]) <= src_ids for c in body["claims"]), "claims must cite returned sources"
    assert body["evidence_strength"] == "high"

    r2 = client.post("/api/chat", json={"query": "monsoon heatwave weather forecast cricket score tonight"})
    b2 = r2.json()
    assert b2["claims"] == [] and any(w["code"] == "out_of_corpus" for w in b2["warnings"]), "out-of-corpus must abstain"

    # WIRING (loop 2.4): the real factories build_app uses select real impls when creds present
    real = Settings(gemini_api_key="x", bhashini_user_id="u", bhashini_ulca_key="z", bhashini_inference_key="k")
    assert type(make_llm(real)).__name__ == "GeminiLLM"
    assert type(make_embeddings(real)).__name__ == "GeminiEmbeddings"
    assert type(make_translation(real)).__name__ == "BhashiniTranslation"
    # ...and fall back to fakes without creds (what build_app used above)
    assert type(make_llm(Settings())).__name__ == "FakeLLM"
    assert type(make_embeddings(Settings())).__name__ == "FakeEmbeddings"
    assert type(make_translation(Settings())).__name__ == "FakeTranslation"
    assert type(app.state.providers["llm"]).__name__ == "FakeLLM"

    print("T011 OK: /api/chat grounded + abstain; /api/health; real provider factories reachable from build_app")
    return 0


if __name__ == "__main__":
    sys.exit(main())
