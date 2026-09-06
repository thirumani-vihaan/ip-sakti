"""Legal-aware chunking: split on section boundaries; keep provisos/explanations with parent.

Each chunk carries enough provenance to become a Source (the retrieval/evidence unit).
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.corpus.ingestion import RawDoc

_SECTION_RE = re.compile(r"Section\s+(\d+[A-Za-z]*(?:\([a-z0-9]+\))?)", re.I)
_KEEP_WITH_PARENT = re.compile(r"^\s*(Provided|Explanation|Illustration)\b", re.I)


class Chunk(BaseModel):
    id: str  # evidence id, e.g. "patents_1970_s3p#c0"
    doc_id: str
    title: str
    section: Optional[str]
    text: str
    jurisdiction: str
    authority_level: str
    status: str
    url: str
    document_hash: str
    effective_date: Optional[date] = None


def _paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _mk(doc: RawDoc, section: Optional[str], text: str, n: int) -> Chunk:
    return Chunk(
        id=f"{doc.id}#c{n}", doc_id=doc.id, title=doc.title, section=section, text=text,
        jurisdiction=doc.jurisdiction, authority_level=doc.authority_level,
        status=doc.status, url=doc.url, document_hash=doc.document_hash,
        effective_date=doc.effective_date,
    )


def chunk_doc(doc: RawDoc, max_chars: int = 1200) -> list[Chunk]:
    # 1) group paragraphs into (section, paras); provisos/explanations stay with their parent
    segments: list[tuple[Optional[str], list[str]]] = []
    cur_section: Optional[str] = None
    cur: list[str] = []
    for para in _paragraphs(doc.text):
        m = _SECTION_RE.search(para)
        if m and not _KEEP_WITH_PARENT.match(para):
            if cur:
                segments.append((cur_section, cur))
            cur_section = m.group(1)
            cur = [para]
        else:
            cur.append(para)
    if cur:
        segments.append((cur_section, cur))
    if not segments:
        segments = [(None, _paragraphs(doc.text) or [doc.text.strip()])]

    # 2) pack each segment into <= max_chars chunks, never splitting a proviso off its clause
    chunks: list[Chunk] = []
    n = 0
    for section, paras in segments:
        buf: list[str] = []
        size = 0
        for para in paras:
            if buf and size + len(para) > max_chars and not _KEEP_WITH_PARENT.match(para):
                chunks.append(_mk(doc, section, "\n\n".join(buf), n))
                n += 1
                buf, size = [], 0
            buf.append(para)
            size += len(para)
        if buf:
            chunks.append(_mk(doc, section, "\n\n".join(buf), n))
            n += 1
    return chunks
