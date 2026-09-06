"""Corpus ingestion: manifest entries -> raw documents with a content hash.

Text/markdown are read directly. HTML (bs4) and PDF (PyMuPDF) are imported lazily
so the offline sample suite (plain .txt) needs neither installed.
"""
from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from app.corpus.manifest import ManifestEntry


class RawDoc(BaseModel):
    id: str
    title: str
    text: str
    jurisdiction: str
    authority_level: str
    license: str
    status: str
    url: str
    document_hash: str
    effective_date: Optional[date] = None


def _extract(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8")
    if suffix in (".html", ".htm"):
        from bs4 import BeautifulSoup  # lazy
        return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser").get_text(" ", strip=True)
    if suffix == ".pdf":
        import fitz  # PyMuPDF, lazy
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    raise ValueError(f"unsupported corpus file type: {suffix}")


def ingest(entries: list[ManifestEntry], base_dir: str | Path) -> list[RawDoc]:
    base = Path(base_dir)
    docs: list[RawDoc] = []
    for e in entries:
        text = _extract(base / e.path)
        if not text.strip():
            raise ValueError(f"empty document for manifest id {e.id}")
        content_hash = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
        if e.document_hash and e.document_hash not in ("sample", content_hash):
            raise ValueError(
                f"corpus hash mismatch for {e.id}: manifest={e.document_hash} computed={content_hash}"
            )
        docs.append(
            RawDoc(
                id=e.id, title=e.title, text=text,
                jurisdiction=e.jurisdiction.value, authority_level=e.authority_level,
                license=e.license, status=e.status.value, url=e.url,
                document_hash=content_hash, effective_date=e.effective_date,
            )
        )
    return docs
