"""T004 acceptance: chunks keep section context; provisos stay with parent; provenance carried."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.retrieval.chunking import chunk_doc
    from app.corpus.ingestion import RawDoc, ingest
    from app.corpus.manifest import load_manifest

    docs = {d.id: d for d in ingest(load_manifest(CORPUS / "manifest.json"), CORPUS)}

    pc = chunk_doc(docs["patents_1970_s3p"])
    assert pc and pc[0].section == "3(p)", f"expected section 3(p), got {pc[0].section if pc else None}"
    assert "traditional knowledge" in pc[0].text.lower()

    bc = chunk_doc(docs["bda_2002_s7"])
    assert bc[0].section == "7"
    assert "form i" in bc[0].text.lower() and "state biodiversity board" in bc[0].text.lower()

    # multi-section synthetic: proviso stays with its parent; two sections -> two chunks
    syn = RawDoc(
        id="syn", title="Syn",
        text="Section 3(p). TK is barred.\n\nProvided that exceptions apply.\n\nSection 4. Novelty is required.",
        jurisdiction="india", authority_level="statute", license="government",
        status="in_force", url="u", document_hash="h",
    )
    cs = chunk_doc(syn)
    assert len(cs) == 2, f"expected 2 chunks, got {len(cs)}"
    assert cs[0].section == "3(p)" and "provided" in cs[0].text.lower(), "proviso must stay with parent"
    assert cs[1].section == "4"

    for c in pc + bc + cs:
        assert c.id and c.doc_id and c.document_hash, "chunk must carry provenance"

    print("T004 OK: legal-aware chunking keeps section context + provisos with parent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
