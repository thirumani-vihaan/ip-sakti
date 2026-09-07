"""T036 acceptance: circuit breaker recovers (half-open after cooldown), then closes on success."""
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))


def main() -> int:
    from app.integrations.provider import CircuitBreaker

    # opens after threshold consecutive failures
    br = CircuitBreaker(threshold=2, cooldown_seconds=30)
    br.record_failure()
    assert br.healthy, "one failure below threshold stays healthy"
    br.record_failure()
    assert br.open and not br.healthy, "threshold failures open the breaker"

    # after the cooldown elapses it reports half-open (closed) so the caller retries
    br.opened_at -= 60
    assert not br.open, "breaker must go half-open after cooldown (auto-recovery)"

    # a successful trial fully closes it
    br.record_success()
    assert br.healthy and br.failures == 0

    # a failed trial re-opens it (does not get stuck half-open)
    br2 = CircuitBreaker(threshold=1, cooldown_seconds=30)
    br2.record_failure()
    assert br2.open
    br2.opened_at -= 60  # cooldown elapsed -> half-open
    assert not br2.open
    br2.record_failure()  # trial fails
    assert br2.open, "a failed trial must re-open the breaker"

    print("T036 OK: circuit breaker opens, half-opens after cooldown, closes on success, re-opens on failure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
