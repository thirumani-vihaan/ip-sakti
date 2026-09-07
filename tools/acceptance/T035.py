"""T035 acceptance: rate limiting is per-client via X-Forwarded-For (proxy-aware)."""
import os
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import build_app

    os.environ["RATE_LIMIT_PER_MIN"] = "2"
    os.environ["TRUST_PROXY"] = "1"
    try:
        client = TestClient(build_app(Settings()))
        a = "203.0.113.7"
        b = "198.51.100.9"
        # client A exhausts its own 2/min budget
        ca = [client.get("/api/health", headers={"X-Forwarded-For": a}).status_code for _ in range(3)]
        # client B must be unaffected by A hitting the limit
        cb = client.get("/api/health", headers={"X-Forwarded-For": b}).status_code
    finally:
        os.environ.pop("RATE_LIMIT_PER_MIN", None)
        os.environ.pop("TRUST_PROXY", None)

    assert ca[:2] == [200, 200] and ca[2] == 429, ca
    assert cb == 200, f"different client must have its own bucket, got {cb}"

    # anti-spoof: with TRUST_PROXY unset (default), a forged X-Forwarded-For is ignored,
    # so flooding with unique fake IPs still shares one bucket (cannot bypass the limit)
    os.environ["RATE_LIMIT_PER_MIN"] = "2"
    try:
        c2 = TestClient(build_app(Settings()))
        codes = [c2.get("/api/health", headers={"X-Forwarded-For": f"10.0.0.{i}"}).status_code for i in range(3)]
    finally:
        os.environ.pop("RATE_LIMIT_PER_MIN", None)
    assert codes[2] == 429, f"forged XFF must not bypass the limit when proxy is untrusted, got {codes}"

    print("T035 OK: rate limiting is per-client (X-Forwarded-For), not one global proxy bucket")
    return 0


if __name__ == "__main__":
    sys.exit(main())
