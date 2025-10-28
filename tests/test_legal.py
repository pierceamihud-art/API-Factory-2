"""Tests for legal compliance module."""
import pytest
from app.legal import legal_validator, DataRegion

@pytest.mark.asyncio
async def test_pii_detection():
    """Test PII detection in content."""
    content_with_pii = "Contact John Smith at john.smith@example.com or 555-123-4567"
    detected = legal_validator._detect_pii(content_with_pii)
    assert "email" in detected
    assert "phone_number" in detected
    assert "full_name" in detected

@pytest.mark.asyncio
async def test_gdpr_compliance():
    """Test GDPR compliance validation."""
    content = "Test content with user data"
    
    # Test without consent
    assert not legal_validator._validate_gdpr_compliance(content, None)
    
    # Test with partial consent
    partial_consent = {"data_processing": True}
    assert not legal_validator._validate_gdpr_compliance(content, partial_consent)
    
    # Test with full consent
    full_consent = {
        "data_processing": True,
        "data_storage": True,
        "data_sharing": True
    }
    assert legal_validator._validate_gdpr_compliance(content, full_consent)

@pytest.mark.asyncio
async def test_ccpa_compliance():
    """Test CCPA compliance validation."""
    content = "Test content with California resident data"
    
    # Test without consent
    assert not legal_validator._validate_ccpa_compliance(content, None)
    
    # Test with partial consent
    partial_consent = {"data_collection": True}
    assert not legal_validator._validate_ccpa_compliance(content, partial_consent)
    
    # Test with full consent
    full_consent = {
        "data_collection": True,
        "data_sale_opt_out": True
    }
    assert legal_validator._validate_ccpa_compliance(content, full_consent)

@pytest.mark.asyncio
async def test_content_rights():
    """Test content rights validation."""
    # Test copyrighted content
    copyrighted = "© 2025 Company Name. All rights reserved."
    assert not legal_validator._validate_content_rights(copyrighted)
    
    # Test allowed content
    allowed = "Regular user content without copyright claims"
    assert legal_validator._validate_content_rights(allowed)

@pytest.mark.asyncio
async def test_full_request_compliance():
    """Test full request compliance validation."""
    content = "Regular user content"
    region = DataRegion.EU
    
    # Test with proper consent
    consent = {
        "data_processing": True,
        "data_storage": True,
        "data_sharing": True
    }
    is_compliant, issues = legal_validator.validate_request_compliance(
        content, region, consent
    )
    assert is_compliant
    assert not issues
    
    # Test without consent
    is_compliant, issues = legal_validator.validate_request_compliance(
        content, region, None
    )
    assert not is_compliant
    assert "gdpr_requirements_not_met" in issues

@pytest.mark.asyncio
async def test_audit_logging():
    """Test audit log creation."""
    log = legal_validator.create_audit_log(
        request_id="test-123",
        user_id="user-456",
        action="predict",
        data_category="user_input",
        region=DataRegion.EU
    )
    
    assert log["request_id"] == "test-123"
    assert log["user_id"] == "user-456"
    assert log["action"] == "predict"
    assert log["data_category"] == "user_input"
    assert log["region"] == "eu"
    assert "timestamp" in log
    assert "compliance_version" in log