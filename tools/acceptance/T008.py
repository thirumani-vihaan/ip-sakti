"""T008 acceptance: prompt exposes only supplied evidence ids; generation cites only those ids."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.integrations.fakes import FakeEmbeddings, FakeLLM
    from app.retrieval.chunking import chunk_doc
    from app.retrieval.hybrid import HybridRetriever
    from app.retrieval.keyword_index import BM25Index
    from app.retrieval.vector_store import InMemoryVectorStore
    from app.workflow.generation import build_prompt, generate_grounded

    chunks = [c for d in ingest(load_manifest(CORPUS / "manifest.json"), CORPUS) for c in chunk_doc(d)]
    emb = FakeEmbeddings()
    vs = InMemoryVectorStore()
    vs.add(emb.embed([c.text for c in chunks]), chunks)
    ki = BM25Index()
    ki.add(chunks)
    retr = HybridRetriever(vs, ki, emb)

    q = "Can I patent a turmeric formulation based on traditional knowledge?"
    evidence = retr.retrieve(q, k=3)
    supplied = {h.evidence_id for h in evidence}

    prompt = build_prompt(q, evidence)
    assert "cite ONLY the ids provided" in prompt
    for eid in supplied:
        assert f"[{eid}]" in prompt, f"prompt missing evidence id {eid}"

    claims = generate_grounded(FakeLLM(), q, evidence)
    assert claims, "expected grounded claims"
    for c in claims:
        assert set(c.source_ids) <= supplied, f"claim cited an unsupplied id: {c.source_ids}"

    assert generate_grounded(FakeLLM(), q, []) == [], "no evidence -> no claims"

    print("T008 OK: prompt exposes only supplied ids; generation cites only those ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
