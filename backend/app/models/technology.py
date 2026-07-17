from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class TechCategory(PyEnum):
    FRONTEND_FRAMEWORK = "frontend_framework"
    BACKEND_FRAMEWORK = "backend_framework"
    WEB_SERVER = "web_server"
    DATABASE = "database"
    CACHE = "cache"
    LANGUAGE = "language"
    CMS = "cms"
    ECOMMERCE = "ecommerce"
    CDN = "cdn"
    WAF = "waf"
    ANALYTICS = "analytics"
    JAVASCRIPT_LIBRARY = "javascript_library"
    MONITORING = "monitoring"
    CONTAINER = "container"
    ORCHESTRATION = "orchestration"
    OTHER = "other"

class Technology(Base):
    __tablename__ = "technologies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="SET NULL"), index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    name = Column(String(255), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    version = Column(String(100))
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0

    # Detection metadata
    detected_method = Column(String(100))  # "header", "body", "behavior", "fingerprint"
    detected_from_url = Column(String(1000))
    detected_at = Column(DateTime, default=datetime.utcnow)

    # Risk assessment
    is_known_vulnerable = Column(String(10), default="unknown")  # "yes", "no", "unknown"
    vulnerability_count = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)

    # Additional metadata
    website = Column(String(500))
    documentation = Column(String(500))
    github = Column(String(500))
    cpes = Column(JSONB)  # Common Platform Enumeration identifiers
    cves = Column(JSONB)  # Known CVEs for this version

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    subdomain = relationship("Subdomain", foreign_keys=[subdomain_id])
    scan = relationship("Scan", foreign_keys=[scan_id])

    __table_args__ = (
        Index("ix_technologies_engagement_id", "engagement_id"),
        Index("ix_technologies_asset_id", "asset_id"),
        Index("ix_technologies_name", "name"),
        Index("ix_technologies_category", "category"),
    )
