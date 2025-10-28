"""Supabase integration used as an optional backup persistence layer.

All Supabase interactions are guarded behind a feature flag so the core
in-memory / Redis-backed behaviour remains the default. When the feature
flag is enabled (and credentials are provided), we best-effort persist
API key metadata, audit entries, and retention records to Supabase for
secondary durability.

The implementation is intentionally defensive: failures are logged and
suppressed to avoid impacting primary request handling paths.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("api-factory.supabase")

try:  # pragma: no cover - optional dependency
    from supabase import Client, create_client  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    Client = None  # type: ignore
    create_client = None  # type: ignore


_SUPABASE_ENABLED = os.getenv("ENABLE_SUPABASE_BACKEND", "false").lower() in ("1", "true", "yes")
_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
_SUPABASE_SCHEMA = os.getenv("SUPABASE_SCHEMA", "public")

_API_KEY_TABLE = os.getenv("SUPABASE_API_KEY_TABLE", "api_key_metadata")
_AUDIT_TABLE = os.getenv("SUPABASE_AUDIT_TABLE", "audit_entries")
_RETENTION_TABLE = os.getenv("SUPABASE_RETENTION_TABLE", "retention_records")

_BACKEND: Optional["SupabaseBackend"] = None
_INIT_LOCK = asyncio.Lock()


class SupabaseBackend:
    """Thin wrapper around the Supabase client with async helpers."""

    def __init__(self, client: Client) -> None:  # type: ignore[valid-type]
        self._client = client

    async def save_api_key_metadata(self, key_id: str, metadata: Dict[str, Any]) -> None:
        payload = {"id": key_id, **metadata}
        await self._upsert(_API_KEY_TABLE, payload)

    async def mark_api_key_disabled(self, key_id: str) -> None:
        payload = {"id": key_id, "disabled": "1"}
        await self._upsert(_API_KEY_TABLE, payload)

    async def save_audit_entry(self, payload: Dict[str, Any]) -> None:
        await self._insert(_AUDIT_TABLE, payload)

    async def save_retention_record(self, data_id: str, payload: Dict[str, Any]) -> None:
        record = {"data_id": data_id, **payload}
        await self._upsert(_RETENTION_TABLE, record)

    async def _upsert(self, table: str, payload: Dict[str, Any]) -> None:
        await self._submit(lambda: self._client.table(table).upsert(payload).execute())

    async def _insert(self, table: str, payload: Dict[str, Any]) -> None:
        await self._submit(lambda: self._client.table(table).insert(payload).execute())

    async def _submit(self, func) -> None:
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, func)
        except RuntimeError:
            # No running loop (e.g. during sync tests); run synchronously.
            func()
        except Exception:  # pragma: no cover - network / client failures
            logger.exception("Supabase operation failed")


async def _initialise_backend() -> Optional[SupabaseBackend]:
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND

    if not _should_initialise():
        return None

    async with _INIT_LOCK:
        if _BACKEND is not None:
            return _BACKEND
        try:
            client = create_client(  # type: ignore[misc]
                _SUPABASE_URL,  # type: ignore[arg-type]
                _SUPABASE_SERVICE_KEY,  # type: ignore[arg-type]
                schema=_SUPABASE_SCHEMA,
            )
            _BACKEND = SupabaseBackend(client)
            logger.info("Supabase backup backend enabled (schema=%s)", _SUPABASE_SCHEMA)
        except Exception:  # pragma: no cover - initialisation failure
            logger.exception("Failed to initialise Supabase backend; continuing without it")
            _BACKEND = None
    return _BACKEND


def _should_initialise() -> bool:
    if not _SUPABASE_ENABLED:
        return False
    if create_client is None:
        logger.warning("Supabase Python client not installed; disable ENABLE_SUPABASE_BACKEND or install package")
        return False
    if not _SUPABASE_URL or not _SUPABASE_SERVICE_KEY:
        logger.warning("Supabase credentials missing; set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    return True


async def persist_api_key_metadata(key_id: str, metadata: Dict[str, Any]) -> None:
    backend = await _initialise_backend()
    if backend is None:
        return
    await backend.save_api_key_metadata(key_id, metadata)


async def mark_api_key_disabled(key_id: str) -> None:
    backend = await _initialise_backend()
    if backend is None:
        return
    await backend.mark_api_key_disabled(key_id)


def persist_audit_entry(payload: Dict[str, Any]) -> None:
    """Fire-and-forget persistence; safe to call from sync contexts."""
    if not _SUPABASE_ENABLED:
        return

    async def _persist() -> None:
        backend = await _initialise_backend()
        if backend is None:
            return
        await backend.save_audit_entry(payload)

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_persist())
    except RuntimeError:
        asyncio.run(_persist())
    except Exception:  # pragma: no cover - scheduling failures
        logger.exception("Failed to enqueue Supabase audit persistence")


def persist_retention_record(data_id: str, payload: Dict[str, Any]) -> None:
    if not _SUPABASE_ENABLED:
        return

    async def _persist() -> None:
        backend = await _initialise_backend()
        if backend is None:
            return
        await backend.save_retention_record(data_id, payload)

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_persist())
    except RuntimeError:
        asyncio.run(_persist())
    except Exception:  # pragma: no cover - scheduling failures
        logger.exception("Failed to enqueue Supabase retention persistence")


__all__ = [
    "persist_api_key_metadata",
    "mark_api_key_disabled",
    "persist_audit_entry",
    "persist_retention_record",
]
