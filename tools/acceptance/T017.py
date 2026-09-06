"""T017 acceptance: statute/section refs preserved verbatim; glossary locked; altered ref -> raise."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


class _DropsSection:
    """A bad provider that silently drops a section reference."""

    def translate(self, text: str, src: str, tgt: str) -> str:
        return text.replace("Section 3(p)", "<omitted>")


def main() -> int:
    from app.i18n.glossary import glossary_for
    from app.i18n.translate import preserve_tokens, translate_preserving
    from app.integrations.fakes import FakeTranslation

    text = "Under Section 3(p), file Form I with the State Biodiversity Board."
    assert set(preserve_tokens(text)) == {"Section 3(p)", "Form I"}

    # good provider preserves statute/section tokens verbatim (hi + te)
    for tgt in ("hi", "te"):
        out = translate_preserving(FakeTranslation(), text, "en", tgt)
        assert "Section 3(p)" in out and "Form I" in out, f"tokens lost in {tgt}: {out}"

    # glossary is populated and locked for both language pairs
    assert glossary_for("en", "hi")["traditional knowledge"] == "paramparagat gyaan"
    assert "biological resource" in glossary_for("en", "te")

    # a translation that alters a compliance-critical reference is rejected
    try:
        translate_preserving(_DropsSection(), text, "en", "hi")
        raise AssertionError("altered section reference should have raised")
    except ValueError:
        pass

    print("T017 OK: statute/section refs preserved; glossary locked; altered ref rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
