"""Build the REAL corpus from public sources (OFF the offline test path).

This is a scaffold: it documents the target sources and writes provenance into the
manifest. Running it requires network and is a separate, reviewable commit. The
offline test suite never calls this — it uses the committed sample corpus.

Targets (public): India Code (Patents Act 1970, Biological Diversity Act 2002,
Trade Marks Act, GI Act, Designs Act, Copyright Act, Drugs & Cosmetics Act, Drugs
& Magic Remedies Act), ipindia.gov.in, ayush.gov.in guidelines, DPIIT TK &
biological-material patent guidelines, WIPO (TRIPS, PCT). TKDL full DB is NOT
available and is never fetched.
"""
from __future__ import annotations

import sys


def main() -> int:
    print("fetch_corpus is a scaffold; wire real downloads + provenance here.")
    print("Offline tests do NOT use this; they use the committed sample corpus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
