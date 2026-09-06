"""Multi-label domain routing with mandatory triggers and budget-based disclosure.

- classify(): heuristic multi-label domain detection,
- an ABS mandatory trigger (biological resource + commercial use always -> ABS),
- route(): keep top domains within a latency budget but ALWAYS keep mandatory ones,
  and disclose any domain left unevaluated as a warning (never silently omit).
"""
from __future__ import annotations

from app.models.enums import Domain
from app.workflow.schema import Warning

_KEYWORDS: dict[Domain, list[str]] = {
    Domain.PATENT: ["patent", "invention", "novelty", "3(p)", "patentable"],
    Domain.GI_TRADEMARK: ["geographical indication", "gi ", "trademark", "brand", "logo", "design", "copyright"],
    Domain.ABS: ["biological resource", "biodiversity", "benefit sharing", "nba", "sbb", "access and benefit"],
    Domain.REGULATORY: ["licence", "license", "drug", "cosmetic", "nutraceutical", "fssai", "ayush", "advertis", "label"],
    Domain.TK_RISK: ["traditional knowledge", "tkdl", "prior art", "classical text", "charaka", "sushruta"],
    Domain.INTERNATIONAL: ["pct", "trips", "wipo", "export", "madrid", "international", "nagoya"],
}

_PRIORITY = [
    Domain.ABS, Domain.PATENT, Domain.TK_RISK,
    Domain.REGULATORY, Domain.GI_TRADEMARK, Domain.INTERNATIONAL,
]

_BIO = ["biological resource", "biodiversity", "plant", "herb", "botanical"]
_COMMERCIAL = ["commercial", "sell", "export", "market"]


def abs_triggered(query: str) -> bool:
    q = query.lower()
    return any(b in q for b in _BIO) and any(c in q for c in _COMMERCIAL)


def classify(query: str) -> set[Domain]:
    q = query.lower()
    labels = {d for d, kws in _KEYWORDS.items() if any(k in q for k in kws)}
    if abs_triggered(query):
        labels.add(Domain.ABS)
    return labels


def route(query: str, budget: int = 2) -> tuple[list[Domain], list[Warning]]:
    labels = classify(query)
    ordered = [d for d in _PRIORITY if d in labels]
    mandatory = [Domain.ABS] if (Domain.ABS in labels and abs_triggered(query)) else []
    selected = list(dict.fromkeys(mandatory + ordered))
    keep = selected[: max(budget, len(mandatory))]
    unevaluated = [d for d in selected if d not in keep]
    warnings = [
        Warning(code="domain_not_evaluated",
                message=f"Domain '{d.value}' not evaluated (scope/latency budget); ask to include it.")
        for d in unevaluated
    ]
    return keep, warnings
