"""
Base worker class for all reconnaissance tasks
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class WorkerConfig:
    """Configuration for worker execution"""
    max_retries: int = 3
    retry_backoff: int = 60  # seconds
    timeout: int = 3600  # 1 hour
    rate_limit: Optional[str] = None  # "10/m" for 10 per minute
    priority: int = 5  # 1-10, higher = more important
    soft_time_limit: int = 3300  # 55 minutes before hard limit
    log_results: bool = True
    store_results: bool = True


class WorkerResult:
    """Standardized result format for all workers"""

    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        execution_time: Optional[float] = None,
        items_processed: int = 0,
        items_failed: int = 0
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.errors = errors or []
        self.execution_time = execution_time
        self.items_processed = items_processed
        self.items_failed = items_failed
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "execution_time": self.execution_time,
            "items_processed": self.items_processed,
            "items_failed": self.items_failed,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        """Convert result to JSON"""
        return json.dumps(self.to_dict(), default=str)


class BaseWorker(ABC):
    """
    Base class for all reconnaissance workers.

    All workers must:
    1. Inherit from BaseWorker
    2. Implement execute() method
    3. Return WorkerResult
    4. Handle errors gracefully
    5. Log all operations
    """

    def __init__(self, config: Optional[WorkerConfig] = None):
        self.config = config or WorkerConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, **kwargs) -> WorkerResult:
        """
        Execute the worker task.

        Must be implemented by subclasses.

        Args:
            **kwargs: Worker-specific arguments

        Returns:
            WorkerResult with success status and data
        """
        pass

    def validate_inputs(self, required_fields: List[str], **kwargs) -> bool:
        """Validate required input fields"""
        missing = [f for f in required_fields if f not in kwargs]
        if missing:
            self.logger.error(f"Missing required fields: {missing}")
            return False
        return True

    def log_execution(self, task_name: str, status: str, details: Dict[str, Any]):
        """Log worker execution with structured data"""
        self.logger.info(
            f"Worker execution: {task_name}",
            extra={
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                **details
            }
        )

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> WorkerResult:
        """
        Handle errors gracefully.

        Args:
            error: The exception that occurred
            context: Context information about the error

        Returns:
            WorkerResult with error information
        """
        error_msg = f"{self.__class__.__name__} error: {str(error)}"
        self.logger.error(error_msg, exc_info=True, extra=context)

        return WorkerResult(
            success=False,
            message=error_msg,
            errors=[str(error)],
        )


class ReconWorker(BaseWorker):
    """
    Base class specifically for reconnaissance workers.

    Adds reconnaissance-specific functionality:
    - Evidence collection
    - Deduplication
    - Source attribution
    """

    def __init__(self, config: Optional[WorkerConfig] = None):
        super().__init__(config)
        self.evidence_files = []
        self.discovered_items = 0
        self.duplicate_items = 0

    def add_evidence(self, file_path: str, evidence_type: str):
        """Track evidence files produced"""
        self.evidence_files.append({
            "path": file_path,
            "type": evidence_type,
            "timestamp": datetime.utcnow().isoformat()
        })

    def check_duplicate(self, item_hash: str, db_session=None) -> bool:
        """Check if item already exists"""
        if db_session and hasattr(self, 'duplicate_check_query'):
            result = self.duplicate_check_query(db_session, item_hash)
            if result:
                self.duplicate_items += 1
                return True
        return False

    def attribution_string(self, sources: List[str]) -> str:
        """Create attribution string from sources"""
        return " + ".join(sorted(set(sources)))


class PingWorker(BaseWorker):
    """Simple ping worker for testing"""

    def execute(self, message: str = "ping", **kwargs) -> WorkerResult:
        """Simple echo test"""
        return WorkerResult(
            success=True,
            message=f"Pong: {message}",
            data={"echo": message},
        )
