"""Legal compliance and data protection module."""
import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("api-factory.legal")

class DataRegion(Enum):
    """Supported data processing regions."""
    EU = "eu"
    US = "us"
    GLOBAL = "global"

class ComplianceType(Enum):
    """Types of compliance requirements."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    GENERAL = "general"

class LegalValidator:
    """Validates requests for legal compliance and data protection."""

    # Common PII patterns to check
    PII_PATTERNS = {
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b": "email",
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b": "phone_number",
        r"\b\d{3}-\d{2}-\d{4}\b": "ssn",
        r"\b(?:\d[ -]*?){13,16}\b": "credit_card",
        r"\b([A-Z][a-z]+ ){1,2}[A-Z][a-z]+\b": "full_name",
    }

    def __init__(self):
        """Initialize the validator with default settings."""
        self.tos_version = "1.0"
        self.required_disclaimers = {
            "api_usage": "This API is provided 'as is' without warranty of any kind",
            "data_processing": "Data may be processed and stored in accordance with our privacy policy",
            "content_rights": "Users must have rights to process submitted content",
        }

    def validate_request_compliance(
        self, 
        content: str,
        region: DataRegion,
        user_consent: Optional[Dict[str, bool]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate a request for legal compliance based on region and user consent.
        Returns (is_compliant, list_of_issues).
        """
        issues = []
        
        # Check for PII data that needs protection
        detected_pii = self._detect_pii(content)
        if detected_pii and not user_consent:
            issues.append("pii_without_consent")
            
        # Region-specific compliance checks
        if region == DataRegion.EU:
            if not self._validate_gdpr_compliance(content, user_consent):
                issues.append("gdpr_requirements_not_met")
        elif region == DataRegion.US:
            if not self._validate_ccpa_compliance(content, user_consent):
                issues.append("ccpa_requirements_not_met")
                
        # Check content rights/licensing
        if not self._validate_content_rights(content):
            issues.append("content_rights_unclear")
            
        return len(issues) == 0, issues

    def create_audit_log(
        self,
        request_id: str,
        user_id: str,
        action: str,
        data_category: str,
        region: DataRegion
    ) -> Dict:
        """Create a compliance audit log entry."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "action": action,
            "data_category": data_category,
            "region": region.value,
            "compliance_version": self.tos_version,
        }

    def _detect_pii(self, content: str) -> Set[str]:
        """Detect PII in content using patterns."""
        import re
        detected = set()
        for pattern, pii_type in self.PII_PATTERNS.items():
            if re.search(pattern, content):
                detected.add(pii_type)
        return detected

    def _validate_gdpr_compliance(
        self,
        content: str,
        user_consent: Optional[Dict[str, bool]]
    ) -> bool:
        """Validate GDPR compliance requirements."""
        if not user_consent:
            return False
            
        required_consents = {
            "data_processing": True,
            "data_storage": True,
            "data_sharing": True
        }
        
        return all(user_consent.get(k) for k in required_consents)

    def _validate_ccpa_compliance(
        self,
        content: str,
        user_consent: Optional[Dict[str, bool]]
    ) -> bool:
        """Validate CCPA compliance requirements."""
        if not user_consent:
            return False
            
        required_consents = {
            "data_collection": True,
            "data_sale_opt_out": True
        }
        
        return all(user_consent.get(k) for k in required_consents)

    def _validate_content_rights(self, content: str) -> bool:
        """
        Validate content for potential copyright/licensing issues.
        This is a basic check - in production use a proper rights management system.
        """
        # Check for common copyrighted content markers.
        # Allow explicit negative contexts like "without copyright" or "no copyright".
        copyright_indicators = [
            "©", "copyright", "all rights reserved",
            "confidential", "proprietary",
        ]

        lower = content.lower()
        for indicator in copyright_indicators:
            il = indicator.lower()
            if il in lower:
                # ignore cases that explicitly negate rights (e.g., "without copyright")
                if f"without {il}" in lower or f"no {il}" in lower:
                    continue
                return False
        return True

legal_validator = LegalValidator()  # Singleton instance