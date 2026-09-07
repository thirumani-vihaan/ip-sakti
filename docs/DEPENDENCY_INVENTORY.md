# DEPENDENCY_INVENTORY

Every external dependency, its gotchas, the injectable interface it sits behind, and its fixture folder. **All are testable offline** via fixture-backed fakes; a real credential/device is only needed for live mode.

## 1. Google Gemini — LLM (answer generation)
- **Purpose:** grounded answer generation from retrieved evidence IDs.
- **Credential:** `GEMINI_API_KEY` (free tier available, no card).
- **Gotchas:** free-tier RPM/RPD limits; **429 / rate-limit** handling with backoff; free tier is Flash models only; never send data in Sensitive-Invention mode.
- **Interface:** `LLMProvider` (real: `GeminiLLM`; fake: `FakeLLM`).
- **Fixtures:** `fixtures/llm/` — normal answers citing supplied IDs, refusals/abstentions, and error cases (timeout, 429, 5xx, malformed). `FakeLLM(force_error=...)`.
- **Offline behavior:** default fake unless `GEMINI_API_KEY` set; logs fixture mode.

## 2. Google Gemini — Embeddings
- **Purpose:** vector embeddings for semantic retrieval (`gemini-embedding-001`).
- **Credential:** `GEMINI_API_KEY` (same).
- **Gotchas:** dimension must match the Chroma collection; rate limits; batch calls.
- **Interface:** `EmbeddingProvider` (real: `GeminiEmbeddings`; fake: `FakeEmbeddings` = deterministic seeded vectors).
- **Fixtures:** `fixtures/embeddings/` — precomputed deterministic vectors for the sample corpus + queries, so retrieval tests are reproducible with no network.
- **Offline behavior:** deterministic fake; real path optional. `sentence-transformers` is the local *fallback* embedder (see #5).

## 3. Bhashini (ULCA) — Translation (Hindi / Telugu)
- **Purpose:** translate query in / answer out; preserve legal terms verbatim.
- **Credential:** `BHASHINI_USER_ID`, `BHASHINI_ULCA_API_KEY`, `BHASHINI_INFERENCE_API_KEY` (free govt platform; registration + email verify).
- **Gotchas:** **legal-term mistranslation risk** — statute names/section numbers must be preserved verbatim; abstain if translation changes a compliance input; voice (ASR/TTS) optional and behind a feature flag; email-verification delay on signup.
- **Interface:** `TranslationProvider` (real: `BhashiniTranslation`; fake: `FakeTranslation`).
- **Fixtures:** `fixtures/translation/` — EN↔HI, EN↔TE pairs incl. code-mixed / transliterated input and glossary-locked terms; error cases.
- **Offline behavior:** default fake; real path optional.

## 4. ChromaDB — Vector store
- **Purpose:** persist + query embeddings.
- **Credential:** none (local, `CHROMA_PERSIST_DIR`).
- **Gotchas:** support 0.5.x `PersistentClient` with `Settings(anonymized_telemetry=False)`, graceful fallback if the arg is unavailable; do NOT re-index at startup; verify count/hash on boot.
- **Interface:** `VectorStore` (wrapper; same interface for tests).
- **Fixtures:** built from the sample corpus + `FakeEmbeddings` at test setup (ephemeral persist dir).
- **Offline behavior:** fully local; no network.

## 5. sentence-transformers — Local embeddings / offline fallback
- **Purpose:** local embedder for the extractive fallback path (when Gemini is down) and offline dev.
- **Credential:** none.
- **Gotchas:** **first-run model download** — MUST be prewarmed in `tools/smoke_test_deps.py` (force download) so retrieval never fails mid-demo; cache dirs `HF_HOME` / `SENTENCE_TRANSFORMERS_HOME`; CPU-only torch may need the CPU wheel index.
- **Interface:** used behind `EmbeddingProvider` (local variant) and the fallback index.
- **Fixtures:** deterministic vectors preferred for tests; the real model is exercised only in the smoke test.
- **Offline behavior:** works offline once the model is cached.

## 6. BM25 (rank-bm25) — Keyword index
- **Purpose:** exact statute/section/form/act matching alongside vectors.
- **Credential:** none.
- **Gotchas:** tokenization must handle "Section 3(p)", "Form I", rule numbers; combine with vectors via reciprocal-rank fusion.
- **Interface:** `KeywordIndex`.
- **Fixtures:** built from the sample corpus at setup.
- **Offline behavior:** fully local.

## 7. Corpus documents (public legal sources)
- **Purpose:** the knowledge base — statutes, rules, guidelines, treaties.
- **Credential:** none (public), but must be fetched + provenance-tracked.
- **Sources:** India Code (Patents Act, Biological Diversity Act, TM/GI/Designs/Copyright, D&C, Magic Remedies), ipindia.gov.in, ayush.gov.in (guidelines), DPIIT TK & biological-material patent guidelines, WIPO (TRIPS, PCT). **TKDL full database is NOT publicly available — capability-gated; use only public overview + DPIIT guidelines.**
- **Gotchas:** licence field enforced (public-domain / government / open only); PDFs vary in structure (PyMuPDF) — hierarchy-aware chunking; record URL + hash + version + effective_date + authority.
- **Mechanism:** `scripts/fetch_corpus.py` builds the real corpus (its own commit, off the offline test path); offline tests use a small **committed sample fixture** under `corpus/` + `fixtures/corpus/`.
- **Offline behavior:** sample fixture only; real fetch is a separate, reviewable step.

## Credential summary (`.env`, all optional for offline tests)
`GEMINI_API_KEY`, `BHASHINI_USER_ID`, `BHASHINI_ULCA_API_KEY`, `BHASHINI_INFERENCE_API_KEY`, `CHROMA_PERSIST_DIR`, `HF_HOME`, `SENTENCE_TRANSFORMERS_HOME`, `LOG_LEVEL`. Setting them is the entire handoff to live mode; no code change required.
