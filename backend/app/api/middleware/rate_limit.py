"""Simple in-memory per-IP sliding-window rate limiter (no accounts, no external store)."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 300, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        dq = self._hits[ip]
        while dq and now - dq[0] > self.window:
            dq.popleft()
        if len(dq) >= self.limit:
            retry = max(1, int(self.window - (now - dq[0])))
            return JSONResponse(
                {"detail": "rate limit exceeded; slow down"},
                status_code=429,
                headers={"Retry-After": str(retry)},
            )
        dq.append(now)
        return await call_next(request)
