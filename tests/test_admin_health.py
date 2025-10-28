import pytest

@pytest.mark.asyncio
async def test_admin_health_deep(async_client):
    resp = await async_client.get("/admin/health/deep")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "checks" in data
    assert set(data["checks"].keys()) == {"api", "rate_limiter", "model"}
    assert data["status"] in ("healthy", "degraded")
