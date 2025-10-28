"""Test legal compliance in predict endpoint."""
import pytest

@pytest.mark.asyncio
async def test_predict_legal_compliance(async_client):
    """Test predict endpoint with legal compliance checks."""
    # Test PII without consent
    response = await async_client.post(
        "/predict",
        json={
            "input": "My email is test@example.com",
            "region": "eu"
        },
        headers={"X-API-Key": "devkey"}
    )
    assert response.status_code == 400
    assert "pii_without_consent" in response.json()["detail"]

    # Test GDPR compliance - missing required consents
    response = await async_client.post(
        "/predict",
        json={
            "input": "Regular content",
            "region": "eu",
            "user_consent": {"data_processing": True}
        },
        headers={"X-API-Key": "devkey"}
    )
    assert response.status_code == 400
    assert "gdpr_requirements_not_met" in response.json()["detail"]

    # Test copyrighted content
    response = await async_client.post(
        "/predict",
        json={
            "input": "© 2025 Company. All rights reserved.",
            "region": "global",
            "user_consent": {"data_processing": True}
        },
        headers={"X-API-Key": "devkey"}
    )
    assert response.status_code == 400
    assert "content_rights" in response.json()["detail"]

    # Test successful request with full compliance
    response = await async_client.post(
        "/predict",
        json={
            "input": "Regular user content",
            "region": "eu",
            "user_consent": {
                "data_processing": True,
                "data_storage": True,
                "data_sharing": True
            }
        },
        headers={"X-API-Key": "devkey"}
    )
    assert response.status_code == 200