from sqlalchemy import Column, String, Text, Enum, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class AssetType(PyEnum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    URL = "url"
    HOST = "host"
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    CIDR = "cidr"
    HOSTNAME = "hostname"
    API = "api"
    CLOUD_ACCOUNT = "cloud_account"
    MOBILE_APP = "mobile_app"
    NETWORK = "network"
    DATABASE = "database"

class Environment(PyEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    QA = "qa"
    TESTING = "testing"

class Criticality(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class AssetStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"
    PENDING = "pending"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    description = Column(Text)

    type = Column(Enum(AssetType), nullable=False, index=True)
    environment = Column(Enum(Environment), index=True)
    criticality = Column(Enum(Criticality), index=True)
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE, index=True)

    owner = Column(String(255))
    tags = Column(JSON)
    technology_stack = Column(JSON)
    operating_system = Column(String(100))

    risk_score = Column(Float, default=0.0, index=True)
    scan_history = Column(JSON)
    metadata = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="assets")
    targets = relationship("Target", back_populates="asset", cascade="all, delete-orphan")
    scans = relationship("Scan", back_populates="asset")
    evidence = relationship("Evidence", back_populates="asset")
    findings = relationship("Finding", back_populates="asset")

    __table_args__ = (
        Index("ix_assets_engagement_id", "engagement_id"),
        Index("ix_assets_type", "type"),
        Index("ix_assets_status", "status"),
        Index("ix_assets_environment", "environment"),
        Index("ix_assets_criticality", "criticality"),
        Index("ix_assets_risk_score", "risk_score"),
    )
