"""T013 acceptance: LLM outage -> extractive cited; cache hit -> cached; breaker opens/closes; healthy -> live."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))

Q = "Under Section 3(p), can I patent a traditional formulation?"


def _service(llm, cache=None):
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
    return AnswerService(HybridRetriever(vs, ki, emb), llm, emb, "v0", cache=cache)


def main() -> int:
    from app.integrations.fakes import FakeLLM
    from app.integrations.provider import CircuitBreaker
    from app.models.enums import AnswerMode
    from app.offline.cache import DemoCache
    from app.workflow.schema import ChatRequest

    # 1) LLM outage -> extractive, grounded, labelled degraded
    r = _service(FakeLLM(force_error="timeout")).answer(ChatRequest(query=Q))
    assert r.answer_mode == AnswerMode.EXTRACTIVE and r.claims, "outage must yield extractive cited answer"
    src_ids = {s.id for s in r.sources}
    assert all(set(c.source_ids) <= src_ids for c in r.claims), "extractive claims must be grounded"
    assert any(w.code == "degraded" for w in r.warnings)

    # 2) cache hit on outage -> CACHED labelled
    good = _service(FakeLLM()).answer(ChatRequest(query=Q))  # healthy LIVE
    assert good.answer_mode == AnswerMode.LIVE
    cache = DemoCache()
    cache.put(Q, good)
    r2 = _service(FakeLLM(force_error="rate_limit"), cache=cache).answer(ChatRequest(query=Q))
    assert r2.answer_mode == AnswerMode.CACHED and r2.claims, "cache hit on outage must be labelled cached"

    # 3) circuit breaker opens after threshold, closes on success
    br = CircuitBreaker(threshold=2)
    br.record_failure()
    assert br.healthy
    br.record_failure()
    assert not br.healthy
    br.record_success()
    assert br.healthy

    print("T013 OK: outage->extractive; cache->cached; breaker opens/closes; healthy->live")
    return 0


if __name__ == "__main__":
    sys.exit(main())
