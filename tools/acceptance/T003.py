"""T003 acceptance: manifest loads with provenance; ingest produces docs; licence enforced."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.ingestion import ingest
    from app.corpus.manifest import ManifestEntry, load_manifest

    entries = load_manifest(CORPUS / "manifest.json")
    assert len(entries) >= 3, "sample manifest should have >= 3 entries"
    for e in entries:
        assert e.url and e.publisher and e.version and e.license and e.authority_level, "missing provenance"

    docs = ingest(entries, CORPUS)
    assert len(docs) == len(entries)
    for d in docs:
        assert d.text.strip(), f"empty text for {d.id}"
        assert d.document_hash.startswith("sha256:"), "content hash required"
        assert d.license in {"public-domain", "government", "open"}

    # licence enforcement: a disallowed licence must be rejected at construction
    try:
        ManifestEntry(
            id="x", title="t", url="u", publisher="p", version="v", path="p.txt",
            document_hash="h", status="in_force", authority_level="statute",
            license="proprietary", jurisdiction="india",
        )
        raise AssertionError("proprietary licence should have been rejected")
    except ValueError:
        pass

    print(f"T003 OK: {len(docs)} docs ingested with provenance; licence enforced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
