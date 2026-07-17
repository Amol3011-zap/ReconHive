from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class ToolRunStatus(PyEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ToolRun(Base):
    __tablename__ = "tool_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Tool info
    tool_name = Column(String(100), nullable=False, index=True)
    tool_version = Column(String(100))
    tool_category = Column(String(100))  # "passive_recon", "web_discovery", "dns", etc.

    # Execution context
    target = Column(String(500), nullable=False)
    arguments = Column(JSONB)  # Command line arguments
    environment_vars = Column(JSONB)  # Environment variables passed

    # Execution tracking
    status = Column(String(50), default="queued", nullable=False, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Exit information
    exit_code = Column(Integer)
    error_message = Column(Text)

    # Output
    stdout = Column(Text)  # First 10KB
    stderr = Column(Text)  # First 10KB
    stdout_full_path = Column(String(500))  # Path to full stdout if too large
    stderr_full_path = Column(String(500))  # Path to full stderr if too large

    # Results
    results_count = Column(Integer, default=0)
    results_summary = Column(JSONB)
    results_stored = Column(String(10), default="unknown")  # "yes", "no", "partial"

    # Worker assignment
    worker_id = Column(String(100), index=True)
    hostname = Column(String(255))

    # Retry information
    attempt_number = Column(Integer, default=1)
    max_retries = Column(Integer, default=3)
    is_retry = Column(String(10), default="no")

    # Metadata
    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    scan = relationship("Scan", foreign_keys=[scan_id])
    job = relationship("Job", foreign_keys=[job_id])

    __table_args__ = (
        Index("ix_tool_runs_engagement_id", "engagement_id"),
        Index("ix_tool_runs_scan_id", "scan_id"),
        Index("ix_tool_runs_job_id", "job_id"),
        Index("ix_tool_runs_tool_name", "tool_name"),
        Index("ix_tool_runs_status", "status"),
        Index("ix_tool_runs_worker_id", "worker_id"),
    )
