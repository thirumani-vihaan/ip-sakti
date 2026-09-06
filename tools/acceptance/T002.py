"""T002 acceptance: fakes satisfy the interfaces; grounding-by-construction; force_error works."""
import pathlib
import sys
from datetime import date

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def _hit(eid: str, text: str):
    from app.workflow.schema import RetrievalHit, Source
    src = Source(id=eid, title="Patents Act 1970", section="3(p)", local_excerpt=text,
                 status="in_force", authority="statute", as_of=date.today(), document_hash="h")
    return RetrievalHit(evidence_id=eid, text=text, score=1.0, source=src)


def main() -> int:
    from app.integrations import fakes
    from app.integrations.provider import (
        EmbeddingProvider, LLMProvider, ProviderError, TranslationProvider,
    )

    llm = fakes.FakeLLM()
    emb = fakes.FakeEmbeddings()
    tr = fakes.FakeTranslation()

    # structural interface conformance (runtime_checkable Protocols)
    assert isinstance(llm, LLMProvider)
    assert isinstance(emb, EmbeddingProvider)
    assert isinstance(tr, TranslationProvider)

    hits = [_hit("e1", "Section 3(p) bars traditional knowledge"), _hit("e2", "novelty requirement")]

    # grounded-by-construction: claims cite ONLY supplied evidence ids
    claims = llm.generate("q", hits)
    supplied = {h.evidence_id for h in hits}
    assert claims and all(set(c.source_ids) <= supplied for c in claims), "FakeLLM cited an unsupplied id"

    # hallucinate + malformed modes cite ids NOT supplied (for validator tests)
    assert fakes.FakeLLM(hallucinate=True).generate("q", hits)[0].source_ids == ["e999"]
    assert fakes.FakeLLM(force_error="malformed").generate("q", hits)[0].source_ids == ["e_missing"]

    # force_error -> retryable ProviderError
    for mode in ("timeout", "rate_limit"):
        try:
            fakes.FakeLLM(force_error=mode).generate("q", hits)
            raise AssertionError(f"expected ProviderError for {mode}")
        except ProviderError as e:
            assert e.retryable is True

    # empty evidence -> empty claims (abstain upstream)
    assert llm.generate("q", []) == []

    # embeddings deterministic + fixed dim + lexical overlap similarity
    v1 = emb.embed(["Section 3(p) turmeric formulation"])[0]
    v2 = emb.embed(["Section 3(p) turmeric formulation"])[0]
    assert v1 == v2 and len(v1) == 256, "embeddings must be deterministic, dim 256"
    close = emb.embed(["turmeric formulation patent"])[0]
    far = emb.embed(["heatwave weather forecast"])[0]
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    assert dot(v1, close) > dot(v1, far), "lexical-overlap query must score higher"

    # translation preserves the section number verbatim
    out = tr.translate("Under Section 3(p), TK is barred.", "en", "hi")
    assert "Section 3(p)" in out, "statute/section must be preserved verbatim"
    assert tr.translate("same", "en", "en") == "same"

    print("T002 OK: providers + fakes conform; grounded-by-construction; force_error + determinism verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
