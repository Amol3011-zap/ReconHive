from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, List, Dict, Any, Optional
from uuid import UUID, uuid4
from app.utils.logger import logger


class EventType(str, Enum):
    # Engagement events
    ENGAGEMENT_CREATED = "engagement.created"
    ENGAGEMENT_UPDATED = "engagement.updated"
    ENGAGEMENT_COMPLETED = "engagement.completed"

    # Scan events
    SCAN_STARTED = "scan.started"
    SCAN_PROGRESS = "scan.progress"
    SCAN_COMPLETED = "scan.completed"
    SCAN_FAILED = "scan.failed"

    # Job events
    JOB_QUEUED = "job.queued"
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"

    # Finding events
    FINDING_CREATED = "finding.created"
    FINDING_UPDATED = "finding.updated"
    FINDING_REMEDIATED = "finding.remediated"

    # Evidence events
    EVIDENCE_COLLECTED = "evidence.collected"
    EVIDENCE_ANALYZED = "evidence.analyzed"

    # Report events
    REPORT_GENERATED = "report.generated"


@dataclass
class Event:
    """Event object."""
    event_type: EventType
    source: str
    timestamp: datetime
    data: Dict[str, Any]
    event_id: str = None
    related_entity_id: Optional[UUID] = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid4())


class EventBus:
    """Publish/subscribe event bus for ReconHive."""

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info("event_subscription_added", event_type=event_type.value, handler=handler.__name__)

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        self._event_history.append(event)
        logger.info("event_published", event_type=event.event_type.value, event_id=event.event_id)

        if event.event_type in self._subscribers:
            for handler in self._subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error("event_handler_failed", event_type=event.event_type.value,
                               handler=handler.__name__, error=str(e))

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get event history."""
        if event_type:
            return [e for e in self._event_history[-limit:] if e.event_type == event_type]
        return self._event_history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history = []


# Global event bus instance
event_bus = EventBus()
