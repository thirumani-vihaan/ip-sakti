"""Rule DSL: a versioned, source-citing rule and a bundled rule set."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Rule(BaseModel):
    id: str
    when: dict[str, Any]  # fact -> required value (all must match)
    obligation: str
    authority: str = ""
    forms: list[str] = []
    source_id: str
    rule_version: str


class RuleSet(BaseModel):
    name: str
    rules: list[Rule]
    required: list[str]  # facts that must be provided or the engine asks
    default_source: str
    default_version: str
    default_obligation: str = "No specific obligation identified for the provided facts."


def matches(rule: Rule, facts: dict) -> bool:
    return all(facts.get(k) == v for k, v in rule.when.items())
