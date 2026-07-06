from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
from app.utils.logger import logger


class NormalizedDataType(str, Enum):
    """Types of normalized data."""
    VULNERABILITY = "vulnerability"
    HOST = "host"
    SERVICE = "service"
    CREDENTIAL = "credential"
    DATA_EXPOSURE = "data_exposure"
    CONFIGURATION = "configuration"
    CUSTOM = "custom"


class Severity(str, Enum):
    """Severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class NormalizedResult:
    """Standardized result from plugin execution."""
    data_type: NormalizedDataType
    severity: Severity
    title: str
    description: str
    evidence: Dict[str, Any]
    affected_assets: List[str]
    remediation: Optional[str] = None
    cwe_ids: List[str] = None
    cvss_score: Optional[float] = None
    tags: List[str] = None
    raw_data: Optional[Dict] = None

    def __post_init__(self):
        if self.cwe_ids is None:
            self.cwe_ids = []
        if self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class ResultNormalizer:
    """Normalize plugin outputs to standard format."""

    # Mapping of severity keywords to standard severity levels
    SEVERITY_MAP = {
        "critical": Severity.CRITICAL,
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "low": Severity.LOW,
        "info": Severity.INFO,
        "informational": Severity.INFO,
        "warning": Severity.HIGH,
        "error": Severity.CRITICAL,
        "severe": Severity.CRITICAL,
        "major": Severity.HIGH,
        "minor": Severity.LOW,
    }

    @staticmethod
    def normalize_vulnerability(raw_result: Dict[str, Any]) -> NormalizedResult:
        """Normalize vulnerability finding."""
        try:
            severity = ResultNormalizer._parse_severity(raw_result.get("severity", "medium"))
            cvss = raw_result.get("cvss_score")
            if isinstance(cvss, str):
                try:
                    cvss = float(cvss)
                except (ValueError, TypeError):
                    cvss = None

            return NormalizedResult(
                data_type=NormalizedDataType.VULNERABILITY,
                severity=severity,
                title=raw_result.get("title", "Unnamed Vulnerability"),
                description=raw_result.get("description", ""),
                evidence=raw_result.get("evidence", {}),
                affected_assets=raw_result.get("affected_assets", []),
                remediation=raw_result.get("remediation"),
                cwe_ids=raw_result.get("cwe_ids", []),
                cvss_score=cvss,
                tags=raw_result.get("tags", []),
                raw_data=raw_result,
            )
        except Exception as e:
            logger.error("normalization_failed", error=str(e))
            raise

    @staticmethod
    def normalize_host(raw_result: Dict[str, Any]) -> NormalizedResult:
        """Normalize host discovery."""
        return NormalizedResult(
            data_type=NormalizedDataType.HOST,
            severity=Severity.INFO,
            title=f"Host discovered: {raw_result.get('hostname', raw_result.get('ip', 'unknown'))}",
            description=raw_result.get("description", ""),
            evidence=raw_result.get("evidence", {}),
            affected_assets=[raw_result.get("ip", "")],
            tags=raw_result.get("tags", ["host"]),
            raw_data=raw_result,
        )

    @staticmethod
    def normalize_service(raw_result: Dict[str, Any]) -> NormalizedResult:
        """Normalize service discovery."""
        return NormalizedResult(
            data_type=NormalizedDataType.SERVICE,
            severity=Severity.INFO,
            title=f"Service: {raw_result.get('service_name', 'unknown')} on {raw_result.get('port', '?')}",
            description=raw_result.get("description", ""),
            evidence=raw_result.get("evidence", {}),
            affected_assets=raw_result.get("affected_assets", []),
            tags=raw_result.get("tags", ["service"]),
            raw_data=raw_result,
        )

    @staticmethod
    def normalize_credential(raw_result: Dict[str, Any]) -> NormalizedResult:
        """Normalize credential finding."""
        return NormalizedResult(
            data_type=NormalizedDataType.CREDENTIAL,
            severity=Severity.CRITICAL,
            title=f"Credential exposed: {raw_result.get('credential_type', 'unknown')}",
            description=raw_result.get("description", ""),
            evidence=raw_result.get("evidence", {}),
            affected_assets=raw_result.get("affected_assets", []),
            remediation="Rotate credentials immediately",
            tags=raw_result.get("tags", ["credential", "critical"]),
            raw_data=raw_result,
        )

    @staticmethod
    def normalize_data_exposure(raw_result: Dict[str, Any]) -> NormalizedResult:
        """Normalize data exposure finding."""
        severity = ResultNormalizer._parse_severity(raw_result.get("severity", "high"))
        return NormalizedResult(
            data_type=NormalizedDataType.DATA_EXPOSURE,
            severity=severity,
            title=raw_result.get("title", "Sensitive data exposed"),
            description=raw_result.get("description", ""),
            evidence=raw_result.get("evidence", {}),
            affected_assets=raw_result.get("affected_assets", []),
            remediation="Restrict access and monitor for unauthorized access",
            tags=raw_result.get("tags", ["data", "exposure"]),
            raw_data=raw_result,
        )

    @staticmethod
    def normalize(result_type: str, raw_result: Dict[str, Any]) -> NormalizedResult:
        """Normalize result based on type."""
        normalizers = {
            "vulnerability": ResultNormalizer.normalize_vulnerability,
            "host": ResultNormalizer.normalize_host,
            "service": ResultNormalizer.normalize_service,
            "credential": ResultNormalizer.normalize_credential,
            "data_exposure": ResultNormalizer.normalize_data_exposure,
        }

        normalizer = normalizers.get(result_type.lower())
        if not normalizer:
            logger.warning("unknown_result_type", result_type=result_type)
            normalizer = ResultNormalizer.normalize_vulnerability

        return normalizer(raw_result)

    @staticmethod
    def _parse_severity(severity_input: Any) -> Severity:
        """Parse severity from various formats."""
        if isinstance(severity_input, Severity):
            return severity_input

        if isinstance(severity_input, str):
            normalized = severity_input.lower().strip()
            return ResultNormalizer.SEVERITY_MAP.get(normalized, Severity.MEDIUM)

        if isinstance(severity_input, int):
            if severity_input >= 90:
                return Severity.CRITICAL
            elif severity_input >= 70:
                return Severity.HIGH
            elif severity_input >= 50:
                return Severity.MEDIUM
            elif severity_input >= 30:
                return Severity.LOW
            else:
                return Severity.INFO

        return Severity.MEDIUM


# Global normalizer instance
result_normalizer = ResultNormalizer()
