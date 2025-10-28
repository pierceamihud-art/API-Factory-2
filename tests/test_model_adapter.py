import os
import pytest
from app.model_adapter import ModelAdapter

pytestmark = pytest.mark.asyncio

async def test_simulated_client_returns_expected():
    os.environ["ANTHROPIC_API_KEY"] = "not-set"
    adapter = ModelAdapter(model="mvp-placeholder")
    result = await adapter.generate("hello world")
    assert result.startswith("simulated response: hello world")

async def test_real_client_fallback():
    # If anthropic is not installed or key is not set, should fallback
    os.environ["ANTHROPIC_API_KEY"] = "not-set"
    adapter = ModelAdapter(model="claude-sonnet-3.5")
    result = await adapter.generate("test")
    assert "simulated response" in result

# Optionally, test with a real key if available (skipped if not set)
@pytest.mark.skipif(os.getenv("ANTHROPIC_API_KEY", "not-set") == "not-set", reason="No real API key configured")
async def test_real_client_runs():
    adapter = ModelAdapter(model="claude-sonnet-3.5")
    result = await adapter.generate("hello")
    assert isinstance(result, str) and len(result) > 0
