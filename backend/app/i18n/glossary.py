"""Locked bilingual legal glossary (English -> Hindi / Telugu)."""
from __future__ import annotations

GLOSSARY: dict[str, dict[str, str]] = {
    "en-hi": {
        "traditional knowledge": "paramparagat gyaan",
        "biological resource": "jaivik sansaadhan",
        "prior approval": "poorv anumati",
        "benefit sharing": "laabh saajhakaran",
        "geographical indication": "bhaugolik sanket",
    },
    "en-te": {
        "traditional knowledge": "sampradaaya gnyaanam",
        "biological resource": "jaiva vanarulu",
        "prior approval": "munduga anumati",
        "benefit sharing": "prayojana panchukolu",
        "geographical indication": "bhaugolika soochika",
    },
}


def glossary_for(src: str, tgt: str) -> dict[str, str]:
    return GLOSSARY.get(f"{src}-{tgt}", {})
