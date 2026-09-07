"""build_app(): the ONE real entry point. Constructs real providers iff creds present,
else fixture-backed fakes, and injects the AnswerService.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.disclaimer import DisclaimerHeaderMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.config import Settings
from app.corpus.ingestion import ingest
from app.corpus.manifest import load_manifest
from app.retrieval.chunking import chunk_doc
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.keyword_index import BM25Index
from app.retrieval.vector_store import InMemoryVectorStore
from app.utils.logger import configure_logging
from app.workflow.pipeline import AnswerService

log = logging.getLogger("ipsakti")


def make_llm(settings: Settings):
    if settings.gemini_api_key:
        from app.integrations.gemini import GeminiLLM
        return GeminiLLM(settings.gemini_api_key)
    from app.integrations.fakes import FakeLLM
    log.info("LLM provider: fixture mode (no GEMINI_API_KEY)")
    return FakeLLM()


def make_embeddings(settings: Settings):
    if settings.gemini_api_key:
        from app.integrations.gemini import GeminiEmbeddings
        return GeminiEmbeddings(settings.gemini_api_key)
    from app.integrations.fakes import FakeEmbeddings
    log.info("Embedding provider: fixture mode")
    return FakeEmbeddings()


def make_translation(settings: Settings):
    if settings.bhashini_user_id and settings.bhashini_inference_key:
        from app.integrations.bhashini import BhashiniTranslation
        return BhashiniTranslation(
            settings.bhashini_user_id, settings.bhashini_ulca_key, settings.bhashini_inference_key
        )
    from app.i18n.offline_translator import OfflineGlossaryTranslation
    log.info("Translation provider: offline glossary mode (no Bhashini credentials)")
    return OfflineGlossaryTranslation()


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    app = FastAPI(title="IP-SAKTI Sahayak", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(DisclaimerHeaderMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        limit=int(os.getenv("RATE_LIMIT_PER_MIN", "300")),
        window_seconds=60,
    )

    llm = make_llm(settings)
    emb = make_embeddings(settings)
    translation = make_translation(settings)

    manifest = load_manifest(Path(settings.corpus_dir) / "manifest.json")
    docs = ingest(manifest, settings.corpus_dir)
    chunks = [c for d in docs for c in chunk_doc(d)]
    vs = InMemoryVectorStore()
    vs.add(emb.embed([c.text for c in chunks]), chunks)
    ki = BM25Index()
    ki.add(chunks)
    retriever = HybridRetriever(vs, ki, emb)

    app.state.settings = settings
    app.state.corpus_manifest = manifest
    app.state.providers = {"llm": llm, "embeddings": emb, "translation": translation}
    app.state.answer_service = AnswerService(
        retriever, llm, emb, settings.corpus_version, translation=translation
    )

    from app.api.routes import abs_check as abs_routes
    from app.api.routes import analyze as analyze_routes
    from app.api.routes import chat as chat_routes
    from app.api.routes import classify as classify_routes
    from app.api.routes import compare as compare_routes
    from app.api.routes import escalate as escalate_routes
    from app.api.routes import export as export_routes
    from app.api.routes import health as health_routes
    from app.api.routes import roadmap as roadmap_routes
    from app.api.routes import search as search_routes
    from app.api.routes import sources as sources_routes
    app.include_router(chat_routes.router)
    app.include_router(health_routes.router)
    app.include_router(abs_routes.router)
    app.include_router(classify_routes.router)
    app.include_router(roadmap_routes.router)
    app.include_router(compare_routes.router)
    app.include_router(export_routes.router)
    app.include_router(search_routes.router)
    app.include_router(sources_routes.router)
    app.include_router(analyze_routes.router)
    app.include_router(escalate_routes.router)
    return app

