# RISK_LOG

| # | Risk | Likelihood/Impact | Mitigation |
|---|---|---|---|
| R1 | **Citation hallucination** — model cites a real-but-irrelevant or invented source. | med / CRITICAL | Server-assigned evidence IDs only; validator rejects unknown IDs + checks section/date/amount vs source; drop unsupported → abstain. Grounding is dimension-0 in Phase 3; any regression stops the loop. Extra adversarial fixtures in `fixtures/llm/`. |
| R2 | **Corpus quality/coverage** — thin or wrong corpus → weak answers. | HIGH / HIGH | Start narrow + curated; `fetch_corpus.py` records provenance/hash/licence; offline tests use a controlled sample fixture; corpus fetch is its own reviewable commit. |
| R3 | **Gemini rate limits (429)** mid-demo. | med / HIGH | Provider abstraction with backoff + circuit breaker; offline extractive fallback (answer_mode=extractive); cached approved demo answers as labelled outage fallback; prewarm local embedder in smoke test. |
| R4 | **Legal-term mistranslation** (Hindi/Telugu changes meaning). | med / HIGH | Locked bilingual glossary; preserve statute names/section numbers verbatim; show normalized English; abstain if translation changes a compliance input; separate Hindi/Telugu fixtures incl. code-mixed. |
| R5 | **Chunk-context loss** — proviso/explanation split from its clause. | med / med | Hierarchy-aware chunking (keep proviso/explanation with parent); tables/forms extracted separately; T004 acceptance asserts section context preserved. |
| R6 | **Stale/superseded law** presented as current. | med / HIGH | ForceState + effective_date + as_of; retrieval returns in-force version; conflict → warn/abstain; visible "law as of". |
| R7 | **Retrieval quality** — hybrid fusion mis-ranks; exact refs lost. | med / med | Resolve exact refs before ranking; RRF; authority as tie-break; T007 Recall@k acceptance gate; tune in Phase 3. |
| R8 | **Wiring gap** — feature built but real factory never constructed at entry point. | med / HIGH | T011 wiring test per dependency; re-checked every Phase-3 iteration (dimension 15); regression stops the loop. |
| R9 | **Prompt injection** via retrieved/uploaded content. | low / med | Treat retrieved text as data, never instructions; sanitize; injection fixtures; ingestion disabled in public/demo mode. |
| R10 | **Non-deterministic compliance** — LLM decides an obligation. | low / HIGH | Rule engine decides; LLM only explains; T014 asserts same input → same obligation across 100 runs; missing fact → insufficient. |
| R11 | **Dependency/version breakage** (Chroma 0.5.x, torch, sentence-transformers). | med / med | Python 3.11; requirements.in→lock; smoke test prewarms model + verifies Chroma Settings; CPU torch wheel fallback. |
| R12 | **Secret leakage** into a commit. | low / CRITICAL | Per-feature secret-scan gate (with doc-pattern exemptions); .env gitignored; .env.example only; never commit .git-embedded tokens. |
| R13 | **Contract drift** — schema changed as a quiet "polish". | low / HIGH | schema.py immutable; any change is its own high-visibility candidate, flagged + docs updated. |
