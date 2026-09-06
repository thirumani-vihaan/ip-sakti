"""T010 acceptance: strong match -> HIGH + grounded; out-of-corpus -> abstain; unsupported -> abstain."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def _service(llm):
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.integrations.fakes import FakeEmbeddings
    from app.retrieval.chunking import chunk_doc
    from app.retrieval.hybrid import HybridRetriever
    from app.retrieval.keyword_index import BM25Index
    from app.retrieval.vector_store import InMemoryVectorStore
    from app.workflow.pipeline import AnswerService

    chunks = [c for d in ingest(load_manifest(CORPUS / "manifest.json"), CORPUS) for c in chunk_doc(d)]
    emb = FakeEmbeddings()
    vs = InMemoryVectorStore()
    vs.add(emb.embed([c.text for c in chunks]), chunks)
    ki = BM25Index()
    ki.add(chunks)
    return AnswerService(HybridRetriever(vs, ki, emb), llm, emb, "v0")


def main() -> int:
    from app.integrations.fakes import FakeLLM
    from app.models.enums import EvidenceStrength
    from app.workflow.schema import ChatRequest

    svc = _service(FakeLLM())

    strong = svc.answer(ChatRequest(query="Under Section 3(p), can I patent a traditional formulation?"))
    assert strong.claims, "strong query should produce grounded claims"
    assert strong.evidence_strength == EvidenceStrength.HIGH, f"got {strong.evidence_strength}"
    src_ids = {s.id for s in strong.sources}
    assert all(set(c.source_ids) <= src_ids for c in strong.claims), "claims must cite returned sources"

    ooc = svc.answer(ChatRequest(query="monsoon heatwave weather forecast cricket score tonight"))
    assert ooc.claims == [] and any(w.code == "out_of_corpus" for w in ooc.warnings), "out-of-corpus must abstain"

    halluc = _service(FakeLLM(hallucinate=True))
    r = halluc.answer(ChatRequest(query="Under Section 3(p), is this patentable?"))
    assert r.claims == [] and any(w.code == "unsupported" for w in r.warnings), "fabricated output must abstain"

    print("T010 OK: strong->HIGH grounded; out-of-corpus->abstain; unsupported->abstain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
