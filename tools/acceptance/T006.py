"""T006 acceptance: BM25 exact-reference retrieval outranks; deterministic; grounding invariant."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.retrieval.chunking import chunk_doc
    from app.retrieval.keyword_index import BM25Index, KeywordIndex

    chunks = [c for d in ingest(load_manifest(CORPUS / "manifest.json"), CORPUS) for c in chunk_doc(d)]
    idx = BM25Index()
    idx.add(chunks)
    assert isinstance(idx, KeywordIndex)

    r = idx.search("Section 3(p)")
    assert r and r[0].evidence_id.startswith("patents_1970_s3p"), f"patents expected, got {r and r[0].evidence_id}"

    r2 = idx.search("geographical indication registration")
    assert r2 and r2[0].evidence_id.startswith("gi_act_1999"), f"gi expected, got {r2 and r2[0].evidence_id}"

    r3 = idx.search("Form I State Biodiversity Board")
    assert r3 and r3[0].evidence_id.startswith("bda_2002_s7"), f"bda expected, got {r3 and r3[0].evidence_id}"

    assert idx.search("zzznonexistentquux") == [], "no-overlap query must return empty"

    for x in r + r2 + r3:
        assert x.source.id == x.evidence_id, "grounding invariant"

    print("T006 OK: BM25 exact-reference retrieval outranks; empty on no-overlap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
