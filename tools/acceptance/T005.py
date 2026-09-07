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

    # a query using text distinctive to Patents s.3(p) must surface that provision first
    h = top("aggregation or duplication of known properties of traditionally known component patentable")
    assert h and h[0].evidence_id.startswith("patents_1970_s3p"), f"patents expected, got {h[0].evidence_id}"

    h2 = top("biological resource commercial prior intimation Form I State Biodiversity Board")
    assert h2 and h2[0].evidence_id.startswith("bda_2002_s7"), f"bda expected, got {h2[0].evidence_id}"

    # jurisdiction filter: the corpus now includes international instruments (TRIPS/PCT/Nagoya)
    _INTL = {"trips_art27", "pct_overview", "nagoya_cbd"}
    intl = top("anything", jur="international")
    assert intl and all(x.evidence_id.split("#")[0] in _INTL for x in intl), "international filter must return only intl docs"
    india = top("anything", jur="india")
    assert india and all(x.evidence_id.split("#")[0] not in _INTL for x in india), "india filter must exclude intl docs"

    order1 = [x.evidence_id for x in top("traditional knowledge")]
    order2 = [x.evidence_id for x in top("traditional knowledge")]
    assert order1 == order2, "retrieval must be deterministic"

    for x in h + h2:
        assert x.source.id == x.evidence_id, "grounding invariant: Source.id == evidence_id"

    print("T005 OK: semantic retrieval returns expected chunks; deterministic; jurisdiction filter works")
    return 0


if __name__ == "__main__":
    sys.exit(main())
