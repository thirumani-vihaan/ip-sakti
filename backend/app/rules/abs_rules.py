"""ABS (Access and Benefit Sharing) obligation rules — Biological Diversity Act 2002 (amended)."""
from __future__ import annotations

from app.rules.dsl import Rule, RuleSet

_REQUIRED = ["resource_origin", "use", "applicant", "tk_association"]
_VERSION = "2024.1"

ABS = RuleSet(
    name="abs",
    required=_REQUIRED,
    default_source="bda_2002_s7",
    default_version=_VERSION,
    default_obligation="No specific ABS obligation identified; verify with the SBB/NBA.",
    rules=[
        Rule(
            id="abs_commercial_indian_entity",
            when={"resource_origin": "india", "use": "commercial", "applicant": "indian_entity"},
            obligation="Give prior intimation to the State Biodiversity Board (SBB) before commercial utilisation.",
            authority="State Biodiversity Board", forms=["Form I"],
            source_id="bda_2002_s7", rule_version=_VERSION,
        ),
        Rule(
            id="abs_commercial_foreign",
            when={"resource_origin": "india", "use": "commercial", "applicant": "foreign"},
            obligation="Obtain prior approval of the National Biodiversity Authority (NBA) before commercial utilisation.",
            authority="National Biodiversity Authority", forms=["Form II"],
            source_id="bda_2002_s3", rule_version=_VERSION,
        ),
        Rule(
            id="abs_research_foreign",
            when={"resource_origin": "india", "use": "research", "applicant": "foreign"},
            obligation="Obtain prior approval of the NBA for research access to Indian biological resources.",
            authority="National Biodiversity Authority", forms=["Form III"],
            source_id="bda_2002_s3", rule_version=_VERSION,
        ),
    ],
)
