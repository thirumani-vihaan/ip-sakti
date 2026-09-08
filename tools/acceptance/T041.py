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

    # forged but self-consistent: a fabricated source cited by the claim must still be
    # rejected because its id/hash is not in the server's real corpus
    forged3 = {
        **good,
        "claims": [{"text": "A patent is automatically granted.", "source_ids": ["attacker#c0"]}],
        "sources": [{
            "id": "attacker#c0", "title": "Fake Act", "section": "1", "url": "http://x",
            "local_excerpt": "fake", "status": "in_force", "authority": "statute",
            "effective_date": None, "as_of": good["as_of"], "document_hash": "sha256:deadbeef",
        }],
    }
    assert client.post("/api/export/pdf", json=forged3).status_code == 422

    # real source id but tampered provenance hash must be rejected
    tampered = {**good, "sources": [{**good["sources"][0], "document_hash": "sha256:tampered"}]}
    assert client.post("/api/export/pdf", json=tampered).status_code == 422

    # real id + real hash but tampered TITLE/excerpt must also be rejected (metadata authenticity)
    tampered_meta = {**good, "sources": [{
        **good["sources"][0],
        "title": "Fabricated Automatic Approval Act",
        "local_excerpt": "All traditional remedies are automatically approved.",
    }]}
    assert client.post("/api/export/pdf", json=tampered_meta).status_code == 422

    # server-authoritative report metadata: forged warnings / corpus_version are sanitized
    from app.api.routes.export import _safe_response
    from app.workflow.schema import ChatResponse

    forged_meta = ChatResponse(
        claims=[], sources=[],
        warnings=[{"code": "made_up", "message": "Patents are automatically granted without examination."}],
        answer_mode="live", evidence_strength="high", jurisdiction="india", language="en",
        as_of=good["as_of"], corpus_version="official-certified",
    )
    safe = _safe_response(forged_meta, "v0")
    assert safe.warnings == [], "client warnings must be dropped from exports"
    assert safe.corpus_version == "v0", "corpus_version must be server-authoritative"
    assert safe.evidence_strength.value == "limited", "a no-claims report must not show high strength"

    print("T041 OK: PDF export authenticates sources vs the corpus and refuses ungrounded/forged claims")
    return 0


if __name__ == "__main__":
    sys.exit(main())
