from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class WorkerStatus(PyEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    PAUSED = "paused"

class WorkerType(PyEnum):
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    EVIDENCE = "evidence"
    REPORTING = "reporting"

class Worker(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(Enum(WorkerType), nullable=False, index=True)
    status = Column(Enum(WorkerStatus), default=WorkerStatus.ONLINE, nullable=False, index=True)

    hostname = Column(String(255))
    ip_address = Column(String(45))
    port = Column(Integer, default=5000)

    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    disk_usage = Column(Float, default=0.0)

    current_job_id = Column(UUID(as_uuid=True), index=True)
    active_jobs = Column(Integer, default=0)
    queue_depth = Column(Integer, default=0)

    completed_jobs = Column(Integer, default=0)
    failed_jobs = Column(Integer, default=0)
    total_runtime_seconds = Column(Integer, default=0)

    supported_plugins = Column(JSONB, default={})
    capabilities = Column(JSONB, default={})
    custom_metadata = Column(JSONB)

    is_enabled = Column(Boolean, default=True, index=True)
    last_heartbeat = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_workers_name", "name"),
        Index("ix_workers_status", "status"),
        Index("ix_workers_type", "type"),
        Index("ix_workers_is_enabled", "is_enabled"),
        Index("ix_workers_last_heartbeat", "last_heartbeat"),
    )
