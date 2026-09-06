"""VectorStore: interface + an in-memory offline double + a real Chroma-backed impl.

The in-memory store is the deterministic offline double used by the test suite
(mock-first: Chroma is a dependency; InMemoryVectorStore is its fixture-equivalent).
ChromaVectorStore is the real persistent impl, lazily imported for live mode.
"""
from __future__ import annotations

from datetime import date
from typing import Optional, Protocol, runtime_checkable

from app.retrieval.chunking import Chunk
from app.workflow.schema import RetrievalHit, Source


def chunk_to_source(chunk: Chunk, as_of: Optional[date] = None) -> Source:
    return Source(
        id=chunk.id, title=chunk.title, section=chunk.section, url=chunk.url,
        local_excerpt=chunk.text, status=chunk.status, authority=chunk.authority_level,
        document_hash=chunk.document_hash, effective_date=chunk.effective_date,
        as_of=as_of or date.today(),
    )


def _cosine(a: list[float], b: list[float]) -> float:
    # FakeEmbeddings / real embeddings are L2-normalised, so dot == cosine.
    return sum(x * y for x, y in zip(a, b))


@runtime_checkable
class VectorStore(Protocol):
    def add(self, vectors: list[list[float]], chunks: list[Chunk]) -> None:
        ...

    def query(self, vector: list[float], k: int = 5, jurisdiction: Optional[str] = None) -> list[RetrievalHit]:
        ...


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._items: list[tuple[list[float], Chunk]] = []

    def add(self, vectors: list[list[float]], chunks: list[Chunk]) -> None:
        for v, c in zip(vectors, chunks):
            self._items.append((v, c))

    def query(self, vector: list[float], k: int = 5, jurisdiction: Optional[str] = None) -> list[RetrievalHit]:
        scored: list[tuple[float, Chunk]] = []
        for v, c in self._items:
            if jurisdiction and c.jurisdiction != jurisdiction:
                continue
            scored.append((_cosine(vector, v), c))
        # deterministic: score desc, then id asc for stable ties
        scored.sort(key=lambda x: (-x[0], x[1].id))
        return [
            RetrievalHit(evidence_id=c.id, text=c.text, score=float(s), source=chunk_to_source(c))
            for s, c in scored[:k]
        ]


class ChromaVectorStore:
    """Real persistent store (lazy import). Not exercised by the offline suite."""

    def __init__(self, persist_dir: str, collection: str = "ipsakti") -> None:
        import chromadb
        from chromadb.config import Settings
        try:
            self._client = chromadb.PersistentClient(
                path=persist_dir, settings=Settings(anonymized_telemetry=False)
            )
        except TypeError:
            self._client = chromadb.PersistentClient(path=persist_dir)
        self._col = self._client.get_or_create_collection(collection)
        self._meta: dict[str, Chunk] = {}

    def add(self, vectors: list[list[float]], chunks: list[Chunk]) -> None:
        self._col.add(
            ids=[c.id for c in chunks], embeddings=vectors,
            documents=[c.text for c in chunks],
            metadatas=[{"jurisdiction": c.jurisdiction} for c in chunks],
        )
        for c in chunks:
            self._meta[c.id] = c

    def query(self, vector: list[float], k: int = 5, jurisdiction: Optional[str] = None) -> list[RetrievalHit]:
        where = {"jurisdiction": jurisdiction} if jurisdiction else None
        res = self._col.query(query_embeddings=[vector], n_results=k, where=where)
        ids = (res.get("ids") or [[]])[0]
        dists = (res.get("distances") or [[None] * len(ids)])[0]
        hits: list[RetrievalHit] = []
        for i, cid in enumerate(ids):
            c = self._meta.get(cid)
            if c is None:
                continue
            dist = dists[i] if i < len(dists) and dists[i] is not None else 0.0
            hits.append(
                RetrievalHit(evidence_id=c.id, text=c.text, score=float(1.0 - dist),
                             source=chunk_to_source(c))
            )
        return hits
