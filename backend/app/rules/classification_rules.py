"""Formulation classification rules (Drugs & Cosmetics Act, AYUSH provisions + FSSAI)."""
from __future__ import annotations

from app.rules.dsl import Rule, RuleSet

_REQUIRED = ["in_first_schedule", "modified", "novel_actives", "intended_use"]
_VERSION = "2024.1"

CLASSIFICATION = RuleSet(
    name="classification",
    required=_REQUIRED,
    default_source="dc_act_1940_ayush",
    default_version=_VERSION,
    default_obligation="Unclassified formulation; consult the AYUSH licensing authority.",
    rules=[
        Rule(
            id="classical",
            when={"in_first_schedule": "yes", "modified": "exact"},
            obligation="Classical Ayurvedic drug (First-Schedule text, unmodified); licensed as an Ayurvedic drug.",
            authority="AYUSH Licensing Authority", source_id="dc_act_1940_ayush", rule_version=_VERSION,
        ),
        Rule(
            id="proprietary",
            when={"in_first_schedule": "yes", "modified": "modified", "novel_actives": "no"},
            obligation="Proprietary Ayurvedic medicine (classical basis, modified, no novel actives).",
            authority="AYUSH Licensing Authority", source_id="dc_act_1940_ayush", rule_version=_VERSION,
        ),
        Rule(
            id="phytopharmaceutical",
            when={"novel_actives": "yes", "intended_use": "medicine", "plant_derived": "yes"},
            obligation="Phytopharmaceutical drug (purified plant-derived actives with defined constituents); "
                       "follow the phytopharmaceutical pathway with specified safety/efficacy data.",
            authority="Drugs Controller (CDSCO)", source_id="dc_act_1940_ayush", rule_version=_VERSION,
        ),
        Rule(
            id="new_drug",
            when={"novel_actives": "yes", "intended_use": "medicine"},
            obligation="New drug (novel actives); requires additional safety and efficacy data before approval.",
            authority="Drugs Controller", source_id="dc_act_1940_ayush", rule_version=_VERSION,
        ),
        Rule(
            id="nutraceutical",
            when={"intended_use": "food"},
            obligation="Nutraceutical / health supplement; FSSAI regulation applies.",
            authority="FSSAI", source_id="fssai_nutraceutical", rule_version=_VERSION,
        ),
        Rule(
            id="cosmetic",
            when={"intended_use": "cosmetic"},
            obligation="Cosmetic; Drugs & Cosmetics cosmetic rules apply.",
            authority="Drugs Controller", source_id="dc_act_1940_ayush", rule_version=_VERSION,
        ),
    ],
)

