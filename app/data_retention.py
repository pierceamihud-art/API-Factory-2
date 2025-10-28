"""Data retention and lifecycle management module."""
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from enum import Enum

from app.supabase_backend import persist_retention_record

logger = logging.getLogger("api-factory.retention")

class RetentionPolicy(Enum):
    """Data retention policy types."""
    TRANSIENT = "transient"  # Delete immediately after processing
    SHORT_TERM = "short_term"  # Keep for 24 hours
    STANDARD = "standard"  # Keep for 30 days
    EXTENDED = "extended"  # Keep for 90 days
    PERMANENT = "permanent"  # Keep indefinitely (requires explicit justification)

class DataCategory(Enum):
    """Data categories for retention purposes."""
    USER_INPUT = "user_input"
    MODEL_OUTPUT = "model_output"
    METRICS = "metrics"
    AUDIT_LOGS = "audit_logs"
    SYSTEM_LOGS = "system_logs"

class RetentionManager:
    """Manages data retention policies and enforcement."""
    
    def __init__(self):
        self.default_policies = {
            DataCategory.USER_INPUT: RetentionPolicy.SHORT_TERM,
            DataCategory.MODEL_OUTPUT: RetentionPolicy.SHORT_TERM,
            DataCategory.METRICS: RetentionPolicy.STANDARD,
            DataCategory.AUDIT_LOGS: RetentionPolicy.EXTENDED,
            DataCategory.SYSTEM_LOGS: RetentionPolicy.STANDARD
        }
        
        # Track data items with their retention info
        self.data_registry: Dict[str, Dict] = {}
        
    def register_data(
        self,
        data_id: str,
        category: DataCategory,
        policy: Optional[RetentionPolicy] = None,
        justification: Optional[str] = None
    ) -> Dict:
        """Register a new data item for retention tracking."""
        if not policy:
            policy = self.default_policies[category]
            
        if policy == RetentionPolicy.PERMANENT and not justification:
            raise ValueError("Permanent retention requires justification")
            
        retention_info = {
            "category": category.value,
            "policy": policy.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "justification": justification,
            "delete_after": self._calculate_delete_after(policy)
        }
        
        self.data_registry[data_id] = retention_info
        persist_retention_record(data_id, retention_info)
        return retention_info
        
    def should_retain(self, data_id: str) -> bool:
        """Check if data should still be retained."""
        if data_id not in self.data_registry:
            return False
        info = self.data_registry[data_id]
        if info["policy"] == RetentionPolicy.PERMANENT.value:
            return True
        delete_after = datetime.fromisoformat(info["delete_after"])
        return datetime.now(timezone.utc) < delete_after
        
    def get_expiring_data(self, within_hours: int = 24) -> List[str]:
        """Get list of data IDs expiring within specified hours."""
        expiring = []
        check_time = datetime.now(timezone.utc) + timedelta(hours=within_hours)
        for data_id, info in self.data_registry.items():
            if info["policy"] == RetentionPolicy.PERMANENT.value:
                continue
            delete_after = datetime.fromisoformat(info["delete_after"])
            if delete_after <= check_time:
                expiring.append(data_id)
        return expiring
        
    def _calculate_delete_after(self, policy: RetentionPolicy) -> str:
        """Calculate deletion timestamp based on retention policy."""
        now = datetime.now(timezone.utc)
        if policy == RetentionPolicy.TRANSIENT:
            return now.isoformat()
        elif policy == RetentionPolicy.SHORT_TERM:
            return (now + timedelta(days=1)).isoformat()
        elif policy == RetentionPolicy.STANDARD:
            return (now + timedelta(days=30)).isoformat()
        elif policy == RetentionPolicy.EXTENDED:
            return (now + timedelta(days=90)).isoformat()
        else:  # PERMANENT
            return datetime.max.isoformat()

retention_manager = RetentionManager()  # Singleton instance