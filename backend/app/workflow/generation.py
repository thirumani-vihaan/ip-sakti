"""Grounded generation: build a prompt that exposes ONLY server-assigned evidence ids."""
from __future__ import annotations

from app.integrations.provider import LLMProvider
from app.workflow.schema import Claim, RetrievalHit


def build_prompt(query: str, evidence: list[RetrievalHit]) -> str:
    lines = [
        "You are a careful legal-information assistant.",
        "Answer ONLY using the evidence passages below; cite each passage by its id in [brackets].",
        "You may cite ONLY the ids provided. If the evidence does not support an answer, say you cannot answer.",
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
