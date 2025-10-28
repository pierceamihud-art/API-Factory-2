import pytest


@pytest.mark.asyncio
async def test_intention_endpoint_root(async_client):
    r = await async_client.get("/v1/")
    assert r.status_code == 200
    j = r.json()
    assert "Welcome to the Daily Intention API" in j.get("message", "")


@pytest.mark.asyncio
async def test_generate_intention(async_client):
    payload = {
        "profile": {"values": ["presence"], "tradition": "secular"},
        "context": {"mood": "calm", "time": "morning", "moon_phase": "new"}
    }
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post("/v1/intention", headers=headers, json=payload)
    assert r.status_code == 200
    j = r.json()
    assert "intention" in j and "affirmation" in j and "ritual" in j
