"""
Reconnaissance tool implementations
"""

import time
import json
from typing import Dict, Any, Tuple
import logging

from app.tools.base import BaseTool, ToolResult, ToolConfig

logger = logging.getLogger(__name__)


class SubfinderTool(BaseTool):
    """Subdomain enumeration with subfinder"""

    @property
    def tool_name(self) -> str:
        return "subfinder"

    @property
    def tool_description(self) -> str:
        return "Subdomain enumeration tool - discovers subdomains using multiple sources"

    @property
    def tool_version(self) -> str:
        return "2.6.0"

    def check_availability(self) -> Tuple[bool, str]:
        """Check if subfinder is available"""
        if self._command_exists("subfinder"):
            return True, "subfinder found in PATH"
        return False, "subfinder not installed - install with: go install github.com/projectdiscovery/subfinder@latest"

    def execute(self, target: str, **kwargs) -> ToolResult:
        """
        Execute subfinder against target domain.

        Args:
            target: Domain to enumerate subdomains for
            **kwargs: Additional arguments

        Returns:
            ToolResult with discovered subdomains
        """
        start = time.time()

        try:
            # Build command
            command = f"subfinder -d {target} -json"

            # Execute
            exit_code, stdout, stderr = self._run_command(command)

            if exit_code != 0:
                return self.create_result(
                    success=False,
                    command=command,
                    exit_code=exit_code,
                    stderr=stderr,
                    errors=[f"subfinder failed with exit code {exit_code}"],
                    execution_time=time.time() - start,
                )

            # Parse JSON output
            subdomains = []
            try:
                for line in stdout.strip().split('\n'):
                    if line:
                        data = json.loads(line)
                        if 'host' in data:
                            subdomains.append(data['host'])
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse subfinder output: {str(e)}")

            return self.create_result(
                success=True,
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                parsed_data={
                    "subdomains": subdomains,
                    "target": target,
                },
                items_discovered=len(subdomains),
                execution_time=time.time() - start,
            )

        except Exception as e:
            return self.handle_error(e, {"target": target})


