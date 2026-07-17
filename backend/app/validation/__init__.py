"""
Proof Validation Engine

Validates discovered vulnerabilities during authorized security assessments.
Generates evidence and confidence scores without data exfiltration.
"""

from app.validation.base import (
    BaseValidator,
    ValidatorRegistry,
    ValidationResult,
    ValidationStatus,
    VulnerabilityType,
    SeverityLevel,
    Evidence,
    HTTPMessage,
)

from app.validation.validators.sqli import SQLiValidator
from app.validation.validators.xss import XSSValidator
from app.validation.validators.ssrf import SSRFValidator

__all__ = [
    "BaseValidator",
    "ValidatorRegistry",
    "ValidationResult",
    "ValidationStatus",
    "VulnerabilityType",
    "SeverityLevel",
    "Evidence",
    "HTTPMessage",
    "SQLiValidator",
    "XSSValidator",
    "SSRFValidator",
]
