"""PDF report built directly from a validated ChatResponse (no re-generation)."""
from __future__ import annotations

import io

from app.workflow.schema import ChatResponse

DISCLAIMER = "Informational guidance, not legal advice. Consult a qualified professional."


def build_report_text(resp: ChatResponse) -> str:
    lines = [
        "IP-SAKTI Sahayak - Report",
        f"Law as of: {resp.as_of}   Jurisdiction: {resp.jurisdiction.value}   Corpus: {resp.corpus_version}",
        f"Evidence strength: {resp.evidence_strength.value}   Mode: {resp.answer_mode.value}",
        "",
        "Answer:",
    ]
    if resp.claims:
        for c in resp.claims:
            lines.append(f"- {c.text}  {list(c.source_ids)}")
    else:
        lines.append("- (No citation-supported answer; see warnings.)")
    if resp.warnings:
        lines.append("")
        lines.append("Notes:")
        for w in resp.warnings:
            lines.append(f"- [{w.code}] {w.message}")
    lines.append("")
    lines.append("Sources:")
    for s in resp.sources:
        lines.append(f"- [{s.id}] {s.title} {s.section or ''} ({s.status.value}) {s.url or ''}")
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def _wrap(text: str, n: int = 95) -> list[str]:
    if not text:
        return [""]
    import textwrap
    return textwrap.wrap(text, width=n, break_long_words=True, break_on_hyphens=False) or [""]


def render_pdf(resp: ChatResponse) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    for line in build_report_text(resp).split("\n"):
        for chunk in _wrap(line):
            c.drawString(2 * cm, y, chunk)
            y -= 0.5 * cm
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
    c.showPage()
    c.save()
    return buf.getvalue()
