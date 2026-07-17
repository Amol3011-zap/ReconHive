from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class ParamType(PyEnum):
    QUERY = "query"
    BODY = "body"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"
    MATRIX = "matrix"
    UNKNOWN = "unknown"

class Parameter(Base):
    __tablename__ = "parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="SET NULL"), index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)
    api_endpoint_id = Column(UUID(as_uuid=True), ForeignKey("api_endpoints.id", ondelete="SET NULL"), index=True)

    # Parameter info
    endpoint_url = Column(String(1000), nullable=False, index=True)
    method = Column(String(20))  # GET, POST, PUT, etc.
    parameter_name = Column(String(255), nullable=False, index=True)
    param_type = Column(String(50), nullable=False)  # query, body, header, path, etc.

    # Parameter details
    parameter_value_type = Column(String(100))  # string, integer, boolean, array, object
    parameter_required = Column(Boolean, default=False)
    parameter_default_value = Column(String(500))
    parameter_example_value = Column(String(500))
    parameter_description = Column(String(1000))

    # Allowed values
    allowed_values = Column(JSONB)  # Enum values if restricted
    regex_pattern = Column(String(500))
    min_length = Column(Integer)
    max_length = Column(Integer)

    # Discovery
    discovered_by = Column(String(100))  # "arjun", "paramspider", "x8", "api-spec", etc.
    discovered_date = Column(DateTime, default=datetime.utcnow)
    verified_date = Column(DateTime)

    # Analysis
    is_reflected = Column(Boolean, default=False)
    is_stored = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)  # password, token, apikey, etc.
    is_injectable = Column(String(10), default="unknown")  # sql, xpath, ldap, command, etc.

    # Findings related to this parameter
    related_finding_ids = Column(JSONB)  # List of finding IDs

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    subdomain = relationship("Subdomain", foreign_keys=[subdomain_id])
    scan = relationship("Scan", foreign_keys=[scan_id])
    api_endpoint = relationship("APIEndpoint", foreign_keys=[api_endpoint_id])

    __table_args__ = (
        Index("ix_parameters_engagement_id", "engagement_id"),
        Index("ix_parameters_asset_id", "asset_id"),
        Index("ix_parameters_endpoint_url", "endpoint_url"),
        Index("ix_parameters_name", "parameter_name"),
    )
