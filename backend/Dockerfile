FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt backend/requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Live-mode SDK (used only when GEMINI_API_KEY is provided at runtime; harmless otherwise):
RUN pip install --no-cache-dir google-generativeai==0.8.6

COPY backend/app ./app
COPY corpus ./corpus

ENV CORPUS_DIR=/app/corpus
EXPOSE 8000
# build_app is a factory; verify corpus integrity at startup happens inside build_app's ingest.
CMD ["uvicorn", "app.main:build_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]


