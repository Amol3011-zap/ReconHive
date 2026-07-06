from sqlalchemy import Column, String, Text, DateTime, Enum, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class EngagementStatus(PyEnum):
    PLANNING = "planning"
    SCOPING = "scoping"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class EngagementType(PyEnum):
    PENETRATION_TEST = "penetration_test"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    SECURITY_AUDIT = "security_audit"
    COMPLIANCE_ASSESSMENT = "compliance_assessment"
    BREACH_SIMULATION = "breach_simulation"
    CONTINUOUS_VALIDATION = "continuous_validation"

class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    type = Column(Enum(EngagementType), nullable=False, index=True)
    status = Column(Enum(EngagementStatus), nullable=False, index=True)
    client = Column(String(255), nullable=False)
    scope = Column(Text)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    due_date = Column(DateTime)

    owner = Column(String(255), nullable=False)
    team_members = Column(String(1000))

    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    assets = relationship("Asset", back_populates="engagement", cascade="all, delete-orphan")
    targets = relationship("Target", back_populates="engagement", cascade="all, delete-orphan")
    scans = relationship("Scan", back_populates="engagement", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="engagement", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="engagement", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_engagements_status", "status"),
        Index("ix_engagements_type", "type"),
        Index("ix_engagements_client", "client"),
        Index("ix_engagements_is_active", "is_active"),
    )
