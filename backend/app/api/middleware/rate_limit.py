"""Simple in-memory per-IP sliding-window rate limiter (no accounts, no external store)."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def client_ip(request: Request) -> str:
    # Behind the nginx proxy the socket peer is the proxy; honour the real client
    # from the left-most X-Forwarded-For entry so the limiter is genuinely per-client.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 300, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        ip = client_ip(request)
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
        if not dq:  # keep the map from growing without bound
            self._hits.pop(ip, None)
        return await call_next(request)
