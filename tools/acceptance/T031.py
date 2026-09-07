"""T031 acceptance: POST /api/analyze grounds an uploaded doc against the corpus, ephemerally."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    client = TestClient(build_app(Settings()))

    content = (
        b"Our product is a traditional knowledge based Ayurvedic formulation. "
        b"We want to know if it is patentable under Section 3(p) of the Patents Act."
    )
    r = client.post("/api/analyze", files={"file": ("product.txt", content, "text/plain")})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["filename"] == "product.txt"
    assert body["extracted_preview"], "expected an extracted preview"
    analysis = body["analysis"]
    # grounded: any cited source id must be a real returned source (never fabricated)
    src_ids = {s["id"] for s in analysis["sources"]}
    assert all(set(c["source_ids"]) <= src_ids for c in analysis["claims"]), "citations must be grounded"

    # unsupported type is rejected
    assert client.post("/api/analyze", files={"file": ("x.exe", b"MZ", "application/octet-stream")}).status_code == 415

    # EPHEMERAL: the upload must NOT be added to the knowledge base
    assert client.get("/api/sources").json()["count"] == 14, "upload must not pollute the corpus"

    print("T031 OK: /api/analyze grounds uploaded doc against corpus; ephemeral; type-checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
