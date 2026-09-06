"""T019 acceptance: sensitive mode -> extractive, grounded, zero LLM calls."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


class _Tripwire:
    """An LLM that fails loudly if ever called — proves sensitive mode bypasses generation."""

    def generate(self, prompt, evidence):
        raise AssertionError("LLM must NOT be called in Sensitive-Invention mode")


class _EmbTripwire:
    """An embedder that fails loudly if ever called — proves sensitive mode makes no external embed call."""

    def embed(self, texts):
        raise AssertionError("embedder must NOT be called in Sensitive-Invention mode")


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.integrations.fakes import FakeEmbeddings
    from app.models.enums import AnswerMode
    from app.retrieval.chunking import chunk_doc
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
    svc = AnswerService(HybridRetriever(vs, ki, _EmbTripwire()), _Tripwire(), emb, "v0")

    r = svc.answer(ChatRequest(query="Under Section 3(p), can I patent a traditional formulation?", sensitive=True))
    assert r.answer_mode == AnswerMode.EXTRACTIVE and r.claims, "sensitive mode must return extractive cited answer"
    assert any(w.code == "sensitive_local" for w in r.warnings), "must warn that processing is local"
    assert all(set(c.source_ids) <= {s.id for s in r.sources} for c in r.claims), "must stay grounded"

    print("T019 OK: sensitive mode -> extractive, grounded, zero LLM calls")
    return 0


if __name__ == "__main__":
    sys.exit(main())
