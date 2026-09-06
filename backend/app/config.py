"""Settings + real-vs-fake decision inputs."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_CORPUS = str(Path(__file__).resolve().parents[2] / "corpus")


@dataclass
class Settings:
    gemini_api_key: str | None = None
    bhashini_user_id: str | None = None
    bhashini_ulca_key: str | None = None
    bhashini_inference_key: str | None = None
    corpus_dir: str = _DEFAULT_CORPUS
    corpus_version: str = "v0"

    @classmethod
    def from_env(cls) -> "Settings":
        def g(k: str) -> str | None:
            return os.getenv(k) or None

        return cls(
            gemini_api_key=g("GEMINI_API_KEY"),
            bhashini_user_id=g("BHASHINI_USER_ID"),
            bhashini_ulca_key=g("BHASHINI_ULCA_API_KEY"),
            bhashini_inference_key=g("BHASHINI_INFERENCE_API_KEY"),
            corpus_dir=os.getenv("CORPUS_DIR", _DEFAULT_CORPUS),
            corpus_version=os.getenv("CORPUS_VERSION", "v0"),
        )
