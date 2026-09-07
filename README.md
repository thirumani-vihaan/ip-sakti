# IP-SAKTI Sahayak

A multilingual, citation-grounded AI assistant for Intellectual Property and
regulatory guidance in Ayurveda - covering national and international regimes.
Smart India Hackathon 2026 - Ministry of AYUSH.

> Status: working prototype. Backend + frontend implemented and tested; runs fully
> offline with no API keys. Add Gemini and/or Bhashini keys later to upgrade quality
> without any code change.

## What it does
Brings IP, traditional-knowledge (TK) risk, ABS (Access and Benefit-Sharing),
regulatory classification, and key international pathways into one guided,
citation-grounded workflow. Every answer maps to an official source the user can
open and verify. It is informational guidance, not legal advice.

## Core guarantees (the four evaluation axes)
- No claim without a validated citation - the model can only cite retrieved,
  server-assigned evidence ids and never invents a source.
- Current law by default, with a visible "law as of" date and in-force filtering.
- Fails safe - abstains with a confidence flag instead of guessing.
- Multilingual delivery with statute/section references preserved verbatim.

Measured on the bundled eval set (`python eval/run_eval.py`, 18 curated cases):
Recall@5 = 1.00, Citation validity = 1.00, Safe abstention = 1.00, term
preservation = pass. Numbers are reproducible offline.

## Features
- Grounded chat with clickable citations, a source drawer, an evidence-strength
  confidence indicator, answer-mode and law-as-of badges, and a standing
  disclaimer on every answer.
- Jurisdiction toggle (India vs International) with answer-sets kept visibly
  separate; a side-by-side compare tool.
- Formulation classifier (classical, proprietary, phytopharmaceutical, new drug,
  nutraceutical, cosmetic) that asks only the minimum questions needed.
- ABS compliance helper and a DPIIT/TKDL prior-art pointer.
- Escalate-to-a-human-IP-facilitator path on low-confidence / out-of-scope answers.
- Document upload -> ephemeral analysis against the trusted corpus (never added to
  the knowledge base).
- IP roadmap, source/provenance registry, PDF export, and query history.
- Multilingual (EN / HI / TE): full neural translation via Bhashini when
  configured, otherwise an offline glossary translator that localises legal terms
  and preserves statute references.
- Guardrails: input sanitization, per-IP rate limiting, always-on disclaimer +
  request-id headers, structured logging, and no user accounts (privacy by design).

## Architecture
React + Vite frontend; FastAPI backend; hybrid retrieval (in-memory vector store +
BM25, reciprocal-rank fusion; Chroma available for persistence) over a version-tracked
corpus with provenance hashes; a deterministic, source-citing rule engine (ABS +
classification); grounded generation with a citation validator; circuit-breaker +
extractive fallback. Providers are swapped in only when their credentials are present.

## Runs with no keys
The whole system - retrieval, grounding, abstention, rules, multilingual glossary,
every endpoint - runs offline on fixtures with no Gemini and no Bhashini key.
Keys are optional and additive:
- `GEMINI_API_KEY` -> real LLM synthesis + embeddings (else fixture LLM/embeddings).
- `BHASHINI_USER_ID` + `BHASHINI_INFERENCE_API_KEY` -> full neural translation
  (else the offline glossary translator). See `docs/REAL_API_SETUP.md`.

## Quickstart
Backend:
```
cd backend
python -m venv venv && venv\Scripts\activate      # Windows
pip install -r requirements.txt                    # core (offline)
pip install -r requirements-real.txt               # optional: live-mode SDKs
uvicorn app.main:build_app --factory --host 0.0.0.0 --port 8000
```
Frontend:
```
cd frontend
npm ci
npm run dev        # dev server
```
Docker (full stack):
```
docker compose up --build
```

## Testing
```
# backend acceptance suite (33 checks, offline)
cd backend
python ..\tools\run_acceptance.py T001            # run any T0XX
python tests\smoke_demo.py                         # one-command end-to-end
python ..\eval\run_eval.py                         # eval metrics + gates
# frontend
cd frontend && npm test
```

## API endpoints
`POST /api/chat`, `GET /api/search`, `POST /api/classify`, `POST /api/abs/check`,
`POST /api/roadmap`, `POST /api/compare`, `POST /api/analyze`, `GET /api/sources`,
`POST /api/escalate`, `POST /api/export/pdf`, `GET /api/health`.

## Documentation
- `docs/IMPLEMENTATION_PLAN.md` - full technical plan.
- `docs/REAL_API_SETUP.md` - enabling live Gemini / Bhashini.
- `docs/ARCHITECTURE.md`, `docs/INTERFACES.md`, `docs/RISK_LOG.md`,
  `docs/FINAL_REPORT.md`.

## License / data
Only public-domain, government, or open-licensed legal sources are used, each with
provenance in `corpus/manifest.json`. The full TKDL database is not publicly
available and is not used; TK checks are pointers for expert review, not clearance.
