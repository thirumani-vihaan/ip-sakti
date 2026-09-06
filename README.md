# IP-SAKTI Sahayak

A multilingual, citation-backed AI assistant for Intellectual Property and
regulatory guidance in Ayurveda - national and international regimes.
Smart India Hackathon 2026 - Problem Statement 45 - Ministry of AYUSH.

> Status: scaffolded, not yet implemented. The build follows `docs/BUILD_LOOP.md`.

## What it does
Brings IP, traditional-knowledge risk, ABS (Access-and-Benefit-Sharing),
regulatory classification, and key international pathways into one guided,
citation-grounded workflow. Every answer maps to an official source the user can
open and verify. It is informational guidance, not legal advice.

## Core guarantees
- No claim without a validated citation (the model cannot invent sources).
- Current law by default, with a visible "law as of" date.
- Fails safe (abstains) instead of guessing.
- Deterministic, reproducible compliance logic (ABS + classification).
- Offline-capable: returns an extractive, still-cited answer if the LLM is down.

## Documentation
- `docs/IMPLEMENTATION_PLAN.md` - the full technical plan (architecture, schemas,
  domain coverage, phases, deployment).
- `docs/BUILD_LOOP.md` - the industry-grade autonomous build loop this project
  follows (mock-first, per-feature commit + push, measured improvement loop).

## Tech stack
React + Vite (frontend) - FastAPI (backend) - Chroma + BM25 hybrid retrieval -
deterministic rule engine - Google Gemini (LLM + embeddings, with local
extractive fallback) - Bhashini (Hindi/Telugu).

## Setup (once building starts)
1. Copy `.env.example` to `.env` and fill in keys (all optional for offline
   tests - the suite runs fully on fixtures with no keys).
2. Backend: create a venv, install `requirements.txt`.
3. Frontend: `npm ci`.
4. `docker compose up` for the full stack.

## License / data
Only public-domain, government, or open-licensed legal sources are ingested.
The full TKDL database is not publicly available and is not used.
