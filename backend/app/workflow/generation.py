"""Grounded generation: build a prompt that exposes ONLY server-assigned evidence ids."""
from __future__ import annotations

from app.integrations.provider import LLMProvider
from app.workflow.schema import Claim, RetrievalHit


def build_prompt(query: str, evidence: list[RetrievalHit]) -> str:
    lines = [
        "You are a careful legal-information assistant for Ayurveda intellectual-property and regulatory questions.",
        "Answer the question directly and plainly, using ONLY the evidence passages below.",
        "Rules you must follow:",
        "- End every sentence that states a fact with its supporting id in [brackets]; cite ONLY the ids provided.",
        "- Write the substance directly. Never talk about the passages themselves: do not write 'the passages', 'the evidence', 'the documents', 'they mention', 'these sources', or anything similar.",
        "- Do not describe what the sources contain; answer the question itself.",
        "- If the evidence below does not actually answer the question, reply with exactly this token and nothing else: INSUFFICIENT_EVIDENCE",
        "- Be concise and neutral. This is informational guidance, not legal advice.",
        "",
        f"Question: {query}",
        "",
        "Evidence:",
    ]
    for h in evidence:
        lines.append(f"[{h.evidence_id}] ({h.source.title} {h.source.section or ''}): {h.text}")
    return "\n".join(lines)


def generate_grounded(llm: LLMProvider, query: str, evidence: list[RetrievalHit]) -> list[Claim]:
    if not evidence:
        return []
    return llm.generate(build_prompt(query, evidence), evidence)
