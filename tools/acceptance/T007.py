"""T007 acceptance: hybrid retrieval Recall@3 on curated cases; exact-ref first; repealed dropped."""
import pathlib
import sys
from datetime import date

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))

GATE = 0.8


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.integrations.fakes import FakeEmbeddings
    from app.retrieval.chunking import Chunk, chunk_doc
    from app.retrieval.hybrid import HybridRetriever
    from app.retrieval.keyword_index import BM25Index
    from app.retrieval.vector_store import InMemoryVectorStore

    chunks = [c for d in ingest(load_manifest(CORPUS / "manifest.json"), CORPUS) for c in chunk_doc(d)]
    emb = FakeEmbeddings()
    vs = InMemoryVectorStore()
    vs.add(emb.embed([c.text for c in chunks]), chunks)
    ki = BM25Index()
    ki.add(chunks)
    retr = HybridRetriever(vs, ki, emb)

    def docs_of(q, k=3):
        return [h.evidence_id.split("#")[0] for h in retr.retrieve(q, k=k)]

    cases = [
        ("turmeric formulation traditional knowledge patent not an invention", "patents_1970_s3p"),
        ("commercial use of an Indian biological resource approval", "bda_2002_s7"),
        ("protect a regional product name geographical indication", "gi_act_1999"),
        ("What does Section 3(p) say", "patents_1970_s3p"),
        ("ABS Form I prior intimation State Biodiversity Board", "bda_2002_s7"),
    ]
    hits = sum(1 for q, exp in cases if exp in docs_of(q, 3))
    recall = hits / len(cases)
    assert recall >= GATE, f"Recall@3={recall:.2f} below gate {GATE}"

    # exact-ref goes first
    top = retr.retrieve("Under Section 3(p), is this patentable?", k=3)
    assert top and top[0].evidence_id.startswith("patents_1970_s3p"), "exact section ref must rank first"

    # repealed source is dropped even with strong lexical overlap
    repealed = Chunk(
        id="old_rule#c0", doc_id="old_rule", title="Repealed Rule", section="9",
        text="traditional knowledge turmeric patent invention aggregation known properties",
        jurisdiction="india", authority_level="statute", status="repealed",
        url="u", document_hash="h",
    )
    vs.add(emb.embed([repealed.text]), [repealed])
    ki.add([repealed])
    ids = [h.evidence_id for h in retr.retrieve("traditional knowledge turmeric patent", k=5)]
    assert "old_rule#c0" not in ids, "repealed (non in-force) source must be excluded"

    print(f"T007 OK: Recall@3={recall:.2f} (gate {GATE}); exact-ref first; repealed excluded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
