"""Structured (redaction-friendly) logging setup for the service."""
from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO") -> logging.Logger:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s")
    )
    log = logging.getLogger("ipsakti")
    log.handlers = [handler]
    log.setLevel(level.upper())
    log.propagate = False
    return log
