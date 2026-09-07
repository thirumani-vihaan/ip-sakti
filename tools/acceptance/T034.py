"""T034 acceptance: optional local-embeddings tier degrades gracefully when unavailable."""
import os
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.config import Settings
    from app.integrations.local_embeddings import sentence_transformers_available
    from app.main import make_embeddings

    # opt-in flag set, but if the heavy package is absent we must fall back to fixtures
    os.environ["USE_LOCAL_EMBEDDINGS"] = "1"
    try:
        emb = make_embeddings(Settings())
    finally:
        os.environ.pop("USE_LOCAL_EMBEDDINGS", None)

    if sentence_transformers_available():
        assert type(emb).__name__ == "LocalEmbeddings", type(emb).__name__
    else:
        assert type(emb).__name__ == "FakeEmbeddings", type(emb).__name__

    # default (flag unset) always uses the deterministic fixture offline
    assert type(make_embeddings(Settings())).__name__ == "FakeEmbeddings"

    print("T034 OK: local-embeddings tier is opt-in and degrades to fixtures when unavailable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
