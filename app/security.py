"""Security utilities for API hardening."""
import re
from typing import Tuple, List

class SecurityValidator:
    # Characters that might indicate injection attempts
    SUSPICIOUS_PATTERNS = [
        r"<[^>]*script.*?>",  # Script tags
        r"{{.*}}",  # Template injection
        r"\$where:",  # NoSQL injection
        r"(?i)(select|union|insert|drop|delete|update)\s+.*",  # SQL injection
        r"^\s*[;|()`]",  # Command injection
    ]
    
    # Minimum API key requirements
    MIN_API_KEY_LENGTH = 32
    API_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{32,}$")
    
    @classmethod
    def validate_input(cls, text: str) -> Tuple[bool, List[str]]:
        """Validate input for suspicious patterns."""
        issues = []
        
        # Check for suspicious patterns
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, text):
                issues.append("suspicious_pattern_detected")
                
        # Check for potential command injection
        if any(char in text for char in ';&|$()`'):
            issues.append("command_injection_risk")
            
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', text)) / len(text) if text else 0
        if special_char_ratio > 0.3:  # If more than 30% special chars
            issues.append("excessive_special_chars")
            
        return len(issues) == 0, issues

    @classmethod
    def validate_api_key(cls, api_key: str) -> Tuple[bool, List[str]]:
        """Validate API key format and strength."""
        issues = []
        
        if len(api_key) < cls.MIN_API_KEY_LENGTH:
            issues.append("api_key_too_short")
            
        if not cls.API_KEY_PATTERN.match(api_key):
            issues.append("api_key_invalid_format")
            
        # Check for sequential or repeated patterns
        if any(str(i) * 4 in api_key for i in range(10)):
            issues.append("api_key_sequential_pattern")
            
        return len(issues) == 0, issues

security_validator = SecurityValidator()