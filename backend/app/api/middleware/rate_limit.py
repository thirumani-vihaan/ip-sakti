"""In-memory per-client sliding-window rate limiter (no accounts, no external store).

Client identity:
- Direct deployment (default): key on the socket peer request.client.host.
- Behind our own reverse proxy: set TRUST_PROXY=1. We then key on the RIGHT-MOST
  X-Forwarded-For entry, which is the hop appended by our proxy and is therefore not
  client-forgeable (a client can only prepend left-side values). The left-most entry is
  never trusted.

Buckets for clients idle beyond the window are swept out so the map cannot grow without
bound (including under forged-header floods).
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 300, window_seconds: int = 60, trust_proxy: bool | None = None) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window_seconds
        self.trust_proxy = (os.getenv("TRUST_PROXY", "0") == "1") if trust_proxy is None else trust_proxy
        self._hits: dict[str, deque] = defaultdict(deque)
        self._since_sweep = 0
        self._sweep_every = 2048

    def _client_key(self, request: Request) -> str:
        if self.trust_proxy:
            xff = request.headers.get("x-forwarded-for")
            if xff:
                parts = [p.strip() for p in xff.split(",") if p.strip()]
                if parts:
                    return parts[-1]  # hop appended by our proxy; not client-forgeable
        return request.client.host if request.client else "unknown"

    def _sweep(self, now: float) -> None:
        stale = [k for k, d in self._hits.items() if not d or now - d[-1] > self.window]
        for k in stale:
            self._hits.pop(k, None)

    async def dispatch(self, request: Request, call_next):
        key = self._client_key(request)
        now = time.monotonic()

        self._since_sweep += 1
        if self._since_sweep >= self._sweep_every:
            self._since_sweep = 0
            self._sweep(now)

        dq = self._hits[key]
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