class DNSXTool(BaseTool):
    """DNS resolution and enumeration with dnsx"""

    @property
    def tool_name(self) -> str:
        return "dnsx"

    @property
    def tool_description(self) -> str:
        return "DNS resolution tool - resolves DNS records and detects wildcards"

    @property
    def tool_version(self) -> str:
        return "1.1.0"

    def check_availability(self) -> Tuple[bool, str]:
        """Check if dnsx is available"""
        if self._command_exists("dnsx"):
            return True, "dnsx found in PATH"
        return False, "dnsx not installed - install with: go install github.com/projectdiscovery/dnsx@latest"

    def execute(self, target: str, **kwargs) -> ToolResult:
        """
        Execute dnsx against target.

        Args:
            target: Domain or subdomain to resolve
            **kwargs: Additional arguments

        Returns:
            ToolResult with DNS records
        """
        start = time.time()

        try:
            # Build command
            command = f"dnsx -d {target} -json"

            # Execute
            exit_code, stdout, stderr = self._run_command(command)

            if exit_code != 0:
                return self.create_result(
                    success=False,
                    command=command,
                    exit_code=exit_code,
                    stderr=stderr,
                    errors=[f"dnsx failed with exit code {exit_code}"],
                    execution_time=time.time() - start,
                )

            # Parse JSON output
            records = []
            try:
                for line in stdout.strip().split('\n'):
                    if line:
                        data = json.loads(line)
                        records.append(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse dnsx output: {str(e)}")

            return self.create_result(
                success=True,
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                parsed_data={
                    "records": records,
                    "target": target,
                },
                items_discovered=len(records),
                execution_time=time.time() - start,
            )

        except Exception as e:
            return self.handle_error(e, {"target": target})


class HTTPXTool(BaseTool):
    """HTTP probing and status detection with httpx"""

    @property
    def tool_name(self) -> str:
        return "httpx"

    @property
    def tool_description(self) -> str:
        return "HTTP probe tool - detects live hosts and collects HTTP metadata"

    @property
    def tool_version(self) -> str:
        return "1.3.0"

    def check_availability(self) -> Tuple[bool, str]:
        """Check if httpx is available"""
        if self._command_exists("httpx"):
            return True, "httpx found in PATH"
        return False, "httpx not installed - install with: go install github.com/projectdiscovery/httpx@latest"

    def execute(self, target: str, **kwargs) -> ToolResult:
        """
        Execute httpx against target.

        Args:
            target: URL or domain to probe
            **kwargs: Additional arguments

        Returns:
            ToolResult with HTTP metadata
        """
        start = time.time()

        try:
            # Build command
            command = f"httpx -u {target} -json"

            # Execute
            exit_code, stdout, stderr = self._run_command(command)

            if exit_code != 0:
                return self.create_result(
                    success=False,
                    command=command,
                    exit_code=exit_code,
                    stderr=stderr,
                    errors=[f"httpx failed with exit code {exit_code}"],
                    execution_time=time.time() - start,
                )

            # Parse JSON output
            endpoints = []
            try:
                for line in stdout.strip().split('\n'):
                    if line:
                        data = json.loads(line)
                        endpoints.append(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse httpx output: {str(e)}")

            return self.create_result(
                success=True,
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                parsed_data={
                    "endpoints": endpoints,
                    "target": target,
                },
                items_discovered=len(endpoints),
                execution_time=time.time() - start,
            )

        except Exception as e:
            return self.handle_error(e, {"target": target})


class NaabuTool(BaseTool):
    """Port scanning with naabu"""

    @property
    def tool_name(self) -> str:
        return "naabu"

    @property
    def tool_description(self) -> str:
        return "Port scanner - fast, powerful port discovery"

    @property
    def tool_version(self) -> str:
        return "2.1.0"

    def check_availability(self) -> Tuple[bool, str]:
        """Check if naabu is available"""
        if self._command_exists("naabu"):
            return True, "naabu found in PATH"
        return False, "naabu not installed - install with: go install github.com/projectdiscovery/naabu@latest"

    def execute(self, target: str, **kwargs) -> ToolResult:
        """
        Execute naabu against target IP/domain.

        Args:
            target: IP address or domain to scan
            **kwargs: Additional arguments

        Returns:
            ToolResult with open ports
        """
        start = time.time()

        try:
            # Build command (scan common ports by default)
            command = f"naabu -host {target} -json"

            # Execute
            exit_code, stdout, stderr = self._run_command(command)

            if exit_code != 0:
                return self.create_result(
                    success=False,
                    command=command,
                    exit_code=exit_code,
                    stderr=stderr,
                    errors=[f"naabu failed with exit code {exit_code}"],
                    execution_time=time.time() - start,
                )

            # Parse JSON output
            ports = []
            try:
                for line in stdout.strip().split('\n'):
                    if line:
                        data = json.loads(line)
                        if 'port' in data:
                            ports.append(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse naabu output: {str(e)}")

            return self.create_result(
                success=True,
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                parsed_data={
                    "ports": ports,
                    "target": target,
                },
                items_discovered=len(ports),
                execution_time=time.time() - start,
            )

        except Exception as e:
            return self.handle_error(e, {"target": target})


class NucleiTool(BaseTool):
    """Vulnerability scanning with nuclei"""

    @property
    def tool_name(self) -> str:
        return "nuclei"

    @property
    def tool_description(self) -> str:
        return "Vulnerability scanner - templates-based vulnerability detection"

    @property
    def tool_version(self) -> str:
        return "3.0.0"

    def check_availability(self) -> Tuple[bool, str]:
        """Check if nuclei is available"""
        if self._command_exists("nuclei"):
            return True, "nuclei found in PATH"
        return False, "nuclei not installed - install with: go install github.com/projectdiscovery/nuclei@latest"

    def execute(self, target: str, **kwargs) -> ToolResult:
        """
        Execute nuclei against target.

        Args:
            target: URL to scan for vulnerabilities
            **kwargs: Additional arguments

        Returns:
            ToolResult with found vulnerabilities
        """
        start = time.time()

        try:
            # Build command
            command = f"nuclei -u {target} -json"

            # Execute
            exit_code, stdout, stderr = self._run_command(command)

            # nuclei returns 0 even if vulnerabilities are found
            if exit_code != 0 and "error" in stderr.lower():
                return self.create_result(
                    success=False,
                    command=command,
                    exit_code=exit_code,
                    stderr=stderr,
                    errors=[f"nuclei failed with exit code {exit_code}"],
                    execution_time=time.time() - start,
                )

            # Parse JSON output
            vulnerabilities = []
            try:
                for line in stdout.strip().split('\n'):
                    if line:
                        data = json.loads(line)
                        vulnerabilities.append(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse nuclei output: {str(e)}")

            return self.create_result(
                success=True,
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                parsed_data={
                    "vulnerabilities": vulnerabilities,
                    "target": target,
                },
                items_discovered=len(vulnerabilities),
                execution_time=time.time() - start,
            )

        except Exception as e:
            return self.handle_error(e, {"target": target})
