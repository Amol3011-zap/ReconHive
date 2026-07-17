"""
SQL Injection Validator

Validates SQL injection vulnerabilities by:
- Testing for error-based injection
- Testing for boolean-based injection
- Testing for time-based injection
- Comparing response differences
- Documenting affected parameters
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode, urlparse, parse_qs

from app.validation.base import (
    BaseValidator,
    ValidationResult,
    ValidationStatus,
    VulnerabilityType,
    SeverityLevel,
    HTTPMessage,
)
from app.validation.payloads import PayloadLibrary, PayloadManager

logger = logging.getLogger(__name__)


class SQLiValidator(BaseValidator):
    """Validates SQL injection vulnerabilities"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.payload_manager = PayloadManager()
        self.database_type = "mysql"

    @property
    def validator_type(self) -> VulnerabilityType:
        return VulnerabilityType.SQL_INJECTION

    @property
    def owasp_category(self) -> str:
        return "A03: Injection"

    def validate(
        self,
        target_url: str,
        parameter: str = "",
        method: str = "GET",
        **kwargs
    ) -> ValidationResult:
        """
        Validate SQL injection without exploitation.

        Tests:
        1. Error-based: Look for SQL error messages
        2. Boolean-based: Compare responses with AND conditions
        3. Time-based: Measure response timing
        """

        result = self.create_result(
            target_url=target_url,
            parameter=parameter,
            severity=SeverityLevel.HIGH,
        )

        try:
            # Phase 1: Error-based detection
            error_result = self._test_error_based(target_url, parameter, method)
            if error_result:
                result.is_valid = True
                result.confidence_score = 0.9
                result.reproduction_steps.append("1. Send payload with SQL syntax error")
                result.reproduction_steps.append("2. Observe SQL error message in response")
                result.payload_used = error_result["payload"]
                self.add_evidence(
                    "response",
                    error_result["error_message"],
                    "SQL error message indicating injection point"
                )
                self.log_validation(
                    target_url,
                    "Error-based SQL injection",
                    "CONFIRMED",
                    result.confidence_score
                )
                result.remediation = "Use parameterized queries or prepared statements"
                return result

            # Phase 2: Boolean-based detection
            boolean_result = self._test_boolean_based(target_url, parameter, method)
            if boolean_result:
                result.is_valid = True
                result.confidence_score = 0.85
                result.reproduction_steps.append("1. Send AND 1=1 payload")
                result.reproduction_steps.append("2. Compare response with AND 1=2 payload")
                result.reproduction_steps.append("3. Observe different responses indicating injection")
                result.payload_used = boolean_result["payload"]
                self.add_evidence(
                    "behavior",
                    f"Response differs by {boolean_result['diff_chars']} chars",
                    "Boolean-based SQL injection confirmed"
                )
                self.log_validation(
                    target_url,
                    "Boolean-based SQL injection",
                    "CONFIRMED",
                    result.confidence_score
                )
                result.remediation = "Use parameterized queries or prepared statements"
                return result

            # Phase 3: Time-based detection
            time_result = self._test_time_based(target_url, parameter, method)
            if time_result:
                result.is_valid = True
                result.confidence_score = 0.8
                result.reproduction_steps.append("1. Send time-based payload with SLEEP/BENCHMARK")
                result.reproduction_steps.append("2. Measure response time")
                result.reproduction_steps.append("3. Observe delayed response indicating injection")
                result.payload_used = time_result["payload"]
                self.add_evidence(
                    "behavior",
                    f"Response delayed by {time_result['delay']:.2f} seconds",
                    "Time-based SQL injection confirmed"
                )
                self.log_validation(
                    target_url,
                    "Time-based SQL injection",
                    "CONFIRMED",
                    result.confidence_score
                )
                result.remediation = "Use parameterized queries or prepared statements"
                return result

        except Exception as e:
            logger.error(f"SQLi validation error: {str(e)}")
            result.status = ValidationStatus.NEEDS_REVIEW
            result.analyst_notes = f"Validation error: {str(e)}"

        result.status = ValidationStatus.NEEDS_REVIEW
        return result

    def _test_error_based(
        self,
        url: str,
        parameter: str,
        method: str
    ) -> Optional[Dict[str, Any]]:
        """Test for error-based SQL injection"""

        if not parameter:
            return None

        # Get payloads from library
        error_payloads = PayloadLibrary.get_sql_payloads(self.database_type)

        try:
            for payload in error_payloads:
                request, response = self._make_request(
                    url,
                    parameter,
                    payload,
                    method
                )

                # Check for SQL error messages
                error_indicators = [
                    "SQL syntax",
                    "mysql_fetch",
                    "Warning: mysql",
                    "ORA-",  # Oracle
                    "Incorrect syntax",  # MSSQL
                    "PostgreSQL",
                    "SQLite",
                    "UNION SELECT",
                ]

                response_text = response.text.lower() if response else ""
                for indicator in error_indicators:
                    if indicator.lower() in response_text:
                        return {
                            "payload": payload,
                            "error_message": response.text[:500],
                        }

        except Exception as e:
            logger.debug(f"Error-based test failed: {str(e)}")

        return None

    def _test_boolean_based(
        self,
        url: str,
        parameter: str,
        method: str
    ) -> Optional[Dict[str, Any]]:
        """Test for boolean-based blind SQL injection"""

        if not parameter:
            return None

        try:
            # Get baseline response
            _, baseline = self._make_request(url, parameter, "1", method)
            if not baseline:
                return None

            baseline_len = len(baseline.text)

            # Test with TRUE condition
            _, response_true = self._make_request(
                url,
                parameter,
                "1' AND '1'='1",
                method
            )

            # Test with FALSE condition
            _, response_false = self._make_request(
                url,
                parameter,
                "1' AND '1'='2",
                method
            )

            if response_true and response_false:
                diff = len(response_true.text) - len(response_false.text)

                # Significant difference indicates boolean-based injection
                if abs(diff) > 50:  # Threshold for significant difference
                    return {
                        "payload": "1' AND '1'='1",
                        "diff_chars": abs(diff),
                    }

        except Exception as e:
            logger.debug(f"Boolean-based test failed: {str(e)}")

        return None

    def _test_time_based(
        self,
        url: str,
        parameter: str,
        method: str
    ) -> Optional[Dict[str, Any]]:
        """Test for time-based blind SQL injection"""

        if not parameter:
            return None

        time_payloads = [
            ("1' AND SLEEP(5) --", 5),  # MySQL
            ("1' AND BENCHMARK(50000000,MD5('test')) --", 3),  # MySQL
            ("1' AND (SELECT SLEEP(5)) --", 5),  # MySQL
            ("1' WAITFOR DELAY '00:00:05' --", 5),  # MSSQL
        ]

        try:
            for payload, expected_delay in time_payloads:
                start = time.time()
                _, response = self._make_request(url, parameter, payload, method)
                elapsed = time.time() - start

                # If response took significantly longer, time-based injection likely
                if elapsed >= (expected_delay * 0.8):  # Allow 20% margin
                    return {
                        "payload": payload,
                        "delay": elapsed,
                    }

        except Exception as e:
            logger.debug(f"Time-based test failed: {str(e)}")

        return None

    def _make_request(
        self,
        url: str,
        parameter: str,
        payload: str,
        method: str
    ) -> Tuple[Optional[HTTPMessage], Optional[requests.Response]]:
        """Make HTTP request with payload"""

        try:
            headers = {
                "User-Agent": "ReconHive/1.0",
                "Accept": "*/*",
            }

            if method.upper() == "GET":
                # Parse URL and modify parameter
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params[parameter] = [payload]
                query_string = urlencode(params, doseq=True)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query_string}"

                response = requests.get(
                    test_url,
                    headers=headers,
                    timeout=10,
                    verify=False
                )
            else:
                # POST request
                response = requests.post(
                    url,
                    data={parameter: payload},
                    headers=headers,
                    timeout=10,
                    verify=False
                )

            request = HTTPMessage(
                method=method,
                url=url,
                headers=headers,
                body=payload,
            )

            return request, response

        except Exception as e:
            logger.debug(f"Request failed: {str(e)}")
            return None, None
