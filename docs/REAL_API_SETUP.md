# Going live (REAL_API_SETUP)

The whole test suite runs offline with **no credentials** (fixture-backed fakes).
Setting the environment variables below is the *entire* handoff to live mode — **no code change is required**.

Copy `.env.example` to `.env` (never commit `.env`) and fill in:

| Variable | Purpose | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Real LLM generation + embeddings | Google AI Studio (aistudio.google.com) — free tier, no card. When set, `GeminiLLM` + `GeminiEmbeddings` replace the fakes automatically. |
| `BHASHINI_USER_ID` | Hindi/Telugu translation | Bhashini ULCA portal (bhashini.gov.in/ulca/user/register) — register + verify email. |
| `BHASHINI_ULCA_API_KEY` | Bhashini auth | Bhashini profile → Generate API key. |
| `BHASHINI_INFERENCE_API_KEY` | Bhashini inference | Bhashini profile → Inference key. When user-id + inference key are set, `BhashiniTranslation` replaces the fake. |
| `CHROMA_PERSIST_DIR` | Vector store persist dir | Local path (default `./data/chroma_db`). |
| `HF_HOME`, `SENTENCE_TRANSFORMERS_HOME` | Local embedding cache | Local path; prewarmed by the smoke test. |
| `CORPUS_DIR` | Corpus location | Defaults to `./corpus`; the Docker image sets `/app/corpus`. |
| `LOG_LEVEL` | Logging | `INFO` |

## Live spot-checks (after keys are set)
These paths are exercised by fakes offline; verify them once live:
- **Gemini**: `POST /api/chat` returns a synthesized (not extractive) answer with `answer_mode: "live"`.
- **Bhashini**: a Hindi/Telugu query preserves statute/section references verbatim (the `translate_preserving` guard raises on any altered reference).

## Provider selection (automatic, in `app/main.py :: build_app`)
- `GEMINI_API_KEY` present → `GeminiLLM` + `GeminiEmbeddings`; else fakes.
- `BHASHINI_USER_ID` + `BHASHINI_INFERENCE_API_KEY` present → `BhashiniTranslation`; else fake.
Fixture mode is logged clearly so it never silently pretends to be live.

## Install live-mode SDKs
The offline core excludes heavy SDKs. Before using real keys, install them:

```bash
pip install -r backend/requirements-real.txt
```

Current default models: LLM `gemini-flash-latest`, embeddings `gemini-embedding-001` (set in `app/integrations/gemini.py`).

