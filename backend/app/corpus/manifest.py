"""Versioned corpus manifest with provenance + licence enforcement."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.enums import ForceState, Jurisdiction

ALLOWED_LICENSES = {"public-domain", "government", "open"}
ALLOWED_AUTHORITY = {"statute", "rule", "notification", "guideline", "treaty", "article"}


class ManifestEntry(BaseModel):
    id: str
    title: str
    url: str
    publisher: str
    version: str
    path: str  # relative to the corpus base dir
    document_hash: str
    status: ForceState
    authority_level: str
    license: str
    jurisdiction: Jurisdiction
    effective_date: Optional[date] = None
    domains: list[str] = []

    @field_validator("license")
    @classmethod
    def _license_allowed(cls, v: str) -> str:
        if v not in ALLOWED_LICENSES:
            raise ValueError(f"license '{v}' not allowed (only {sorted(ALLOWED_LICENSES)})")
        return v

    @field_validator("authority_level")
    @classmethod
    def _authority_allowed(cls, v: str) -> str:
        if v not in ALLOWED_AUTHORITY:
            raise ValueError(f"authority_level '{v}' not allowed")
        return v


def load_manifest(path: str | Path) -> list[ManifestEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [ManifestEntry(**entry) for entry in data]
