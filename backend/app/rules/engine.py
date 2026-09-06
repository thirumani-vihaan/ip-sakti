"""Deterministic rule engine: same facts -> same RuleResult; asks when required facts are missing."""
from __future__ import annotations

from app.rules.dsl import RuleSet, matches
from app.workflow.schema import RuleResult


def evaluate(ruleset: RuleSet, facts: dict) -> RuleResult:
    missing = [f for f in ruleset.required if facts.get(f) in (None, "")]
    if missing:
        return RuleResult(status="insufficient", missing=missing)
    for r in ruleset.rules:  # first match wins (rule order is significant + tested)
        if matches(r, facts):
            return RuleResult(
                obligation=r.obligation, authority=r.authority, forms=list(r.forms),
                source_id=r.source_id, rule_version=r.rule_version, status="decided",
            )
    return RuleResult(
        obligation=ruleset.default_obligation, authority="",
        source_id=ruleset.default_source, rule_version=ruleset.default_version, status="decided",
    )
