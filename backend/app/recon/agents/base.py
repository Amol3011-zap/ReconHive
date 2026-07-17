"""
Base agent class for all reconnaissance agents
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import json
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agent execution"""
    max_retries: int = 3
    timeout: int = 3600
    priority: int = 5
    enable_caching: bool = True
    cache_ttl: int = 3600
    enable_logging: bool = True
    enable_deduplication: bool = True
    batch_size: int = 100


@dataclass
class AgentResult:
    """Result from agent execution"""
    success: bool
    agent_name: str
    execution_time: float = 0.0
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    items_discovered: int = 0
    items_deduplicated: int = 0
    evidence_collected: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "agent_name": self.agent_name,
            "execution_time": self.execution_time,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
            "items_discovered": self.items_discovered,
            "items_deduplicated": self.items_deduplicated,
            "evidence_collected": self.evidence_collected,
            "next_steps": self.next_steps,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)


class BaseReconAgent(ABC):
    """
    Base class for all reconnaissance agents.

    Every agent must:
    1. Inherit from BaseReconAgent
    2. Implement execute() method
    3. Return AgentResult
    4. Handle errors gracefully
    5. Track evidence and deduplication
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.discovered_items: Set[str] = set()
        self.deduplicated_items: Set[str] = set()
        self.evidence_files: List[Dict[str, Any]] = []

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Agent identifier"""
        pass

    @property
    @abstractmethod
    def agent_description(self) -> str:
        """Agent capabilities description"""
        pass

    @abstractmethod
    def execute(
        self,
        target: str,
        engagement_id: UUID,
        scan_id: UUID,
        **kwargs
    ) -> AgentResult:
        """
        Execute the reconnaissance agent.

        Args:
            target: The target to scan (domain, IP, URL, etc.)
            engagement_id: Associated engagement UUID
            scan_id: Associated scan UUID
            **kwargs: Agent-specific parameters

        Returns:
            AgentResult with success status and discovered data
        """
        pass

    def check_duplicate(self, item_hash: str, db_session=None) -> bool:
        """
        Check if item was already discovered.

        Args:
            item_hash: Hash of the item to check
            db_session: Database session for persistence check

        Returns:
            True if duplicate, False otherwise
        """
        if item_hash in self.discovered_items:
            self.deduplicated_items.add(item_hash)
            return True

        if db_session and hasattr(self, 'duplicate_check_query'):
            try:
                result = self.duplicate_check_query(db_session, item_hash)
                if result:
                    self.deduplicated_items.add(item_hash)
                    return True
            except Exception as e:
                self.logger.warning(f"Duplicate check failed: {str(e)}")

        return False

    def add_discovered_item(self, item_hash: str):
        """Track a newly discovered item"""
        self.discovered_items.add(item_hash)

    def add_evidence(
        self,
        evidence_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add evidence collected during reconnaissance.

        Args:
            evidence_type: Type of evidence (screenshot, response, etc.)
            content: Evidence content or file path
            metadata: Additional metadata about the evidence
        """
        evidence = {
            "type": evidence_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.evidence_files.append(evidence)

    def log_execution(
        self,
        status: str,
        details: Dict[str, Any],
        level: str = "info"
    ):
        """Log agent execution with context"""
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(
            f"Agent execution: {self.agent_name}",
            extra={
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "agent": self.agent_name,
                **details
            }
        )

    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any]
    ) -> AgentResult:
        """
        Handle errors gracefully.

        Args:
            error: The exception that occurred
            context: Context information

        Returns:
            AgentResult with error information
        """
        error_msg = f"{self.agent_name} error: {str(error)}"
        self.logger.error(
            error_msg,
            exc_info=True,
            extra={**context, "agent": self.agent_name}
        )

        return AgentResult(
            success=False,
            agent_name=self.agent_name,
            message=error_msg,
            errors=[str(error)],
        )

    def validate_target(self, target: str) -> bool:
        """Validate target format. Override in subclasses."""
        return bool(target and len(target) > 0)

    def create_result(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        execution_time: float = 0.0,
        next_steps: Optional[List[str]] = None
    ) -> AgentResult:
        """Create a standardized result"""
        return AgentResult(
            success=success,
            agent_name=self.agent_name,
            message=message,
            data=data or {},
            errors=errors or [],
            items_discovered=len(self.discovered_items),
            items_deduplicated=len(self.deduplicated_items),
            evidence_collected=self.evidence_files,
            execution_time=execution_time,
            next_steps=next_steps or [],
        )
