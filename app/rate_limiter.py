"""Async pluggable rate limiter: memory (default) and Redis-backed.

Usage: import get_rate_limiter and call await limiter.is_rate_limited(key)
"""
from __future__ import annotations

import asyncio
import os
import time
from collections import deque
from typing import Deque, Dict

try:
    import redis.asyncio as aioredis  # type: ignore
except Exception:  # pragma: no cover - redis optional
    aioredis = None


class BaseRateLimiter:
    async def is_rate_limited(self, key: str) -> bool:  # pragma: no cover - interface
        raise NotImplementedError


class MemoryRateLimiter(BaseRateLimiter):
    def __init__(self, window: int = 60, requests: int = 20) -> None:
        self.window = window
        self.requests = requests
        self._rate_table: Dict[str, Deque[float]] = {}
        self._lock = asyncio.Lock()

    async def is_rate_limited(self, key: str) -> bool:
        now = time.time()
        async with self._lock:
            dq = self._rate_table.setdefault(key, deque())
            while dq and dq[0] <= now - self.window:
                dq.popleft()
            if len(dq) >= self.requests:
                return True
            dq.append(now)
            return False


class RedisRateLimiter(BaseRateLimiter):
    def __init__(self, redis_url: str, window: int = 60, requests: int = 20) -> None:
        if aioredis is None:
            raise RuntimeError("redis package not available; install redis>=4.6.0 to use RedisRateLimiter")
        self.window = window
        self.requests = requests
        self._client = aioredis.from_url(redis_url)

    async def is_rate_limited(self, key: str) -> bool:
        # Use a sorted set per key with timestamps as scores.
        now = time.time()
        zkey = f"rl:{key}"
        min_score = now - self.window
        # remove old
        try:
            await self._client.zremrangebyscore(zkey, 0, min_score)
            count = await self._client.zcard(zkey)
            if count >= self.requests:
                return True
            # add current timestamp; use member as score string to avoid collisions
            await self._client.zadd(zkey, {str(now): now})
            # set TTL a bit longer than window
            await self._client.expire(zkey, int(self.window + 5))
            return False
        except Exception:
            # Fail open: if Redis errors, don't block traffic but log in production
            return False


# Singleton factory
_GLOBAL: BaseRateLimiter | None = None


def get_rate_limiter() -> BaseRateLimiter:
    """Return a singleton rate limiter configured from environment.

    Environment variables:
      RATE_LIMIT_STORE: memory|redis (default memory)
      RATE_LIMIT_WINDOW, RATE_LIMIT_REQUESTS, REDIS_URL
    """
    global _GLOBAL
    if _GLOBAL is not None:
        return _GLOBAL

    store = os.getenv("RATE_LIMIT_STORE", "memory").lower()
    window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    requests = int(os.getenv("RATE_LIMIT_REQUESTS", "20"))

    if store == "redis":
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _GLOBAL = RedisRateLimiter(redis_url, window=window, requests=requests)
    else:
        _GLOBAL = MemoryRateLimiter(window=window, requests=requests)

    return _GLOBAL


def _reset_rate_limiter_for_tests() -> None:
    """Reset the global singleton (tests only).

    This allows tests to reconfigure the limiter by changing environment variables
    before calling get_rate_limiter() again.
    """
    global _GLOBAL
    _GLOBAL = None


# Public alias for tests
reset_rate_limiter_for_tests = _reset_rate_limiter_for_tests
