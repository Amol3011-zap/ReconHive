"""
Base tool class for all reconnaissance tools
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from enum import Enum
import logging
import json
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """Tool execution status"""
    AVAILABLE = "available"
    INSTALLED = "installed"
    MISSING = "missing"
    ERROR = "error"


@dataclass
class ToolConfig:
    """Configuration for tool execution"""
    timeout: int = 300  # 5 minutes
    max_retries: int = 1
    capture_output: bool = True
    parse_output: bool = True
    store_evidence: bool = True


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    tool_name: str
    command: str = ""
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    items_discovered: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "tool_name": self.tool_name,
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout[:1000] if self.stdout else "",  # Truncate
            "stderr": self.stderr[:1000] if self.stderr else "",
            "parsed_data": self.parsed_data,
            "errors": self.errors,
            "execution_time": self.execution_time,
            "items_discovered": self.items_discovered,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)


class BaseTool(ABC):
    """
    Base class for all reconnaissance tools.

    Every tool must:
    1. Inherit from BaseTool
    2. Implement execute() method
    3. Implement check_availability() method
    4. Return ToolResult
    5. Handle timeouts and errors
    """

    def __init__(self, config: Optional[ToolConfig] = None):
        self.config = config or ToolConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Tool identifier"""
        pass

    @property
    @abstractmethod
    def tool_description(self) -> str:
        """Tool description and capabilities"""
        pass

    @property
    @abstractmethod
    def tool_version(self) -> str:
        """Tool version"""
        pass

    @abstractmethod
    def check_availability(self) -> Tuple[bool, str]:
        """
        Check if tool is available on system.

        Returns:
            Tuple of (available, message)
        """
        pass

    @abstractmethod
    def execute(
        self,
        target: str,
        **kwargs
    ) -> ToolResult:
        """
        Execute the tool against target.

        Args:
            target: The target to scan
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with execution details
        """
        pass

    def _run_command(
        self,
        command: str,
        shell: bool = False,
        input_data: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """
        Run a shell command safely.

        Args:
            command: Command to run
            shell: Whether to use shell
            input_data: Input to send to stdin

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                timeout=self.config.timeout,
            )

            stdout, stderr = process.communicate(input=input_data)
            return process.returncode, stdout, stderr

        except subprocess.TimeoutExpired:
            process.kill()
            return 1, "", f"Command timeout after {self.config.timeout}s"
        except Exception as e:
            return 1, "", str(e)

    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        return shutil.which(command) is not None

    def create_result(
        self,
        success: bool,
        command: str = "",
        exit_code: int = 0,
        stdout: str = "",
        stderr: str = "",
        parsed_data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        execution_time: float = 0.0,
        items_discovered: int = 0
    ) -> ToolResult:
        """Create a standardized result"""
        return ToolResult(
            success=success,
            tool_name=self.tool_name,
            command=command,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            parsed_data=parsed_data or {},
            errors=errors or [],
            execution_time=execution_time,
            items_discovered=items_discovered,
        )

    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> ToolResult:
        """Handle errors gracefully"""
        error_msg = f"{self.tool_name} error: {str(error)}"
        self.logger.error(error_msg, exc_info=True, extra=context)

        return self.create_result(
            success=False,
            errors=[str(error)]
        )
