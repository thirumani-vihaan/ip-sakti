# SPEC_SUMMARY

Distilled from `docs/IMPLEMENTATION_PLAN.md`. This is the contract the build is judged against.

## Mission
A multilingual, **citation-backed** AI triage assistant for Intellectual Property and regulatory guidance in Ayurveda (national + selected international regimes). SIH 2026, PS 45, Ministry of AYUSH. It helps users reach the right question, form, authority, and professional faster — **informational guidance, not legal advice**.

## Goals
- Answer IP / TK-risk / ABS / regulatory / (selected) international questions grounded in official sources.
- Every answer maps to a verifiable source passage the user can open.
- Current-law aware; deterministic, reproducible compliance logic.
- Multilingual (English, Hindi, Telugu for the demo).
- Runs offline-capable and fully testable with no API keys.

## Hard constraints
1. **Offline-testable:** the entire test suite runs with NO real credentials and NO network, on fixtures. Setting `.env` keys is the only handoff to live mode — no code change.
2. **Provider abstraction:** workflow code never imports Gemini/Bhashini SDKs directly; only injectable interfaces (LLMProvider, EmbeddingProvider, TranslationProvider, VectorStore, KeywordIndex).
3. **Grounding is sacred:** the model may cite only server-assigned evidence IDs; it cannot invent sources. Fabricated/unsupported citations are the worst possible failure.
4. **Fail closed:** on missing evidence / conflicting or superseded law / out-of-corpus / provider failure → abstain or show the raw passage; never guess.
5. **Deterministic compliance:** ABS + formulation classification decided by versioned rule sets, not the LLM; same facts → same obligation; each cites its legal source + rule_version.
6. **Immutable contract:** the schema/enums are a global contract once approved.
7. **Git:** one feature = one atomic commit + push, gated by a secret-scan. **Sole author = repo owner; never add a Copilot co-author/contributor trailer.**
8. **No test-gaming; no silent failure** (no bare `except: pass` without a logged reason).

## Tech stack
- Frontend: React 18 + Vite (Vitest + React Testing Library for offline tests).
- Backend: Python 3.11 + FastAPI.
- Retrieval: ChromaDB (vector) + BM25 (keyword), reciprocal-rank fusion.
- LLM + embeddings: Google Gemini, with local `sentence-transformers` extractive fallback.
- Multilingual: Bhashini (Hindi/Telugu; voice optional, flagged).
- Compliance: versioned deterministic rule engine.
- Packaging: Docker Compose (frontend, backend, chromadb + healthcheck).

## The five design principles (product guarantees)
1. No claim without a validated citation.
2. Show the evidence (open the exact passage, served locally too).
3. Current law by default, with a visible "law as of <date>".
4. Fail safe, not confident.
5. Guidance, not legal opinion (escalate filing/compliance to a professional / NBA / SBB).

## Acceptance criteria (demo-readiness)
- Corpus loaded + integrity-verified at startup.
- English and Hindi queries both return cited answers.
- Clicking a citation opens the exact supporting passage.
- An out-of-scope question correctly abstains.
- Current-law filtering + "law as of" visible.
- ABS wizard produces a sourced obligation summary (with an insufficient-info path).
- Cloud-outage fallback returns an extractive, labelled answer.
- PDF export matches the on-screen validated answer.
- Whole suite passes on fixtures only (zero credentials).

## Honest metrics (reported with sample size, never as guarantees)
- Retrieval quality: Recall@k on the curated test set.
- Citation validity: % of citations that map to a real supporting passage (fabricated = 0 target).
- Correct abstention rate (and false-abstention rate).
- Legal-term preservation across Hindi/Telugu (not BLEU).
- Latency: p50 / p95 for simple and multi-domain queries.

## In-scope features (map to build phases)
Chat with inline citations + source drawer; evidence-strength + answer-mode badges; India/International jurisdiction toggle; hybrid retrieval; grounded generation + citation validation; temporal current-law; offline/extractive fallback; deterministic ABS + classification wizards; multi-domain routing; Hindi/Telugu; roadmap + comparison; sensitive-invention mode; PDF export; eval harness + demo smoke suite; Docker deployment.

## Explicit NON-GOALS (out of scope for this build — deferred to the plan's Future Enhancements)
- Full legal-version history (provision-level amendment lineage over time).
- Expert-panel blind benchmark (IP lawyer / AYUSH / ABS-NBA / patent agent adjudication).
- Automated NLI entailment verification of each claim.
- Neo4j knowledge-graph visualisation.
- Live scheduled scrapers / auto corpus sync.
- User accounts / roles / analytics / admin console.
- OAuth paid-source connectors.
- Broad 22-language coverage + full voice.
- Full TKDL database integration (not publicly available; capability-gated).
- State-law coverage (demo is central-law; state questions → referral).

## Ambiguities / decisions flagged (see intake notes; resolved with defaults, no silent guessing)
1. **Exact corpus document set + URLs:** the plan lists source families (India Code, ipindia, ayush, DPIIT, WIPO) but not exact document IDs. Decision: `scripts/fetch_corpus.py` targets a defined starter list; offline tests use a small committed sample fixture. Corpus quality is the main real-world variable.
2. **Retrieval acceptance gate (Recall@k threshold):** not numerically fixed in the plan. Decision: set an initial gate during Phase 1 against the curated fixture set; tune in Phase 3.
3. **Sensitive-Invention mode implementation:** reuse the extractive/no-cloud path (no separate local LLM) to keep scope tight.
4. **Embeddings for offline tests:** deterministic fake embeddings (seeded) so retrieval tests are reproducible without network; real path uses Gemini `text-embedding-004` with `sentence-transformers` local fallback.
