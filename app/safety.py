"""Content safety and validation module."""
import re
from typing import List, Tuple
import logging

logger = logging.getLogger("api-factory")

# Extended profanity/safety list - this would normally be loaded from a managed list
UNSAFE_PATTERNS = {
    # Placeholder patterns - in production use a proper content classifier
    r"\b(malware|exploit|hack|crack)\b": "security",
    r"\b(http|www|\.com)\b": "urls",
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b": "emails",
    r"\b\d{3}-?\d{2}-?\d{4}\b": "ssn",
    r"\b\d{16}\b": "credit_card",
    r"\b(kill|hurt|harm)\b": "violence",
    r"\b(damn|hell)\b": "mild_profanity",
    r"\b(racist|sexist)\b": "hate_speech"
}

class ContentValidator:
    """Validates and sanitizes input content."""
    
    def __init__(self):
        self.patterns = {re.compile(k, re.I): v for k, v in UNSAFE_PATTERNS.items()}
        
    def validate(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate text content against safety rules.
        Returns (is_safe, list_of_issues).
        """
        issues = []
        
        if not text or not text.strip():
            issues.append("empty_input")
            return False, issues
            
        # Check against patterns
        for pattern, issue_type in self.patterns.items():
            if pattern.search(text):
                issues.append(issue_type)
                
        # Check other rules
        if len(text.split()) > 500:  # Arbitrary word limit
            issues.append("too_many_words")
            
        if len(set(text.split())) < len(text.split()) * 0.3:
            issues.append("repetitive_content")
            
        return len(issues) == 0, issues

    def get_toxicity_score(self, text: str) -> float:
        """
        Get a basic toxicity score 0-1.
        In production, this would use a proper ML model.
        """
        _, issues = self.validate(text)
        # Simple scoring based on number and type of issues
        score = len(issues) * 0.2  # 0.2 per issue
        return min(1.0, score)  # Cap at 1.0

content_validator = ContentValidator()  # Singleton instance