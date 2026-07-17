from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Boolean, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class SubdomainStatus(PyEnum):
    DISCOVERED = "discovered"
    ALIVE = "alive"
    DEAD = "dead"
    PENDING_VERIFICATION = "pending_verification"

class Subdomain(Base):
    __tablename__ = "subdomains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), index=True)
    is_wildcard = Column(Boolean, default=False, index=True)
    status = Column(Enum(SubdomainStatus), default=SubdomainStatus.DISCOVERED, index=True)

    # DNS Records
    a_records = Column(JSONB)
    aaaa_records = Column(JSONB)
    cname = Column(String(255))
    mx_records = Column(JSONB)
    txt_records = Column(JSONB)
    ns_records = Column(JSONB)

    # Discovery metadata
    sources = Column(JSONB)  # List of sources (crt.sh, subfinder, etc.)
    first_discovered_date = Column(DateTime, nullable=False)
    last_verified_date = Column(DateTime)
    last_active_date = Column(DateTime)

    # Risk and confidence
    is_takeover_candidate = Column(Boolean, default=False, index=True)
    confidence_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)

    # Relationships
    technologies = Column(JSONB)  # Detected technologies on this subdomain
    endpoints = Column(JSONB)  # HTTP endpoints found on this subdomain
    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    scan = relationship("Scan", foreign_keys=[scan_id])
    dns_records = relationship("DNSRecord", back_populates="subdomain", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_subdomains_engagement_id", "engagement_id"),
        Index("ix_subdomains_asset_id", "asset_id"),
        Index("ix_subdomains_name", "name"),
        Index("ix_subdomains_status", "status"),
        Index("ix_subdomains_is_takeover_candidate", "is_takeover_candidate"),
    )
