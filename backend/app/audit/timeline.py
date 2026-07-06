from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4
from app.utils.logger import logger


class ActivityType(str, Enum):
    """Types of activities in the system."""
    ENGAGEMENT_CREATED = "engagement.created"
    ENGAGEMENT_UPDATED = "engagement.updated"
    ENGAGEMENT_COMPLETED = "engagement.completed"
    SCAN_STARTED = "scan.started"
    SCAN_PAUSED = "scan.paused"
    SCAN_RESUMED = "scan.resumed"
    SCAN_STOPPED = "scan.stopped"
    SCAN_COMPLETED = "scan.completed"
    JOB_QUEUED = "job.queued"
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    FINDING_CREATED = "finding.created"
    FINDING_UPDATED = "finding.updated"
    FINDING_REMEDIATED = "finding.remediated"
    EVIDENCE_COLLECTED = "evidence.collected"
    REPORT_GENERATED = "report.generated"
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_EXECUTED = "plugin.executed"
    PLUGIN_FAILED = "plugin.failed"


@dataclass
class ActivityEntry:
    """Single activity entry in the timeline."""
    activity_id: str = field(default_factory=lambda: str(uuid4()))
    activity_type: ActivityType = ActivityType.ENGAGEMENT_CREATED
    entity_id: str = ""
    entity_type: str = ""
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "activity_id": self.activity_id,
            "activity_type": self.activity_type.value,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metadata": self.metadata,
            "status": self.status,
            "error_message": self.error_message,
        }


class ActivityTimeline:
    """Track all activities for audit trail."""

    def __init__(self, max_entries: int = 10000):
        self.entries: List[ActivityEntry] = []
        self.max_entries = max_entries
        self.engagement_activities: Dict[str, List[ActivityEntry]] = {}

    def record(self, activity_type: ActivityType, entity_id: str, entity_type: str,
              user_id: Optional[str] = None, description: str = "",
              metadata: Optional[Dict] = None, status: str = "success",
              error_message: Optional[str] = None) -> str:
        """Record an activity."""
        entry = ActivityEntry(
            activity_type=activity_type,
            entity_id=entity_id,
            entity_type=entity_type,
            user_id=user_id,
            description=description,
            metadata=metadata or {},
            status=status,
            error_message=error_message,
        )

        self.entries.append(entry)

        # Track per-engagement for quick retrieval
        if entity_type == "engagement":
            if entity_id not in self.engagement_activities:
                self.engagement_activities[entity_id] = []
            self.engagement_activities[entity_id].append(entry)

        # Keep only max entries
        if len(self.entries) > self.max_entries:
            removed = self.entries.pop(0)
            logger.info("activity_pruned", activity_id=removed.activity_id)

        logger.info("activity_recorded", activity_id=entry.activity_id,
                   activity_type=activity_type.value, entity_id=entity_id)

        return entry.activity_id

    def get_entity_timeline(self, entity_id: str, limit: int = 100) -> List[Dict]:
        """Get timeline for specific entity."""
        matching = [e for e in self.entries if e.entity_id == entity_id][-limit:]
        return [e.to_dict() for e in matching]

    def get_engagement_timeline(self, engagement_id: str, limit: int = 100) -> List[Dict]:
        """Get timeline for specific engagement."""
        activities = self.engagement_activities.get(engagement_id, [])[-limit:]
        return [e.to_dict() for e in activities]

    def get_user_activities(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get activities for specific user."""
        matching = [e for e in self.entries if e.user_id == user_id][-limit:]
        return [e.to_dict() for e in matching]

    def get_timeline(self, activity_type: Optional[ActivityType] = None,
                    limit: int = 100) -> List[Dict]:
        """Get timeline entries."""
        entries = self.entries
        if activity_type:
            entries = [e for e in entries if e.activity_type == activity_type]
        return [e.to_dict() for e in entries[-limit:]]

    def get_recent_activities(self, hours: int = 24, limit: int = 50) -> List[Dict]:
        """Get activities from last N hours."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        matching = [e for e in self.entries if e.timestamp > cutoff][-limit:]
        return [e.to_dict() for e in matching]

    def get_failed_activities(self, limit: int = 50) -> List[Dict]:
        """Get all failed activities."""
        matching = [e for e in self.entries if e.status == "failed"][-limit:]
        return [e.to_dict() for e in matching]

    def stats(self) -> Dict:
        """Get timeline statistics."""
        return {
            "total_entries": len(self.entries),
            "max_entries": self.max_entries,
            "engaged_entities": len(self.engagement_activities),
            "recent_24h": len([e for e in self.entries
                             if (datetime.utcnow() - e.timestamp).days < 1]),
        }


# Global activity timeline instance
activity_timeline = ActivityTimeline()
