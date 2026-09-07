"""T026 acceptance: offline glossary translation localises legal terms, preserves refs, EN passthrough."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.i18n.offline_translator import OfflineGlossaryTranslation
    from app.i18n.translate import translate_preserving
    from app.integrations.provider import TranslationProvider

    tr = OfflineGlossaryTranslation()
    assert isinstance(tr, TranslationProvider), "must satisfy the TranslationProvider protocol"

    text = "Under Section 3(p), traditional knowledge and biological resource use needs prior approval."

    for tgt, term in (("hi", "paramparagat gyaan"), ("te", "sampradaaya gnyaanam")):
        out = tr.translate(text, "en", tgt)
        assert term in out, f"glossary term not localised for {tgt}: {out}"
        assert "Section 3(p)" in out, f"statute reference must be preserved verbatim in {tgt}"
        assert "traditional knowledge" not in out, "source term should have been replaced"

    # same-language and unknown-pair are safe passthroughs
    assert tr.translate("hello world", "en", "en") == "hello world"
    assert tr.translate("hello", "en", "zz") == "hello"

    # wrapped by translate_preserving: a preserved ref that survives does not raise
    guarded = translate_preserving(tr, text, "en", "hi")
    assert "Section 3(p)" in guarded

    print("T026 OK: offline glossary translation localises terms, preserves refs, safe passthrough")
    return 0


if __name__ == "__main__":
    sys.exit(main())
