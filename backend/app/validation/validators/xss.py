"""
XSS Validator

Validates XSS vulnerabilities by:
- Testing reflected XSS payload execution
- Testing stored XSS persistence
- Testing DOM XSS via JavaScript execution
- Capturing payload execution evidence
"""

import re
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode, urlparse, parse_qs

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.validation.base import (
    BaseValidator,
    ValidationResult,
    ValidationStatus,
    VulnerabilityType,
    SeverityLevel,
)
from app.validation.payloads import PayloadLibrary, PayloadManager

logger = logging.getLogger(__name__)


class XSSValidator(BaseValidator):
    """Validates XSS vulnerabilities"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.xss_type = "reflected"  # reflected, stored, dom
        self.payload_manager = PayloadManager()

    @property
    def validator_type(self) -> VulnerabilityType:
        return VulnerabilityType.REFLECTED_XSS

    @property
    def owasp_category(self) -> str:
        return "A03: Injection"

    def validate(
        self,
        target_url: str,
        parameter: str = "",
        xss_type: str = "reflected",
        **kwargs
    ) -> ValidationResult:
        """
        Validate XSS without data theft or malicious execution.

        Tests:
        1. Reflected XSS: Payload echoed in response
        2. Stored XSS: Payload persisted in database and returned
        3. DOM XSS: Payload executed in JavaScript context
        """

        self.xss_type = xss_type
        result = self.create_result(
            target_url=target_url,
            parameter=parameter,
            severity=SeverityLevel.HIGH,
        )

        try:
            if xss_type == "reflected":
                return self._validate_reflected(target_url, parameter, result)
            elif xss_type == "stored":
                return self._validate_stored(target_url, parameter, result)
            elif xss_type == "dom":
                return self._validate_dom(target_url, parameter, result)

        except Exception as e:
            logger.error(f"XSS validation error: {str(e)}")
            result.status = ValidationStatus.NEEDS_REVIEW
            result.analyst_notes = f"Validation error: {str(e)}"

        return result

    def _validate_reflected(
        self,
        url: str,
        parameter: str,
        result: ValidationResult
    ) -> ValidationResult:
        """Validate reflected XSS"""

        if not parameter:
            return result

        # Get payloads from library
        payloads = PayloadLibrary.get_xss_payloads("reflected")

        try:
            for payload in payloads:
                response = self._send_payload(url, parameter, payload)

                if response and self._is_payload_reflected(response.text, payload):
                    result.is_valid = True
                    result.confidence_score = 0.95
                    result.payload_used = payload
                    result.status = ValidationStatus.CONFIRMED

                    result.reproduction_steps = [
                        f"1. Visit {url}?{parameter}={payload}",
                        "2. Observe payload reflected in HTML without escaping",
                        "3. Browser executes JavaScript payload",
                    ]

                    self.add_evidence(
                        "response",
                        response.text[:500],
                        f"Payload reflected without HTML encoding: {payload}"
                    )

                    result.remediation = (
                        "1. HTML-encode all user input in output\n"
                        "2. Use Content Security Policy (CSP)\n"
                        "3. Use templating engines with auto-escaping\n"
                        "4. Input validation for expected formats"
                    )

                    self.log_validation(
                        url,
                        "Reflected XSS",
                        "CONFIRMED",
                        result.confidence_score
                    )
                    return result

        except Exception as e:
            logger.debug(f"Reflected XSS test failed: {str(e)}")

        result.status = ValidationStatus.NEEDS_REVIEW
        return result

    def _validate_stored(
        self,
        url: str,
        parameter: str,
        result: ValidationResult
    ) -> ValidationResult:
        """Validate stored XSS"""

        # Non-malicious payload that proves storage and retrieval
        test_payload = '<svg onload="console.log(\'stored_xss_test\')">'
        test_marker = "xss_test_marker_12345"

        try:
            # POST data with payload
            response = self._send_payload(url, parameter, test_payload, method="POST")

            if response:
                # Check if payload was stored (try to retrieve it)
                get_response = requests.get(url, timeout=10, verify=False)

                if test_marker in get_response.text or test_payload in get_response.text:
                    result.is_valid = True
                    result.confidence_score = 0.9
                    result.payload_used = test_payload
                    result.status = ValidationStatus.CONFIRMED

                    result.reproduction_steps = [
                        f"1. Submit form with payload: {test_payload}",
                        "2. Payload is stored in database",
                        "3. Reload page and payload executes in browser",
                    ]

                    self.add_evidence(
                        "behavior",
                        f"Payload persisted in response",
                        "Stored XSS confirmed"
                    )

                    result.remediation = (
                        "1. Sanitize user input on server-side\n"
                        "2. Use Content Security Policy\n"
                        "3. Never trust user input\n"
                        "4. Store raw data, encode on output"
                    )

                    self.log_validation(
                        url,
                        "Stored XSS",
                        "CONFIRMED",
                        result.confidence_score
                    )
                    return result

        except Exception as e:
            logger.debug(f"Stored XSS test failed: {str(e)}")

        result.status = ValidationStatus.NEEDS_REVIEW
        return result

    def _validate_dom(
        self,
        url: str,
        parameter: str,
        result: ValidationResult
    ) -> ValidationResult:
        """Validate DOM-based XSS"""

        payload = '<img src=x onerror="console.log(\'DOM_XSS\')">'

        try:
            # Use Selenium to execute JavaScript
            driver = self._get_chrome_driver()

            if driver:
                # Navigate to URL with payload
                test_url = f"{url}?{parameter}={payload}"
                driver.get(test_url)

                # Wait for potential DOM manipulation
                wait = WebDriverWait(driver, 5)

                # Check if payload executed via console logs
                logs = driver.get_log('browser')
                for log in logs:
                    if "DOM_XSS" in log.get('message', ''):
                        result.is_valid = True
                        result.confidence_score = 0.9
                        result.payload_used = payload
                        result.status = ValidationStatus.CONFIRMED

                        result.reproduction_steps = [
                            "1. Load page with JavaScript payload in parameter",
                            "2. JavaScript processes parameter value without sanitization",
                            "3. Payload executes in DOM context",
                        ]

                        self.add_evidence(
                            "behavior",
                            "Payload executed in DOM context",
                            "DOM-based XSS confirmed"
                        )

                        result.remediation = (
                            "1. Use innerText instead of innerHTML\n"
                            "2. Sanitize DOM inputs with DOMPurify\n"
                            "3. Use frameworks with auto-escaping (React)\n"
                            "4. Content Security Policy"
                        )

                        self.log_validation(
                            url,
                            "DOM XSS",
                            "CONFIRMED",
                            result.confidence_score
                        )
                        return result

                driver.quit()

        except Exception as e:
            logger.debug(f"DOM XSS test failed: {str(e)}")

        result.status = ValidationStatus.NEEDS_REVIEW
        return result

    def _is_payload_reflected(self, response_text: str, payload: str) -> bool:
        """Check if payload is reflected in response without escaping"""
        # Check if payload appears unescaped
        if payload in response_text:
            # Verify it's not HTML-encoded
            if "&lt;" not in response_text or "&gt;" not in response_text:
                return True
        return False

    def _send_payload(
        self,
        url: str,
        parameter: str,
        payload: str,
        method: str = "GET"
    ) -> Optional[requests.Response]:
        """Send XSS payload to target"""

        try:
            headers = {"User-Agent": "ReconHive/1.0"}

            if method.upper() == "GET":
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params[parameter] = [payload]
                query = urlencode(params, doseq=True)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"
                return requests.get(test_url, headers=headers, timeout=10, verify=False)
            else:
                return requests.post(
                    url,
                    data={parameter: payload},
                    headers=headers,
                    timeout=10,
                    verify=False
                )

        except Exception as e:
            logger.debug(f"Payload send failed: {str(e)}")
            return None

    def _get_chrome_driver(self) -> Optional[webdriver.Chrome]:
        """Get Chrome driver for DOM testing"""
        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.warning(f"Chrome driver unavailable: {str(e)}")
            return None
