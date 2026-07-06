from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum, Index, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class Severity(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FindingStatus(PyEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    FIXED = "fixed"
    ACCEPTED_RISK = "accepted_risk"
    FALSE_POSITIVE = "false_positive"
    DUPLICATE = "duplicate"

class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(Enum(Severity), nullable=False, index=True)
    status = Column(Enum(FindingStatus), default=FindingStatus.OPEN, nullable=False, index=True)

    cvss_score = Column(Float)
    cvss_vector = Column(String(100))
    cwe_id = Column(String(20))
    cwe_name = Column(String(255))
    owasp_id = Column(String(20))

    affected_assets = Column(JSON)
    affected_targets = Column(JSON)
    evidence_ids = Column(JSON)

    remediation = Column(Text)
    remediation_complexity = Column(String(50))
    estimated_effort = Column(String(100))

    references = Column(JSON)
    labels = Column(JSON)
    metadata = Column(JSON)

    detected_by = Column(String(255))
    verified_by = Column(String(255))
    verified_at = Column(DateTime)

    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="findings")
    asset = relationship("Asset", back_populates="findings")
    scan = relationship("Scan", foreign_keys=[scan_id])

    __table_args__ = (
        Index("ix_findings_engagement_id", "engagement_id"),
        Index("ix_findings_asset_id", "asset_id"),
        Index("ix_findings_severity", "severity"),
        Index("ix_findings_status", "status"),
    )
