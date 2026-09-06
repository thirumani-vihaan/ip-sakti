"""T005 acceptance: fake-embedding retrieval returns expected chunks; deterministic; jurisdiction filter."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.integrations.fakes import FakeEmbeddings
    from app.retrieval.chunking import chunk_doc
    from app.retrieval.vector_store import InMemoryVectorStore, VectorStore

    docs = ingest(load_manifest(CORPUS / "manifest.json"), CORPUS)
    chunks = [c for d in docs for c in chunk_doc(d)]
    emb = FakeEmbeddings()
    store = InMemoryVectorStore()
    assert isinstance(store, VectorStore)
    store.add(emb.embed([c.text for c in chunks]), chunks)

    def top(q: str, k: int = 3, jur=None):
        return store.query(emb.embed([q])[0], k=k, jurisdiction=jur)

    h = top("traditional knowledge patent not an invention barred")
    assert h and h[0].evidence_id.startswith("patents_1970_s3p"), f"patents expected, got {h[0].evidence_id}"

    h2 = top("biological resource commercial prior intimation Form I State Biodiversity Board")
    assert h2 and h2[0].evidence_id.startswith("bda_2002_s7"), f"bda expected, got {h2[0].evidence_id}"

    assert top("anything", jur="india"), "india filter should return hits"
    assert top("anything", jur="international") == [], "international filter should be empty here"

    order1 = [x.evidence_id for x in top("traditional knowledge")]
    order2 = [x.evidence_id for x in top("traditional knowledge")]
    assert order1 == order2, "retrieval must be deterministic"

    for x in h + h2:
        assert x.source.id == x.evidence_id, "grounding invariant: Source.id == evidence_id"

    print("T005 OK: semantic retrieval returns expected chunks; deterministic; jurisdiction filter works")
    return 0


if __name__ == "__main__":
    sys.exit(main())
