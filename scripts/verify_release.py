"""Release integrity: load + ingest + chunk the corpus, verify it is non-empty, print a release hash."""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import load_manifest
    from app.retrieval.chunking import chunk_doc

    corpus = ROOT / "corpus"
    docs = ingest(load_manifest(corpus / "manifest.json"), corpus)
    chunks = [c for d in docs for c in chunk_doc(d)]
    assert docs and chunks, "corpus is empty"

    h = hashlib.sha256()
    for c in sorted(chunks, key=lambda x: x.id):
        h.update(f"{c.id}:{c.document_hash}".encode("utf-8"))
    print(f"corpus OK: {len(docs)} docs, {len(chunks)} chunks, release-hash {h.hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
