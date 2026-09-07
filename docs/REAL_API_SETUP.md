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


## Running the server (local)
```bash
cd backend
python -m pip install -r requirements.txt          # core (now includes uvicorn)
python -m pip install -r requirements-real.txt      # live-mode SDKs (Gemini)
# put GEMINI_API_KEY in the environment (or backend/.env and export it):
export GEMINI_API_KEY=your_key_here                 # PowerShell: $env:GEMINI_API_KEY='your_key'
uvicorn app.main:build_app --factory --host 0.0.0.0 --port 8000
```
A live key yields `answer_mode: "live"` on `POST /api/chat`; with no key the server runs in offline fixture mode.

## Running with Docker
```bash
export GEMINI_API_KEY=your_key_here      # optional; omit to run offline
docker compose up --build
```
The backend image installs the Gemini SDK, and `docker-compose.yml` passes `GEMINI_API_KEY` (and the `BHASHINI_*` vars) through from your shell. CORS is enabled so the frontend at `:5173` can call the API.

## Optional: offline semantic embeddings (no key)
For better offline retrieval without any API key, enable a local model:

```bash
pip install sentence-transformers
# then start the backend with:
USE_LOCAL_EMBEDDINGS=1 uvicorn app.main:build_app --factory   # PowerShell: $env:USE_LOCAL_EMBEDDINGS='1'
```

When the flag is set and the package is installed, retrieval uses `all-MiniLM-L6-v2` locally; otherwise it falls back to the deterministic fixture embedder. A `GEMINI_API_KEY` always takes precedence.

