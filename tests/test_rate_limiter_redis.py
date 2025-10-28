import os
import asyncio
import pytest

from app import rate_limiter as rl


pytestmark = pytest.mark.asyncio


async def test_rate_limiter_e2e():
    """End-to-end test for the rate limiter.

    This test runs for both `memory` and `redis` stores. CI sets
    `RATE_LIMIT_STORE` via the job matrix. The test reinitializes the
    limiter singleton to pick up env changes.
    """
    store = os.getenv("RATE_LIMIT_STORE", "memory").lower()
    # configure tiny window for fast test
    os.environ["RATE_LIMIT_WINDOW"] = "1"
    os.environ["RATE_LIMIT_REQUESTS"] = "2"

    # if redis, ensure REDIS_URL defaults are present
    if store == "redis":
        os.environ.setdefault("REDIS_URL", os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"))

    # reset singleton so new config is picked up
    rl.reset_rate_limiter_for_tests()
    limiter = rl.get_rate_limiter()

    key = f"test:{int(asyncio.get_event_loop().time()*1000)}"

    assert await limiter.is_rate_limited(key) is False
    assert await limiter.is_rate_limited(key) is False
    # third should be rate limited
    assert await limiter.is_rate_limited(key) is True

    # wait window to expire, then should be allowed again
    await asyncio.sleep(1.1)
    assert await limiter.is_rate_limited(key) is False
