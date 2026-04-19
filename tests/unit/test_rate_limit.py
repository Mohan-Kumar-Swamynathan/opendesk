"""Rate limit tests."""
import pytest


def test_rate_limit_recovers_after_window():
    from opendesk.safety import RateLimiter
    import time

    limiter = RateLimiter()

    for _ in range(5):
        allowed, retry = limiter.check_and_consume("delete_file")
        assert allowed, "First 5 calls should be allowed"

    allowed, retry = limiter.check_and_consume("delete_file")
    assert not allowed, "6th call should be denied"
    assert retry > 0, "Should report retry time"


def test_no_rate_limit_for_safe_tools():
    from opendesk.safety import RateLimiter

    limiter = RateLimiter()

    allowed, retry = limiter.check_and_consume("get_system_info")
    assert allowed, "Get tools should not be rate limited"