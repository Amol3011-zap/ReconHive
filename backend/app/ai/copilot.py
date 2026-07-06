from typing import List, Dict, Any, Optional
from app.utils.logger import logger


class AICopilot:
    """AI Copilot for security assessment analysis."""

    # CWE to MITRE ATT&CK mapping (curated knowledge base)
    MITRE_CWE_MAPPING = {
        "79": "T1190",  # XSS -> Exploit Public-Facing Application
        "89": "T1190",  # SQL Injection -> Exploit Public-Facing Application
        "434": "T1566",  # Unrestricted Upload -> Phishing
        "522": "T1556",  # Weak Auth -> Modify Authentication Process
        "427": "T1105",  # Uncontrolled File Upload -> Ingress Tool Transfer
    }

    # Generic remediation patterns (no fabrication)
    REMEDIATION_PATTERNS = {
        "injection": "Use parameterized queries and input validation to prevent injection attacks.",
        "authentication": "Implement strong authentication mechanisms, MFA, and session management.",
        "encryption": "Use TLS/SSL for data in transit and encrypt sensitive data at rest.",
        "validation": "Implement comprehensive input validation and output encoding.",
        "access_control": "Implement proper authorization checks and principle of least privilege.",
    }

    @staticmethod
    def summarize_findings(findings: List[Dict[str, Any]]) -> str:
        """Summarize findings without inventing new ones."""
        if not findings:
            return "No findings detected in this assessment."

        critical = len([f for f in findings if f.get("severity") == "critical"])
        high = len([f for f in findings if f.get("severity") == "high"])
        medium = len([f for f in findings if f.get("severity") == "medium"])
        low = len([f for f in findings if f.get("severity") == "low"])

        summary = f"Assessment identified {len(findings)} findings: "
        counts = []
        if critical:
            counts.append(f"{critical} critical")
        if high:
            counts.append(f"{high} high")
        if medium:
            counts.append(f"{medium} medium")
        if low:
            counts.append(f"{low} low")

        summary += ", ".join(counts) + "."
        return summary

    @staticmethod
    def suggest_mitre_mapping(cwe_id: str) -> Optional[str]:
        """Suggest MITRE ATT&CK mapping for a CWE."""
        if cwe_id in AICopilot.MITRE_CWE_MAPPING:
            return AICopilot.MITRE_CWE_MAPPING[cwe_id]
        logger.info("mitre_mapping_not_found", cwe_id=cwe_id)
        return None

    @staticmethod
    def suggest_remediation(finding: Dict[str, Any]) -> Optional[str]:
        """Suggest remediation based on finding characteristics."""
        title = finding.get("title", "").lower()
        description = finding.get("description", "").lower()
        combined = f"{title} {description}"

        for pattern_key, remediation in AICopilot.REMEDIATION_PATTERNS.items():
            if pattern_key in combined:
                return remediation

        logger.info("remediation_suggestion_not_found", finding_id=finding.get("id"))
        return None

    @staticmethod
    def detect_duplicates(findings: List[Dict[str, Any]]) -> List[tuple]:
        """Detect likely duplicate findings (same severity, similar title)."""
        duplicates = []
        for i, finding1 in enumerate(findings):
            for finding2 in findings[i+1:]:
                if (finding1.get("severity") == finding2.get("severity") and
                    finding1.get("title").lower() == finding2.get("title").lower()):
                    duplicates.append((finding1.get("id"), finding2.get("id")))
        return duplicates

    @staticmethod
    def generate_executive_summary(engagement: Dict[str, Any], findings: List[Dict[str, Any]],
                                 scans: List[Dict[str, Any]]) -> str:
        """Generate an executive summary from engagement data."""
        summary = f"# {engagement.get('name')} Assessment Summary\n\n"
        summary += f"**Client**: {engagement.get('client')}\n"
        summary += f"**Duration**: {engagement.get('start_date')} to {engagement.get('end_date')}\n\n"

        summary += "## Assessment Coverage\n"
        summary += f"- Scans conducted: {len(scans)}\n"
        summary += f"- Findings identified: {len(findings)}\n\n"

        summary += "## Risk Profile\n"
        critical = len([f for f in findings if f.get("severity") == "critical"])
        high = len([f for f in findings if f.get("severity") == "high"])
        if critical:
            summary += f"- **Critical Issues**: {critical} findings require immediate attention\n"
        if high:
            summary += f"- **High Risk**: {high} findings should be prioritized\n"

        summary += "\n## Next Steps\n"
        summary += "1. Review and prioritize critical findings\n"
        summary += "2. Develop remediation plan\n"
        summary += "3. Track remediation progress\n"

        return summary

    @staticmethod
    def validate_finding(finding: Dict[str, Any]) -> bool:
        """Validate that finding has evidence and was not invented."""
        required_fields = ["title", "severity", "description"]
        has_evidence = bool(finding.get("evidence_ids"))

        if not all(field in finding for field in required_fields):
            logger.warning("finding_incomplete", finding_id=finding.get("id"))
            return False

        if not has_evidence:
            logger.warning("finding_no_evidence", finding_id=finding.get("id"))
            return False

        return True
