from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class JSAssetType(PyEnum):
    ENDPOINT = "endpoint"
    SECRET = "secret"
    API_KEY = "api_key"
    INTERNAL_HOSTNAME = "internal_hostname"
    AWS_BUCKET = "aws_bucket"
    GRAPHQL_ENDPOINT = "graphql_endpoint"
    WEBSOCKET = "websocket"

class JavaScriptAsset(Base):
    __tablename__ = "javascript_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="SET NULL"), index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    js_file_url = Column(String(1000), nullable=False, index=True)
    js_file_hash = Column(String(64))

    # Extracted data
    asset_type = Column(String(50), nullable=False)
    asset_value = Column(String(1000), nullable=False)

    # Context
    context_line = Column(String(500))
    context_surrounding = Column(String(2000))

    # Analysis
    is_valid = Column(String(10), default="unknown")  # "yes", "no", "unknown"
    is_sensitive = Column(String(10), default="unknown")
    risk_level = Column(String(20), default="low")  # low, medium, high, critical

    # Discovery
    extracted_by = Column(String(100))  # "linkfinder", "secretfinder", "jsfinder", etc.
    extracted_date = Column(DateTime, default=datetime.utcnow)
    verified_date = Column(DateTime)

    # Related findings
    finding_id = Column(UUID(as_uuid=True), ForeignKey("findings.id", ondelete="SET NULL"), index=True)

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    subdomain = relationship("Subdomain", foreign_keys=[subdomain_id])
    scan = relationship("Scan", foreign_keys=[scan_id])
    finding = relationship("Finding", foreign_keys=[finding_id])

    __table_args__ = (
        Index("ix_javascript_assets_engagement_id", "engagement_id"),
        Index("ix_javascript_assets_asset_id", "asset_id"),
        Index("ix_javascript_assets_js_file_url", "js_file_url"),
        Index("ix_javascript_assets_asset_type", "asset_type"),
    )
