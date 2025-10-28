"""Authentication / API key store backed by Redis with an in-memory fallback for tests.

Provides:
- `get_api_key` dependency for FastAPI routes (enforces existence, active status, and per-key quota)
- helpers: `create_api_key`, `disable_api_key`, `rotate_api_key` for admin/management and tests

Storage layout (Redis): Hash at `api_key:{sha256(raw_key)}` with fields:
  owner, tier, is_admin (0/1), quota (int or empty), usage (int), disabled (0/1)

In-memory fallback stores the same shape in a dict.

Note: For production use, store only hashed keys and manage raw keys securely (never commit raw keys).
"""
from __future__ import annotations

import os
import hashlib
import logging
import asyncio
from typing import Any, Dict, Optional, TYPE_CHECKING

from fastapi import Header, HTTPException, status

try:
    import redis.asyncio as aioredis  # type: ignore
except Exception:  # pragma: no cover - redis optional
    aioredis = None

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from redis.asyncio import Redis as RedisClient  # type: ignore
else:  # pragma: no cover - runtime fallback when redis missing
    RedisClient = Any  # type: ignore

from app.supabase_backend import (
    mark_api_key_disabled as supabase_mark_api_key_disabled,
    persist_api_key_metadata as supabase_persist_api_key_metadata,
)

logger = logging.getLogger("api-factory.auth")

AUTH_STORE = os.getenv("AUTH_STORE", "memory").lower()  # redis or memory
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# In-memory fallback
_memory_store: Dict[str, Dict[str, str]] = {}
_memory_lock = asyncio.Lock()

_redis_client: Optional[RedisClient] = None

async def _get_redis_client() -> RedisClient:
    global _redis_client
    if aioredis is None:
        raise RuntimeError("redis package not available; install redis>=4.6.0 to use Redis auth store")
    if _redis_client is None:
        _redis_client = aioredis.from_url(REDIS_URL)
    return _redis_client


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


async def create_api_key(raw_key: str, owner: str = "dev", tier: str = "standard", is_admin: bool = False, quota: Optional[int] = None) -> str:
    """Create and store API key metadata. Returns the hashed key id.

    In production, you should store only the hash and return the raw key to the user exactly once.
    """
    h = _hash_key(raw_key)
    data = {
        "owner": owner,
        "tier": tier,
        "is_admin": "1" if is_admin else "0",
        "quota": str(quota) if quota is not None else "",
        "usage": "0",
        "disabled": "0",
    }

    if AUTH_STORE == "redis":
        client = await _get_redis_client()
        await client.hset(f"api_key:{h}", mapping=data)
    else:
        async with _memory_lock:
            _memory_store[h] = data

    await supabase_persist_api_key_metadata(h, data)
    return h


async def _get_metadata(raw_key: str) -> Optional[Dict[str, str]]:
    h = _hash_key(raw_key)
    if AUTH_STORE == "redis":
        client = await _get_redis_client()
        exists = await client.exists(f"api_key:{h}")
        if not exists:
            return None
        data = await client.hgetall(f"api_key:{h}")
        # redis returns bytes for values, decode
        return {k.decode(): v.decode() for k, v in data.items()}
    else:
        async with _memory_lock:
            return _memory_store.get(h)


async def _set_metadata_by_hash(hashed: str, mapping: Dict[str, str]):
    if AUTH_STORE == "redis":
        client = await _get_redis_client()
        await client.hset(f"api_key:{hashed}", mapping=mapping)
    else:
        async with _memory_lock:
            _memory_store[hashed] = mapping


async def disable_api_key(raw_key: str) -> bool:
    """Mark a key disabled. Returns True if found and disabled."""
    h = _hash_key(raw_key)
    result = False
    if AUTH_STORE == "redis":
        client = await _get_redis_client()
        exists = await client.exists(f"api_key:{h}")
        if not exists:
            return False
        await client.hset(f"api_key:{h}", mapping={"disabled": "1"})
        result = True
    else:
        async with _memory_lock:
            v = _memory_store.get(h)
            if not v:
                return False
            v["disabled"] = "1"
            _memory_store[h] = v
            result = True

    if result:
        await supabase_mark_api_key_disabled(h)
    return result


async def rotate_api_key(old_raw: str, new_raw: str, owner: str = "dev", tier: str = "standard", is_admin: bool = False, quota: Optional[int] = None) -> str:
    """Disable old key and create a new key with given metadata. Returns new hashed id."""
    await disable_api_key(old_raw)
    return await create_api_key(new_raw, owner=owner, tier=tier, is_admin=is_admin, quota=quota)


async def _increment_usage(hashed: str) -> int:
    if AUTH_STORE == "redis":
        client = await _get_redis_client()
        return int(await client.hincrby(f"api_key:{hashed}", "usage", 1))
    else:
        async with _memory_lock:
            v = _memory_store.get(hashed)
            if not v:
                raise KeyError("not found")
            v["usage"] = str(int(v.get("usage", "0")) + 1)
            _memory_store[hashed] = v
            return int(v["usage"])


async def get_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> str:
    """FastAPI dependency that validates API key, checks disabled state and quota.

    Returns the raw API key string if valid. Raises HTTPException otherwise.
    """
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")

    meta = await _get_metadata(x_api_key)
    if not meta:
        # Allow the global default dev key (convenience for local dev/tests) if set in env
        if x_api_key == os.getenv("API_KEY", "devkey"):
            return x_api_key
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    if meta.get("disabled") == "1":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key disabled")

    # enforce quota if present
    quota = int(meta.get("quota")) if meta.get("quota") else None
    h = _hash_key(x_api_key)
    if quota is not None:
        try:
            usage = await _increment_usage(h)
            if usage > quota:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Quota exceeded")
        except KeyError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    # pass through the raw key for downstream use
    return x_api_key


# Test helper to reset in-memory store (used by tests)
async def _reset_for_tests() -> None:
    global _memory_store
    async with _memory_lock:
        _memory_store = {}


__all__ = [
    "create_api_key",
    "disable_api_key",
    "rotate_api_key",
    "get_api_key",
    "_reset_for_tests",
]
