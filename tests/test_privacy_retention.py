"""Tests for privacy and retention features."""
import pytest
from app.privacy import privacy_manager, PrivacyTier, AnonymizationLevel
from app.data_retention import retention_manager, DataCategory, RetentionPolicy
from app.audit import audit_trail

@pytest.mark.asyncio
async def test_privacy_classification():
    """Test privacy tier classification."""
    # Test public data
    text = "This is public information"
    tier, elements = privacy_manager.classify_privacy_tier(text)
    assert tier == PrivacyTier.PUBLIC
    assert not elements

    # Test sensitive data
    text = "My credit card is 4111-1111-1111-1111"
    tier, elements = privacy_manager.classify_privacy_tier(text)
    assert tier == PrivacyTier.SENSITIVE
    assert "credit_card" in elements

@pytest.mark.asyncio
async def test_data_anonymization():
    """Test data anonymization."""
    text = "Contact John at john@example.com or 555-123-4567"
    
    # Test partial anonymization
    anon_text, stats = privacy_manager.anonymize_data(text, AnonymizationLevel.PARTIAL)
    assert "john@example.com" not in anon_text
    assert "555-123-4567" not in anon_text
    assert stats["replacements"] > 0

    # Test full anonymization
    anon_text, stats = privacy_manager.anonymize_data(text, AnonymizationLevel.FULL)
    assert "[REDACTED]" in anon_text
    assert stats["replacements"] > 0

@pytest.mark.asyncio
async def test_retention_management():
    """Test data retention management."""
    # Test standard retention
    retention_info = retention_manager.register_data(
        "test-123",
        DataCategory.USER_INPUT,
        RetentionPolicy.STANDARD
    )
    assert retention_info["policy"] == RetentionPolicy.STANDARD.value
    assert retention_manager.should_retain("test-123")

    # Test permanent retention (should fail without justification)
    with pytest.raises(ValueError):
        retention_manager.register_data(
            "test-456",
            DataCategory.USER_INPUT,
            RetentionPolicy.PERMANENT
        )

    # Test expiring data detection
    retention_info = retention_manager.register_data(
        "test-789",
        DataCategory.USER_INPUT,
        RetentionPolicy.SHORT_TERM
    )
    expiring = retention_manager.get_expiring_data(within_hours=48)
    assert "test-789" in expiring

@pytest.mark.asyncio
async def test_audit_trail():
    """Test audit trail functionality."""
    # Add an entry
    entry = audit_trail.add_entry(
        action="test_action",
        user_id="test_user",
        resource_id="test_resource",
        details={"test": "data"}
    )
    assert entry.entry_hash
    assert entry.previous_hash is None  # First entry

    # Add another entry and verify chain
    entry2 = audit_trail.add_entry(
        action="test_action_2",
        user_id="test_user",
        resource_id="test_resource",
        details={"test": "data2"}
    )
    assert entry2.previous_hash == entry.entry_hash
    assert audit_trail.verify_integrity()

    # Test filtering
    entries = audit_trail.get_user_actions("test_user")
    assert len(entries) == 2
    assert entries[0]["action"] == "test_action"