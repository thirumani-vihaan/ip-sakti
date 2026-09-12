"""PDF report built directly from a validated ChatResponse (no re-generation)."""
from __future__ import annotations

import io
from app.workflow.schema import ChatResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

DISCLAIMER = "Informational guidance, not legal advice. Consult a qualified professional."


def build_report_text(resp: ChatResponse) -> str:
    """Plain-text rendering of a validated ChatResponse.

    Contains every claim, every cited source (id + title), the law-as-of date,
    the corpus version, and the standing disclaimer — the same content the PDF
    renders, in a form that is trivial to assert on and to embed as PDF text.
    """
    lines: list[str] = ["IP-SAKTI Legal Report", ""]
    lines.append(f"Law as of: {resp.as_of}")
    lines.append(f"Jurisdiction: {resp.jurisdiction.value.title()}")
    lines.append(f"Evidence strength: {resp.evidence_strength.value.title()}")
    lines.append(f"Answer mode: {resp.answer_mode.value.title()}")
    lines.append(f"Corpus version: {resp.corpus_version}")
    lines.append("")
    lines.append("Synthesized Guidance:")
    if resp.claims:
        for i, c in enumerate(resp.claims, 1):
            cites = f" (Sources: {', '.join(c.source_ids)})" if c.source_ids else ""
            lines.append(f"{i}. {c.text}{cites}")
    else:
        lines.append("(No citation-supported answer; see warnings.)")
    if resp.warnings:
        lines.append("")
        lines.append("System Warnings:")
        for w in resp.warnings:
            lines.append(f"- [{w.code}] {w.message}")
    if resp.sources:
        lines.append("")
        lines.append("Cited Sources:")
        for s in resp.sources:
            url = s.url or "No URL available"
            lines.append(f"- [{s.id}] {s.title} {s.section or ''} ({s.status.value.title()}) {url}")
    lines.append("")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def _header_footer(canvas, doc):
    canvas.saveState()
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.gray)
    canvas.drawCentredString(A4[0] / 2.0, 1 * cm, DISCLAIMER)
    canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()

def render_pdf(resp: ChatResponse) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2.5*cm)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    title_style.textColor = colors.HexColor('#335c45') # var(--primary)
    title_style.fontName = 'Times-Bold' # Match serif theme
    
    body_style = styles['Normal']
    body_style.fontSize = 11
    body_style.leading = 16

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=10
    )

    h2_style = styles['Heading2']
    h2_style.textColor = colors.HexColor('#7b5b19') # var(--accent-ink)
    h2_style.fontName = 'Times-Bold' # Match serif theme
    h2_style.spaceBefore = 20
    h2_style.spaceAfter = 10

    elements = []

    # Header
    elements.append(Paragraph("<b>IP-SAKTI Legal Report</b>", title_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#ba964b'), spaceAfter=20)) # var(--thread)

    # Metadata Table
    meta_data = [
        ['Law as of:', resp.as_of, 'Jurisdiction:', resp.jurisdiction.value.title()],
        ['Evidence:', resp.evidence_strength.value.title(), 'Mode:', resp.answer_mode.value.title()],
        ['Corpus Version:', resp.corpus_version, '', '']
    ]
    meta_table = Table(meta_data, colWidths=[3.5*cm, 4.5*cm, 3.5*cm, 4.5*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f6ee')), # var(--bg)
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#282c25')), # var(--ink)
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#deded0')), # var(--border)
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))

    # Answer Section
    elements.append(Paragraph("<b>Synthesized Guidance</b>", h2_style))
    
    if resp.claims:
        for i, c in enumerate(resp.claims, 1):
            source_text = f" <i>(Sources: {', '.join(c.source_ids)})</i>" if c.source_ids else ""
            elements.append(Paragraph(f"<b>{i}.</b> {c.text}{source_text}", bullet_style))
    else:
        elements.append(Paragraph("<i>(No citation-supported answer; see warnings.)</i>", body_style))

    # Warnings Section
    if resp.warnings:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>System Warnings</b>", h2_style))
        for w in resp.warnings:
            elements.append(Paragraph(f"• <b>[{w.code}]</b> {w.message}", bullet_style))

    # Sources Section
    if resp.sources:
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#ba964b'), spaceAfter=15)) # var(--thread)
        elements.append(Paragraph("<b>Cited Sources</b>", h2_style))
        for s in resp.sources:
            link = f'<a href="{s.url}" color="#335c45">{s.url}</a>' if s.url else "<i>No URL available</i>" # var(--primary)
            elements.append(Paragraph(f"• <b>[{s.id}] {s.title}</b> {s.section or ''} ({s.status.value.title()})<br/>{link}", bullet_style))

    # Build PDF
    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    
    return buf.getvalue()
