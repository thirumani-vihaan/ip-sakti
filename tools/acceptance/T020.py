"""T020 acceptance: PDF built from the validated ChatResponse; contains claims/sources/law-as-of/disclaimer."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app
    from app.utils.pdf_generator import build_report_text, render_pdf
    from app.workflow.schema import ChatResponse

    client = TestClient(build_app(Settings()))
    resp_json = client.post("/api/chat", json={
        "query": "Under Section 3(p), can I patent a traditional formulation?"
    }).json()
    resp = ChatResponse.model_validate(resp_json)

    text = build_report_text(resp)
    for c in resp.claims:
        assert c.text in text, "every claim must appear in the report"
    for s in resp.sources:
        assert s.id in text and s.title in text, "every source must appear in the report"
    assert str(resp.as_of) in text, "law-as-of must be in the report"
    assert resp.corpus_version in text
    assert "not legal advice" in text.lower(), "disclaimer required"

    pdf = render_pdf(resp)
    assert pdf[:4] == b"%PDF" and len(pdf) > 500, "must produce a valid PDF"

    er = client.post("/api/export/pdf", json=resp_json)
    assert er.status_code == 200
    assert er.headers["content-type"].startswith("application/pdf")
    assert er.content[:4] == b"%PDF"

    print("T020 OK: PDF from validated response; claims/sources/law-as-of/disclaimer present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
