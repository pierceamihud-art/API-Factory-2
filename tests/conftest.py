import os
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))

env_path = repo_root / "SafeNow.env.example"
_original_env: dict[str, str | None] = {}
if env_path.exists():
    from dotenv import dotenv_values

    for key, value in dotenv_values(env_path).items():
        if value is None:
            continue
        _original_env[key] = os.environ.get(key)
        os.environ[key] = value

    # Ensure tests use the simulated model backend instead of making real API calls.
    if "ANTHROPIC_API_KEY" not in _original_env:
        _original_env["ANTHROPIC_API_KEY"] = os.environ.get("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = ""

    # Disable optional Supabase backend to avoid init errors in tests.
    if "ENABLE_SUPABASE_BACKEND" not in _original_env:
        _original_env["ENABLE_SUPABASE_BACKEND"] = os.environ.get("ENABLE_SUPABASE_BACKEND")
    os.environ["ENABLE_SUPABASE_BACKEND"] = "false"

from app.main import app


@pytest.fixture(scope="session", autouse=True)
def load_env_from_example():
    """Populate test environment using SafeNow.env.example defaults."""
    if not env_path.exists():
        yield
        return

    try:
        yield
    finally:
        for key, value in _original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client backed by the FastAPI ASGI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
