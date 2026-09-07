"""Locked bilingual legal glossary (English -> Hindi / Telugu).

Romanised target terms keep the demo readable without extra fonts. These are the
credential-free localisation anchors; full neural translation comes from Bhashini
when configured. Statute/section references are never translated (see translate.py).
"""
from __future__ import annotations

GLOSSARY: dict[str, dict[str, str]] = {
    "en-hi": {
        "traditional knowledge": "paramparagat gyaan",
        "biological resource": "jaivik sansaadhan",
        "biological diversity": "jaiv vividhata",
        "national biodiversity authority": "rashtriya jaiv vividhata pradhikaran",
        "state biodiversity board": "rajya jaiv vividhata board",
        "prior approval": "poorv anumati",
        "benefit sharing": "laabh saajhakaran",
        "geographical indication": "bhaugolik sanket",
        "trademark": "vyaapaar chinh",
        "copyright": "pratilipi adhikaar",
        "patent": "petent",
        "invention": "aavishkaar",
        "drug": "aushadhi",
        "advertisement": "vigyapan",
        "license": "anugyapatra",
    },
    "en-te": {
        "traditional knowledge": "sampradaaya gnyaanam",
        "biological resource": "jaiva vanarulu",
        "biological diversity": "jaiva vaividhyam",
        "national biodiversity authority": "jaateeya jaiva vaividhya samstha",
        "state biodiversity board": "raashtra jaiva vaividhya mandali",
        "prior approval": "munduga anumati",
        "benefit sharing": "prayojana panchukolu",
        "geographical indication": "bhaugolika soochika",
        "trademark": "vyaapaara mudra",
        "copyright": "prachurana hakku",
        "patent": "petentu",
        "invention": "aavishkaranam",
        "drug": "mandu",
        "advertisement": "prakatana",
        "license": "anumati patram",
    },
}


def glossary_for(src: str, tgt: str) -> dict[str, str]:
    return GLOSSARY.get(f"{src}-{tgt}", {})
