"""T012 acceptance: future-effective excluded until as_of; repealed excluded; law-as-of surfaced."""
import pathlib
import sys
from datetime import date, timedelta

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.integrations.fakes import FakeEmbeddings, FakeLLM
    from app.retrieval.chunking import Chunk, chunk_doc
    from app.retrieval.hybrid import HybridRetriever
    from app.retrieval.keyword_index import BM25Index
    from app.retrieval.vector_store import InMemoryVectorStore
    from app.workflow.pipeline import AnswerService
    from app.workflow.schema import ChatRequest

    chunks = [c for d in ingest(load_manifest(CORPUS / "manifest.json"), CORPUS) for c in chunk_doc(d)]
    emb = FakeEmbeddings()
    vs = InMemoryVectorStore()
    vs.add(emb.embed([c.text for c in chunks]), chunks)
    ki = BM25Index()
    ki.add(chunks)
    retr = HybridRetriever(vs, ki, emb)

    today = date.today()
    future = today + timedelta(days=365)
    fut = Chunk(
        id="future_rule#c0", doc_id="future_rule", title="Future Rule", section="99",
        text="zephyr protocol quantum ledger novel extraction method effective later",
        jurisdiction="india", authority_level="statute", status="in_force",
        url="u", document_hash="h", effective_date=future,
    )
    vs.add(emb.embed([fut.text]), [fut])
    ki.add([fut])
    q = "zephyr protocol quantum ledger novel extraction method"

    now_ids = [h.evidence_id for h in retr.retrieve(q, k=5, as_of=today)]
    assert "future_rule#c0" not in now_ids, "future-effective provision must be excluded as of today"

    later_ids = [h.evidence_id for h in retr.retrieve(q, k=5, as_of=future + timedelta(days=1))]
    assert "future_rule#c0" in later_ids, "future provision must be included once effective"

    rep = Chunk(
        id="rep#c0", doc_id="rep", title="Repealed", section="8",
        text="zephyr protocol quantum ledger repealed old", jurisdiction="india",
        authority_level="statute", status="repealed", url="u", document_hash="h",
    )
    vs.add(emb.embed([rep.text]), [rep])
    ki.add([rep])
    assert "rep#c0" not in [h.evidence_id for h in retr.retrieve(q, k=5, as_of=future + timedelta(days=1))], \
        "repealed source must remain excluded"

    svc = AnswerService(retr, FakeLLM(), emb, "v0")
    r = svc.answer(ChatRequest(query="Under Section 3(p), can I patent a traditional formulation?"))
    assert r.claims and str(r.as_of) == str(today), "response must carry law-as-of (today by default)"
    r2 = svc.answer(ChatRequest(query="Under Section 3(p), can I patent?", as_of=today))
    assert str(r2.as_of) == str(today), "explicit as_of must be honoured"

    print("T012 OK: future-effective excluded until as_of; repealed excluded; law-as-of surfaced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
