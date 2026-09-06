# TASK_PLAN

Ordered tasks with dependencies + risk. HIGH-risk ordered early. Each task: implement → `tools/acceptance/T0XX.py` (fixture-only) → on PASS commit+push (git protocol) → on FAIL retry ≤3 then STOP.

Legend: risk = [low|med|HIGH|HIGHEST]; deps = tasks that must finish first.

| Task | Description | Deps | Risk |
|---|---|---|---|
| T000 | Repo init/scaffold + logs (ALREADY DONE — verify, don't re-init) | — | low |
| T001 | `workflow/schema.py` contract + `models/enums.py` | T000 | HIGH |
| T002 | Provider interfaces + fixture fakes (LLM/Embedding/Translation) | T001 | HIGH |
| T003 | Corpus manifest + ingestion + sample fixture (+ `scripts/fetch_corpus.py`) | T001 | med |
| T004 | Legal-aware chunking | T003 | med |
| T005 | Embeddings + Chroma VectorStore | T002,T004 | med |
| T006 | BM25 KeywordIndex | T004 | med |
| T007 | Hybrid retrieval + reference resolver (RRF, jurisdiction/as_of filter) | T005,T006 | HIGH |
| T008 | Grounded generation (evidence IDs only) | T002,T007 | med |
| T009 | Citation validator (reject unknown IDs; fact checks; drop→abstain) | T008 | HIGHEST |
| T010 | Evidence strength + abstention | T009 | HIGH |
| T011 | `/api/chat` + WIRING (real providers in build_app; per-dep reachability test) | T010 | HIGH |
| T012 | Temporal current-law (ForceState + as_of; in-force filter; law-as-of) | T007 | HIGH |
| T013 | Offline/resilience (fallback index, extractive, circuit breaker, cached mode) | T011 | HIGH |
| T014 | Deterministic rule engine + ABS + classification rule sets | T001 | HIGH |
| T015 | Domain router (multi-label + mandatory triggers + ambiguity) | T007,T014 | med |
| T016 | `/api/abs/check` + `/api/classify` | T014,T015 | med |
| T017 | i18n glossary + translate (Hindi/Telugu) | T002 | med |
| T018 | `/api/roadmap` + `/api/compare` (reuse validated object) | T011 | med |
| T019 | Sensitive-Invention mode (extractive/no-cloud) | T013 | med |
| T020 | PDF export from validated object | T011 | low |
| T021 | Frontend chat + source drawer + badges | T011 | med |
| T022 | Frontend wizards (classification + ABS) | T016,T021 | med |
| T023 | Frontend roadmap/comparison/jurisdiction/sensitive/language | T018,T022 | low |
| T024 | Eval harness (testset + run_eval) + demo smoke suite | T011,T016 | med |
| T025 | Docker compose + verify_release + README/REAL_API_SETUP | T024 | med |

## Spikes (validate risky assumptions before full build)
- T007: spike RRF fusion on the sample fixture; confirm exact "Section 3(p)" resolution beats semantic-only.
- T009: spike the deterministic fact-check (section-number/date mismatch → reject) before the full validator.
- T012: spike ForceState interval selection with a repealed + in-force pair.

## Wiring verification tracking (loop §2.4) — filled during T011 & re-checked each Phase-3 iteration
| Dependency | Real factory reachable from build_app()? | Evidence |
|---|---|---|
| LLMProvider (GeminiLLM) | OK | (grep + test) |
| EmbeddingProvider (GeminiEmbeddings) | OK | |
| TranslationProvider (BhashiniTranslation) | OK | |
| VectorStore (ChromaVectorStore) | OK | |
| KeywordIndex (BM25Index) | OK | |
