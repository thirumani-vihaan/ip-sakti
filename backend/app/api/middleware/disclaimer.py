"""Attach the legal disclaimer and a request id to every response."""
from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

DISCLAIMER = "Informational guidance, not legal advice. Consult a qualified professional."


class DisclaimerHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Disclaimer"] = DISCLAIMER
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return response
