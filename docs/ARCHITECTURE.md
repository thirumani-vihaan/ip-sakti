# ARCHITECTURE

Modules, responsibilities, data flow, boundaries. State is immutable + explicitly transitioned wherever practical.

## Backend modules (`backend/app/`)
| Module | Single responsibility |
|---|---|
| `main.py` | `build_app()` / lifespan — the ONE real entry point; constructs real-or-fake providers from config and injects them. |
| `config.py` | Load settings + feature flags from env; decide real-vs-fake per dependency. |
| `workflow/schema.py` | **Immutable domain contract**: ChatRequest, ChatResponse, Claim, Source, RetrievalHit, RuleResult, Warning. |
| `models/enums.py` | Jurisdiction, ForceState, EvidenceStrength, FormulationType, Domain, AnswerMode. |
| `workflow/pipeline.py` | Orchestrate the answer workflow (below); owns no I/O, only sequences typed steps. |
| `workflow/query_understanding.py` | Language detect + entity/reference extraction. |
| `workflow/domain_router.py` | Multi-label domain profiling + mandatory triggers + ambiguity protocol. |
| `workflow/reference_resolver.py` | Resolve exact Section/Form/Act references before retrieval. |
| `workflow/generation.py` | Grounded generation over server-assigned evidence IDs (via LLMProvider). |
| `workflow/citation_validator.py` | Reject unknown IDs; verify facts vs source; drop unsupported → abstain. |
| `workflow/evidence_strength.py` | Composite evidence-strength scoring. |
| `workflow/abstention.py` | Fail-closed decision logic. |
| `retrieval/{hybrid,vector_store,keyword_index,fallback_index,chunking,embeddings}.py` | Hybrid BM25+vector retrieval, legal-aware chunking, local fallback index. |
| `rules/{engine,dsl,abs_rules,classification_rules}.py` | Deterministic versioned rule engine + rule sets. |
| `corpus/{manifest,ingestion,sources}.py` | Versioned corpus + provenance + ingestion. |
| `integrations/{provider,gemini,bhashini}.py` | Real SDK clients behind provider interfaces + circuit breaker. |
| `i18n/{glossary,translate}.py` | Locked legal glossary + term-preserving translation. |
| `offline/{precompute,cache}.py` | Persist embeddings/indexes; approved demo-answer cache. |
| `api/routes/*` | Thin HTTP layer over the workflow + rule engine. |
| `api/middleware/*` | Disclaimer injection, global/per-IP rate budget, request→release pinning. |
| `utils/{pdf_generator,logger,security}.py` | PDF export from validated object; redacted logging; input sanitization / injection boundary. |

## Frontend (`frontend/src/`)
React 18 + Vite. Chat + SourceDrawer + badges (evidence-strength, law-as-of, answer-mode), jurisdiction toggle, ClassificationWizard, ABSWizard, Roadmap, ComparisonTool, Sensitive-Invention toggle, disclaimer banner. Talks to the backend via a mockable API client (Vitest + RTL for offline tests).

## Answer data flow
```
query
  -> query_understanding (language, entities, statute/section refs)
  -> domain_router (multi-label + mandatory triggers)         [+ ambiguity -> ask/insufficient]
  -> reference_resolver (exact refs)  ->  retrieval/hybrid (BM25 + vector, RRF)
       filtered by jurisdiction + in-force(as_of) BEFORE ranking
  -> generation (grounded on evidence IDs only)   [LLMProvider]
  -> citation_validator (reject unknown IDs; verify facts)     [fail-closed -> abstention]
  -> evidence_strength + warnings + "law as of"
  -> ChatResponse (validated)
```
Compliance questions additionally run `rules/engine` (deterministic). Roadmap/comparison/PDF reuse the SAME validated ChatResponse — no second generation.

## Module boundaries (where integration bugs live — made explicit)
1. workflow ↔ `LLMProvider` / `EmbeddingProvider` / `TranslationProvider` (injected; never import SDK in workflow).
2. workflow ↔ `VectorStore` / `KeywordIndex`.
3. workflow ↔ `rules/engine` (typed RuleResult only).
4. api ↔ workflow (HTTP request → typed workflow input; typed ChatResponse → HTTP).
5. `main.build_app()` ↔ every provider factory (the one place real impls are constructed).
6. corpus/ingestion ↔ retrieval indexes (release bundle: manifest + chunks + indexes share one release id).

## State & concurrency
- Workflow state is a typed, immutable object threaded through steps; each step returns a new value, never mutates in place.
- **Streaming answer path:** status/progress events stream first; the FINAL prose is rendered ONLY after `citation_validator` completes. Unvalidated claims are never streamed to the user. (Sequential: validate → then render; not concurrent.)
- Retrieval is synchronous per request; provider calls have timeouts + circuit breaker; corpus is never re-indexed at startup (only count/hash verified).

## Offline / degraded path
If `LLMProvider(real)` fails or is absent: `offline` returns an extractive answer (top passages + citations, no generation), `answer_mode="extractive"`; approved demo-answer cache is an outage fallback only, visibly labelled.
