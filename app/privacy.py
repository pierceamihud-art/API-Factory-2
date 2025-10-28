"""Data privacy and anonymization module."""
import re
import logging
from typing import Dict, List, Tuple
from enum import Enum

logger = logging.getLogger("api-factory.privacy")

class PrivacyTier(Enum):
    """Privacy tier levels for data handling."""
    PUBLIC = "public"  # No PII, freely shareable
    INTERNAL = "internal"  # Business data, limited sharing
    RESTRICTED = "restricted"  # Contains PII, strict controls
    SENSITIVE = "sensitive"  # Special category data (health, biometric, etc)

class AnonymizationLevel(Enum):
    """Levels of data anonymization."""
    NONE = "none"  # No anonymization
    PARTIAL = "partial"  # Replace obvious identifiers
    FULL = "full"  # Complete anonymization
    SYNTHETIC = "synthetic"  # Replace with synthetic data

class PrivacyManager:
    """Manages data privacy and anonymization."""
    
    # Patterns for identifying sensitive data types
    SENSITIVE_PATTERNS = {
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
        "ssn": r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",
        "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "address": r"\b\d+\s+([A-Za-z]+ ){1,3}(St|Street|Rd|Road|Ave|Avenue|Blvd|Boulevard)\b",
    }
    
    def __init__(self):
        """Initialize with compiled regex patterns."""
        self.patterns = {k: re.compile(v) for k, v in self.SENSITIVE_PATTERNS.items()}
        
    def classify_privacy_tier(self, text: str) -> Tuple[PrivacyTier, List[str]]:
        """Determine privacy tier based on content analysis."""
        found_patterns = []
        
        # Check for sensitive patterns
        for pattern_name, pattern in self.patterns.items():
            if pattern.search(text):
                found_patterns.append(pattern_name)
                
        # Determine tier based on findings
        if any(p in ["credit_card", "ssn"] for p in found_patterns):
            return PrivacyTier.SENSITIVE, found_patterns
        elif found_patterns:
            return PrivacyTier.RESTRICTED, found_patterns
        elif len(text.split()) > 100:  # Arbitrary length for potential internal data
            return PrivacyTier.INTERNAL, ["length_based"]
        else:
            return PrivacyTier.PUBLIC, []

    def anonymize_data(
        self,
        text: str,
        level: AnonymizationLevel
    ) -> Tuple[str, Dict[str, int]]:
        """Anonymize text based on specified level."""
        if level == AnonymizationLevel.NONE:
            return text, {}
            
        stats = {"replacements": 0}
        result = text
        
        if level in [AnonymizationLevel.PARTIAL, AnonymizationLevel.FULL]:
            # Replace sensitive patterns
            for pattern_name, pattern in self.patterns.items():
                def replace_func(match):
                    stats["replacements"] += 1
                    if level == AnonymizationLevel.PARTIAL:
                        # Keep last 4 digits for some types
                        if pattern_name in ["credit_card", "phone"]:
                            return f"****{match.group()[-4:]}"
                    return "[REDACTED]"
                    
                result = pattern.sub(replace_func, result)
                
        if level == AnonymizationLevel.SYNTHETIC:
            # Replace with realistic-looking synthetic data
            # This is a simple example - in production use proper synthetic data generation
            result = self._generate_synthetic_replacement(text)
            stats["replacements"] = 1
            
        return result, stats

    def _generate_synthetic_replacement(self, original: str) -> str:
        """Generate synthetic replacement maintaining statistical properties."""
        # This is a placeholder - in production use proper synthetic data generation
        word_count = len(original.split())
        return " ".join([f"synthetic_word_{i}" for i in range(word_count)])

    def get_privacy_requirements(
        self,
        tier: PrivacyTier
    ) -> Dict[str, List[str]]:
        """Get handling requirements for privacy tier."""
        base_requirements = ["encryption_at_rest", "access_logging"]
        
        if tier == PrivacyTier.SENSITIVE:
            return {
                "storage": base_requirements + ["secure_enclave", "redundancy"],
                "transport": ["tls_1_3", "client_certificates"],
                "access": ["mfa", "role_based", "purpose_limitation"],
                "retention": ["max_90_days", "secure_deletion"],
            }
        elif tier == PrivacyTier.RESTRICTED:
            return {
                "storage": base_requirements + ["redundancy"],
                "transport": ["tls_1_2_min"],
                "access": ["role_based", "purpose_limitation"],
                "retention": ["max_180_days"],
            }
        elif tier == PrivacyTier.INTERNAL:
            return {
                "storage": base_requirements,
                "transport": ["tls_1_2_min"],
                "access": ["authenticated"],
                "retention": ["standard_policy"],
            }
        else:  # PUBLIC
            return {
                "storage": ["basic_backup"],
                "transport": ["tls_1_2_min"],
                "access": ["rate_limited"],
                "retention": ["standard_policy"],
            }

privacy_manager = PrivacyManager()  # Singleton instance