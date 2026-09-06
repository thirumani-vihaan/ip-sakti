"""Immutable enum contract for IP-SAKTI. Do not change without a flagged, high-visibility candidate."""
from enum import Enum


class Jurisdiction(str, Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class ForceState(str, Enum):
    IN_FORCE = "in_force"
    NOT_YET_IN_FORCE = "not_yet_in_force"
    REPEALED = "repealed"


class EvidenceStrength(str, Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LIMITED = "limited"


class FormulationType(str, Enum):
    CLASSICAL = "classical"
    PROPRIETARY = "proprietary"
    NEW_DRUG = "new_drug"
    PHYTOPHARMACEUTICAL = "phytopharmaceutical"
    NUTRACEUTICAL = "nutraceutical"
    COSMETIC = "cosmetic"


class Domain(str, Enum):
    PATENT = "patent"
    GI_TRADEMARK = "gi_trademark"
    ABS = "abs"
    REGULATORY = "regulatory"
    TK_RISK = "tk_risk"
    INTERNATIONAL = "international"


class AnswerMode(str, Enum):
    LIVE = "live"
    EXTRACTIVE = "extractive"
    CACHED = "cached"
