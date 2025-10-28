import os

import pytest


@pytest.mark.asyncio
async def test_health(async_client):
    r = await async_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_predict_requires_api_key(async_client):
    r = await async_client.post("/predict", json={"input": "hello"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_predict_success(async_client):
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post(
        "/predict",
        headers=headers,
        json={
            "input": "hello",
            "context": {"system": "You are a friendly assistant"}
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert "output" in j
    assert isinstance(j["output"], str) and len(j["output"]) > 0


@pytest.mark.asyncio
async def test_default_model_is_claude(async_client):
    # Default behavior should use DEFAULT_MODEL from config
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post("/predict", headers=headers, json={"input": "hello"})
    assert r.status_code == 200
    j = r.json()
    # debug.method should show the model used
    expected_model = os.getenv("DEFAULT_MODEL", "claude-sonnet-3.5")
    assert j.get("debug", {}).get("method") == expected_model


@pytest.mark.asyncio
async def test_client_requested_model_overridden_when_forced(async_client):
    # Forced model mode should ignore the client-requested model header
    headers = {"X-API-Key": "devkey", "X-Model": "mvp-placeholder"}
    r = await async_client.post("/predict", headers=headers, json={"input": "hello"})
    assert r.status_code == 200
    j = r.json()
    expected_model = os.getenv("DEFAULT_MODEL", "claude-sonnet-3.5")
    assert j.get("debug", {}).get("method") == expected_model


@pytest.mark.asyncio
async def test_predict_input_too_long(async_client):
    headers = {"X-API-Key": "devkey"}
    long_text = "a" * 1200
    r = await async_client.post("/predict", headers=headers, json={"input": long_text})
    assert r.status_code == 413


@pytest.mark.asyncio
async def test_predict_profanity(async_client):
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post(
        "/predict",
        headers=headers,
        json={"input": "this contains badword"},
    )
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_security_headers(async_client):
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post("/predict", headers=headers, json={"input": "hello"})
    assert r.status_code == 200
    assert "X-Content-Type-Options" in r.headers
    assert "X-Frame-Options" in r.headers
    assert "X-XSS-Protection" in r.headers
    assert "Strict-Transport-Security" in r.headers
    assert "Content-Security-Policy" in r.headers


@pytest.mark.asyncio
async def test_predict_injection_blocked(async_client):
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post(
        "/predict",
        headers=headers,
        json={"input": "<script>alert('xss')</script>"},
    )
    assert r.status_code == 400
    assert "security_validation" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_predict_sql_injection_blocked(async_client):
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post(
        "/predict",
        headers=headers,
        json={"input": "SELECT * FROM users; DROP TABLE users;"},
    )
    assert r.status_code == 400
    assert "security_validation" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_predict_command_injection_blocked(async_client):
    headers = {"X-API-Key": "devkey"}
    r = await async_client.post(
        "/predict",
        headers=headers,
        json={"input": "hello; rm -rf /"},
    )
    assert r.status_code == 400
    assert "security_validation" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_predict_with_ip_rate_limiting(async_client):
    headers = {
        "X-API-Key": "devkey",
        "X-Real-IP": "192.168.1.1"
    }
    r = await async_client.post("/predict", headers=headers, json={"input": "hello"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_invalid_api_key_format(async_client):
    headers = {"X-API-Key": "short"}
    r = await async_client.post("/predict", headers=headers, json={"input": "hello"})
    assert r.status_code == 401
    assert "format" in r.json()["detail"].lower()
