import pytest

from app import auth

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
async def set_auth_store_env(monkeypatch):
    # Use the in-memory auth store for tests to avoid external Redis dependency
    monkeypatch.setenv("AUTH_STORE", "memory")
    # Reset any in-memory store
    await auth._reset_for_tests()
    yield


async def test_admin_key_allows_admin_endpoint(async_client):
    # Create an admin key and a regular key
    admin_raw = "admin_test_key"
    user_raw = "user_test_key"

    await auth.create_api_key(admin_raw, owner="admin", is_admin=True, quota=100)
    await auth.create_api_key(user_raw, owner="user", is_admin=False, quota=100)

    # Admin endpoint requires admin_ prefix in key or metadata; our admin creation sets metadata is_admin
    headers_admin = {"X-API-Key": admin_raw}
    headers_user = {"X-API-Key": user_raw}

    r = await async_client.get("/admin/stats", headers=headers_admin)
    assert r.status_code == 200

    r = await async_client.get("/admin/stats", headers=headers_user)
    assert r.status_code == 403


async def test_key_rotation_disables_old_key(async_client):
    old_raw = "old_key"
    new_raw = "new_key"

    await auth.create_api_key(old_raw, owner="ops", is_admin=False, quota=10)

    headers_old = {"X-API-Key": old_raw}
    r = await async_client.get("/health", headers=headers_old)
    assert r.status_code == 200

    # Rotate: disable old, create new
    await auth.rotate_api_key(old_raw, new_raw, owner="ops", is_admin=False, quota=10)

    # Old key should now be invalid
    r = await async_client.get("/health", headers=headers_old)
    assert r.status_code == 401

    # New key works
    headers_new = {"X-API-Key": new_raw}
    r = await async_client.get("/health", headers=headers_new)
    assert r.status_code == 200
