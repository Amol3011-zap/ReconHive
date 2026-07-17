from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class APIType(PyEnum):
    REST = "rest"
    GRAPHQL = "graphql"
    SOAP = "soap"
    GRPC = "grpc"
    WEBHOOK = "webhook"

class APIAuth(PyEnum):
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH = "oauth"
    UNKNOWN = "unknown"

class APIEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="SET NULL"), index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    # API Info
    endpoint_path = Column(String(1000), nullable=False, index=True)
    api_type = Column(String(50), nullable=False)
    version = Column(String(100))
    title = Column(String(255))
    description = Column(String(1000))

    # Documentation
    documentation_url = Column(String(500))
    spec_format = Column(String(50))  # "swagger", "openapi", "graphql", etc.
    spec_version = Column(String(100))

    # Methods and parameters
    methods = Column(JSONB)  # ["GET", "POST", "PUT", etc.]
    parameters = Column(JSONB)  # List of parameters
    request_schema = Column(JSONB)
    response_schema = Column(JSONB)

    # Authentication
    auth_type = Column(String(50), default="unknown")
    auth_required = Column(Boolean, default=False)
    auth_details = Column(JSONB)

    # Discovery
    discovered_from = Column(String(100))  # "swagger", "graphql-voyager", "kiterunner", etc.
    discovered_date = Column(DateTime, default=datetime.utcnow)
    verified_date = Column(DateTime)

    # Analysis
    is_public = Column(Boolean, default=False)
    is_documented = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    has_known_vulnerabilities = Column(Boolean, default=False)

    # Endpoints from this API
    operation_count = Column(Integer, default=0)
    parameter_count = Column(Integer, default=0)

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    subdomain = relationship("Subdomain", foreign_keys=[subdomain_id])
    scan = relationship("Scan", foreign_keys=[scan_id])

    __table_args__ = (
        Index("ix_api_endpoints_engagement_id", "engagement_id"),
        Index("ix_api_endpoints_asset_id", "asset_id"),
        Index("ix_api_endpoints_endpoint_path", "endpoint_path"),
        Index("ix_api_endpoints_api_type", "api_type"),
    )
