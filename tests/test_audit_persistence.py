import json

import pytest

from app.audit import AuditTrail


def test_audit_persists_to_file(tmp_path, monkeypatch):
    log_file = tmp_path / "audit.log"
    # Ensure redaction is enabled during test
    monkeypatch.setattr("app.audit.LOG_REDACT_PII", True, raising=False)

    trail = AuditTrail(sink_path=str(log_file))
    entry = trail.add_entry(
        action="predict",
        user_id="user123",
        resource_id="resource123",
        details={"pii": "john@example.com"}
    )

    assert log_file.exists(), "Audit log file should be created"
    payloads = [json.loads(line) for line in log_file.read_text().splitlines() if line.strip()]
    assert payloads, "Audit log should contain at least one entry"

    saved = payloads[-1]
    assert saved["entry_hash"] == entry.entry_hash
    assert saved["resource_id"] == "resource123"
    # Redaction should remove raw email from persisted payload
    assert "john@example.com" not in json.dumps(saved["details"])
    assert trail.verify_integrity(), "Audit trail integrity check should pass"
