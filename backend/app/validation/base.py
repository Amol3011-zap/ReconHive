"""
Base validation engine for proof of concept vulnerability verification.
Validates that discovered vulnerabilities are real without data exfiltration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation lifecycle status"""
    DETECTED = "detected"  # Initial finding from reconnaissance
    NEEDS_REVIEW = "needs_review"  # Flagged for manual verification
    REPRODUCED = "reproduced"  # Analyst reproduced the issue
    CONFIRMED = "confirmed"  # Validator confirmed vulnerability
    CLIENT_VERIFIED = "client_verified"  # Client acknowledged issue


class SeverityLevel(Enum):
    """Finding severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class VulnerabilityType(Enum):
    """Supported vulnerability types"""
    SQL_INJECTION = "sql_injection"
    REFLECTED_XSS = "reflected_xss"
    STORED_XSS = "stored_xss"
    DOM_XSS = "dom_xss"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    SSRF = "ssrf"
    XXE = "xxe"
    SSTI = "ssti"
    LFI = "lfi"
    RFI = "rfi"
    OPEN_REDIRECT = "open_redirect"
    FILE_UPLOAD = "file_upload"
    API_AUTHORIZATION = "api_authorization"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"


@dataclass
class HTTPMessage:
    """HTTP request or response"""
    method: str = ""
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: str = ""
    status_code: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "status_code": self.status_code,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Evidence:
    """Evidence of vulnerability"""
    type: str  # "screenshot", "request", "response", "log", "behavior"
    content: str  # Base64-encoded image or text content
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "content_hash": hash(self.content),  # Don't expose raw content
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ValidationResult:
    """Result of vulnerability validation"""
    vulnerability_type: VulnerabilityType
    affected_url: str
    affected_parameter: str = ""
    status: ValidationStatus = ValidationStatus.DETECTED
    confidence_score: float = 0.0  # 0.0-1.0
    is_valid: bool = False
    severity: SeverityLevel = SeverityLevel.MEDIUM
    owasp_category: str = ""

    # Evidence collection
    request: Optional[HTTPMessage] = None
    response: Optional[HTTPMessage] = None
    evidence_list: List[Evidence] = field(default_factory=list)

    # Reproduction details
    payload_used: str = ""
    reproduction_steps: List[str] = field(default_factory=list)

    # Analysis
    analyst_notes: str = ""
    remediation: str = ""
    false_positive_risk: str = ""

    # Metadata
    validated_at: datetime = field(default_factory=datetime.utcnow)
    validated_by: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vulnerability_type": self.vulnerability_type.value,
            "affected_url": self.affected_url,
            "affected_parameter": self.affected_parameter,
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "is_valid": self.is_valid,
            "severity": self.severity.value,
            "owasp_category": self.owasp_category,
            "request": self.request.to_dict() if self.request else None,
            "response": self.response.to_dict() if self.response else None,
            "evidence": [e.to_dict() for e in self.evidence_list],
            "payload_used": self.payload_used,
            "reproduction_steps": self.reproduction_steps,
            "analyst_notes": self.analyst_notes,
            "remediation": self.remediation,
            "validated_at": self.validated_at.isoformat(),
            "validated_by": self.validated_by,
        }


class BaseValidator(ABC):
    """
    Abstract base for all vulnerability validators.

    Each validator:
    - Takes a target and potential vulnerability details
    - Executes non-exploitative proof-of-concept
    - Captures evidence of vulnerability existence
    - Returns validation result without data exfiltration
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.evidence_list: List[Evidence] = []

    @property
    @abstractmethod
    def validator_type(self) -> VulnerabilityType:
        """Vulnerability type this validator handles"""
        pass

    @property
    @abstractmethod
    def owasp_category(self) -> str:
        """OWASP category (e.g., 'A03: Injection')"""
        pass

    @abstractmethod
    def validate(self, target_url: str, **kwargs) -> ValidationResult:
        """
        Validate vulnerability without exploitation.
        Must return evidence that vulnerability exists, not exploit it.
        """
        pass

    def add_evidence(
        self,
        evidence_type: str,
        content: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Evidence:
        """Add evidence of vulnerability"""
        evidence = Evidence(
            type=evidence_type,
            content=content,
            description=description,
            metadata=metadata or {}
        )
        self.evidence_list.append(evidence)
        return evidence

    def create_result(
        self,
        target_url: str,
        parameter: str = "",
        is_valid: bool = False,
        confidence: float = 0.0,
        severity: SeverityLevel = SeverityLevel.MEDIUM
    ) -> ValidationResult:
        """Create validation result"""
        return ValidationResult(
            vulnerability_type=self.validator_type,
            affected_url=target_url,
            affected_parameter=parameter,
            status=ValidationStatus.CONFIRMED if is_valid else ValidationStatus.NEEDS_REVIEW,
            is_valid=is_valid,
            confidence_score=confidence,
            severity=severity,
            owasp_category=self.owasp_category,
            evidence_list=self.evidence_list.copy(),
        )

    def log_validation(
        self,
        url: str,
        finding: str,
        status: str,
        confidence: float
    ):
        """Log validation attempt"""
        self.logger.info(
            f"Validation: {self.validator_type.value} on {url}",
            extra={
                "finding": finding,
                "status": status,
                "confidence": confidence,
            }
        )


class ValidatorRegistry:
    """
    Registry for all available validators.
    Manages validator plugins and routing.
    """

    def __init__(self):
        self.validators: Dict[VulnerabilityType, BaseValidator] = {}
        self.validation_history: List[ValidationResult] = []

    def register(self, validator: BaseValidator):
        """Register a validator"""
        self.validators[validator.validator_type] = validator
        logger.info(f"Registered validator: {validator.validator_type.value}")

    def get_validator(self, vuln_type: VulnerabilityType) -> Optional[BaseValidator]:
        """Get validator for vulnerability type"""
        return self.validators.get(vuln_type)

    def list_validators(self) -> Dict[str, str]:
        """List all available validators"""
        return {
            vuln_type.value: validator.owasp_category
            for vuln_type, validator in self.validators.items()
        }

    def validate(
        self,
        vuln_type: VulnerabilityType,
        target_url: str,
        **kwargs
    ) -> Optional[ValidationResult]:
        """Validate a finding"""
        validator = self.get_validator(vuln_type)
        if not validator:
            logger.warning(f"No validator for {vuln_type.value}")
            return None

        result = validator.validate(target_url, **kwargs)
        self.validation_history.append(result)
        return result

    def get_history(self) -> List[Dict[str, Any]]:
        """Get validation history"""
        return [result.to_dict() for result in self.validation_history]

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        confirmed = sum(1 for r in self.validation_history if r.is_valid)
        total = len(self.validation_history)

        return {
            "total_validations": total,
            "confirmed": confirmed,
            "accuracy": (confirmed / total * 100) if total > 0 else 0,
            "by_type": self._group_by_type(),
            "by_severity": self._group_by_severity(),
        }

    def _group_by_type(self) -> Dict[str, int]:
        """Group results by vulnerability type"""
        groups = {}
        for result in self.validation_history:
            key = result.vulnerability_type.value
            groups[key] = groups.get(key, 0) + 1
        return groups

    def _group_by_severity(self) -> Dict[str, int]:
        """Group results by severity"""
        groups = {}
        for result in self.validation_history:
            key = result.severity.value
            groups[key] = groups.get(key, 0) + 1
        return groups
