# Final Report — IP-SAKTI Sahayak

A multilingual, citation-grounded AI assistant for Ayurveda Intellectual Property and
regulatory guidance. Smart India Hackathon 2026, Ministry of AYUSH.

**Status: complete working prototype.** Backend and frontend implemented, tested, and
pushed to `origin/main`. The entire system runs offline with no API keys; Gemini and
Bhashini are optional and additive. All commits are sole-authored.

## Headline results
- **35 / 35** backend acceptance checks pass (offline, no credentials).
- **7 / 7** frontend component tests pass; production `vite build` succeeds.
- **Eval gates (18-case set):** Recall@5 = 1.00, Citation validity = 1.00,
  Safe abstention = 1.00, legal-term preservation = pass.
- One-command end-to-end smoke covers all 11 API route groups.

## What was built
### Retrieval & grounding
Hybrid retrieval (Chroma vector store + BM25, reciprocal-rank fusion) over a
version-tracked corpus with SHA-256 provenance hashes; exact Section/Form reference
resolution; jurisdiction + in-force(as_of) filtering before ranking; grounded
generation constrained to server-assigned evidence ids; a citation validator that
rejects unknown ids, fabricated sources, and reference mismatches; fail-closed
abstention; a composite evidence-strength (High/Moderate/Limited) confidence indicator.

### Deterministic compliance
A versioned, source-citing rule engine (same facts -> same result) powering the ABS
compliance helper and the six-category formulation classifier (classical, proprietary,
phytopharmaceutical, new drug, nutraceutical, cosmetic). It asks only the minimum
missing facts and never lets the LLM do legal math.

### Coverage
Six domain profiles over 13 documents: Patents s.3(p), Biodiversity Act s.7, GI Act,
Trade Marks Act, Designs Act, Copyright Act, Drugs & Cosmetics Act (AYUSH), Drugs and
Magic Remedies Act, FSSAI nutraceutical regulation, DPIIT/TKDL guidance, and the
international TRIPS, PCT and Nagoya/CBD instruments (jurisdiction-separated).

### Safety, guardrails & privacy
Escalate-to-a-human-IP-facilitator path on abstention/low-confidence; standing
"information, not legal advice" disclaimer on every answer and as a response header;
input sanitization + prompt-injection heuristic; per-client rate limiting
(X-Forwarded-For aware); structured logging; request-id headers for audit; no user
accounts (privacy by design, DPDP-aligned).

### Multilingual (Bhashini-optional)
Full neural translation via Bhashini when configured; otherwise a credential-free
offline glossary translator that localises legal terms and preserves statute/section
references verbatim. Script-based auto language detection (EN/HI/TE).

### Endpoints
`/api/chat`, `/api/search`, `/api/classify`, `/api/abs/check`, `/api/roadmap`,
`/api/compare`, `/api/analyze` (ephemeral document analysis, never added to the KB),
`/api/sources` (provenance registry), `/api/escalate`, `/api/export/pdf`, `/api/health`.

### Frontend
React 18 + Vite. A professional legal-tech UI: hero with the core guarantees, tabbed
sections (Assistant, Classify, ABS, Compare, Roadmap, Analyze, Sources), grounded chat
with clickable citations + source drawer + confidence/answer-mode/law-as-of badges,
per-answer disclaimer, escalation modal, query history (localStorage), PDF export,
jurisdiction toggle, language selector, and Sensitive-Invention mode.

## Provider tiers (graceful degradation)
| Capability | Live (key present) | Offline default | Deterministic test double |
|---|---|---|---|
| LLM | GeminiLLM | — | FakeLLM (grounded by construction) |
| Embeddings | GeminiEmbeddings | LocalEmbeddings (opt-in) | FakeEmbeddings |
| Translation | BhashiniTranslation | OfflineGlossaryTranslation | FakeTranslation |
| Vector store | Chroma (cosine) | InMemoryVectorStore | InMemoryVectorStore |

## Testing & evaluation
- Acceptance harness `tools/acceptance/T001..T035` (contracts, retrieval, rules,
  temporal, resilience, translation, search, hardening, upload, escalation, embeddings).
- `backend/tests/smoke_demo.py` — one-command end-to-end over every endpoint.
- `eval/run_eval.py` — Recall@k, citation validity, safe abstention, term preservation,
  latency; exits non-zero unless the gates hold.
- `frontend` — Vitest + React Testing Library, dependency-injected API.

## Deployment
`docker compose up --build`: backend image installs the live SDK and runs uvicorn with
`--proxy-headers`; the frontend is a multi-stage production build served by nginx that
proxies `/api` to the backend (same-origin, no CORS reliance). Corpus integrity is
verified at startup.

## Deliberately out of scope (future roadmap)
Relational knowledge graph + agentic multi-source orchestration; automated law-change
tracking / scrapers; paid-source connectors; full 22-language + voice; full TKDL access;
expert-panel benchmark and NLI entailment scoring.

## Known limitations
- Offline retrieval uses a deterministic fixture embedder unless `USE_LOCAL_EMBEDDINGS=1`
  (with `sentence-transformers` installed) or a Gemini key is provided.
- The corpus is a curated demonstration subset; breadth (case law, pharmacopoeia,
  registry records, plant-variety) is expandable via `corpus/manifest.json`.
- Live Gemini/Bhashini calls require a one-time spot-check after keys are added
  (`docs/REAL_API_SETUP.md`).
