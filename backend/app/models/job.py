from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class JobStatus(PyEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)

    plugin_name = Column(String(255), nullable=False, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True)

    priority = Column(Integer, default=5, index=True)
    queue = Column(String(100), default="default")
    worker_id = Column(String(255), index=True)

    configuration = Column(JSON)
    target_filter = Column(JSON)

    progress_percent = Column(Integer, default=0)
    current_task = Column(String(255))

    retries = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text)

    queued_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    result_summary = Column(JSON)
    evidence_ids = Column(JSON)
    logs = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    scan = relationship("Scan", back_populates="jobs")

    __table_args__ = (
        Index("ix_jobs_scan_id", "scan_id"),
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_worker_id", "worker_id"),
        Index("ix_jobs_plugin_name", "plugin_name"),
        Index("ix_jobs_priority", "priority"),
    )
