"""Audit trail with cryptographic integrity verification."""
import json
import hashlib
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from collections import deque

from app.privacy import privacy_manager, AnonymizationLevel
from app.supabase_backend import persist_audit_entry

logger = logging.getLogger("api-factory.audit")

AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH")
LOG_REDACT_PII = os.getenv("LOG_REDACT_PII", "true").lower() in ("1", "true", "yes")

class AuditEntry:
    """Immutable audit log entry with cryptographic linking."""
    
    def __init__(
        self,
        action: str,
        user_id: str,
        resource_id: str,
        details: Dict,
        previous_hash: Optional[str] = None
    ):
        self.timestamp = datetime.now(timezone.utc)
        self.action = action
        self.user_id = user_id
        self.resource_id = resource_id
        self.details = details
        self.previous_hash = previous_hash
        self.entry_hash = self._calculate_hash()
        
    def _calculate_hash(self) -> str:
        """Calculate cryptographic hash of the entry."""
        data = {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "details": self.details,
            "previous_hash": self.previous_hash
        }
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        
    def to_dict(self) -> Dict:
        """Convert entry to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "details": self.details,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash
        }

class AuditTrail:
    """Maintains a cryptographically linked audit trail."""
    
    def __init__(self, max_memory_entries: int = 1000, sink_path: Optional[str] = None):
        self.entries: deque = deque(maxlen=max_memory_entries)
        self.last_hash: Optional[str] = None
        self.sink_path = sink_path or AUDIT_LOG_PATH
        
    def add_entry(
        self,
        action: str,
        user_id: str,
        resource_id: str,
        details: Dict
    ) -> AuditEntry:
        """Add a new entry to the audit trail."""
        # Determine the most recent entry for the same resource_id to create
        # a per-resource chain. This allows independent chains for different
        # resources so tests and multi-tenant workloads do not interfere.
        previous = None
        for e in reversed(self.entries):
            if e.resource_id == resource_id:
                previous = e.entry_hash
                break

        entry = AuditEntry(
            action=action,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            previous_hash=previous
        )

        self.entries.append(entry)
        # Update global last_hash as an overall pointer (not used for per-resource chaining)
        self.last_hash = entry.entry_hash
        # Prepare payload and optionally redact PII before external persist/log
        payload = entry.to_dict()
        safe_payload = self._redact_payload(payload) if LOG_REDACT_PII else payload

        # Log entry for external persistence (PII-safe if enabled)
        logger.info("Audit entry: %s", json.dumps(safe_payload))
        self._persist_entry(safe_payload)
        persist_audit_entry(safe_payload)

        return entry
        
    def verify_integrity(self, start_index: int = 0) -> bool:
        """Verify the integrity of the audit trail."""
        if not self.entries:
            return True

        entries_list = list(self.entries)
        # Validate per-resource chaining: each entry's previous_hash must point
        # to the most recent prior entry with the same resource_id (if any).
        for i, current in enumerate(entries_list[start_index:], start=start_index):
            # If there is no previous_hash, ensure no prior entry exists for same resource
            if current.previous_hash is None:
                for prior in entries_list[:i]:
                    if prior.resource_id == current.resource_id:
                        logger.error(
                            "Audit trail integrity broken: missing previous_hash for resource %s at index %d",
                            current.resource_id, i
                        )
                        return False
                continue

            # Find most recent prior entry with same resource_id
            found = None
            for prior in reversed(entries_list[:i]):
                if prior.resource_id == current.resource_id:
                    found = prior
                    break

            if not found or current.previous_hash != found.entry_hash:
                logger.error(
                    "Audit trail integrity broken for resource %s at index %d",
                    current.resource_id, i
                )
                return False

        return True
        
    def get_entries(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Get filtered audit entries."""
        filtered = []
        
        for entry in self.entries:
            if user_id and entry.user_id != user_id:
                continue
            if action and entry.action != action:
                continue
            if resource_id and entry.resource_id != resource_id:
                continue
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
                
            filtered.append(entry.to_dict())
            
        return filtered
        
    def get_user_actions(
        self,
        user_id: str,
        start_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Get all actions by a specific user."""
        return self.get_entries(user_id=user_id, start_time=start_time)
        
    def get_resource_history(
        self,
        resource_id: str,
        start_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Get complete history for a specific resource."""
        return self.get_entries(resource_id=resource_id, start_time=start_time)

    def _redact_payload(self, payload: Dict) -> Dict:
        """Redact sensitive values from payload before external exposure."""
        try:
            redacted = payload.copy()
            redacted["details"] = self._redact_value(redacted.get("details"))
            return redacted
        except Exception:
            logger.exception("Failed to redact audit payload; falling back to original")
            return payload

    def _redact_value(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            redacted, _ = privacy_manager.anonymize_data(value, AnonymizationLevel.PARTIAL)
            return redacted
        if isinstance(value, dict):
            return {k: self._redact_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._redact_value(v) for v in value]
        return value

    def _persist_entry(self, payload: Dict) -> None:
        if not self.sink_path:
            return
        try:
            path = Path(self.sink_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload) + "\n")
        except Exception:
            logger.exception("Failed to persist audit entry to %s", self.sink_path)

audit_trail = AuditTrail()  # Singleton instance