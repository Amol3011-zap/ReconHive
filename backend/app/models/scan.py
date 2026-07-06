from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, Index, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class ScanStatus(PyEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Scan(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("targets.id", ondelete="CASCADE"), index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(500))
    plugin_names = Column(JSON)
    configuration = Column(JSON)

    status = Column(Enum(ScanStatus), default=ScanStatus.QUEUED, nullable=False, index=True)
    progress_percent = Column(Integer, default=0)
    current_stage = Column(String(100))

    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    worker_id = Column(String(255), index=True)
    result_summary = Column(JSON)
    error_message = Column(String(1000))

    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="scans")
    asset = relationship("Asset", back_populates="scans")
    target = relationship("Target", back_populates="scans")
    jobs = relationship("Job", back_populates="scan", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="scan", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_scans_engagement_id", "engagement_id"),
        Index("ix_scans_asset_id", "asset_id"),
        Index("ix_scans_status", "status"),
        Index("ix_scans_worker_id", "worker_id"),
    )
