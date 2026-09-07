"""T039 acceptance: every deterministic rule cites a corpus id that actually exists."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
CORPUS = pathlib.Path(__file__).resolve().parents[2] / "corpus"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.corpus.manifest import load_manifest
    from app.rules.abs_rules import ABS
    from app.rules.classification_rules import CLASSIFICATION

    ids = {e.id for e in load_manifest(CORPUS / "manifest.json")}
    for rs in (ABS, CLASSIFICATION):
        used = {r.source_id for r in rs.rules} | {rs.default_source}
        missing = used - ids
        assert not missing, f"rule set '{rs.name}' cites unknown corpus sources: {sorted(missing)}"

    # the specific IDs the reviewer flagged now resolve
    assert "bda_2002_s3" in ids and "dc_act_1940_ayush" in ids

    print("T039 OK: all ABS + classification rule source_ids resolve to real corpus documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
