from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Integer, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class HTTPMethod(PyEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class URLStatus(PyEnum):
    ALIVE = "alive"
    DEAD = "dead"
    REDIRECT = "redirect"
    TIMEOUT = "timeout"
    ERROR = "error"
    PENDING = "pending"

class URLEndpoint(Base):
    __tablename__ = "url_endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="SET NULL"), index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    url = Column(String(1000), nullable=False, index=True)
    method = Column(Enum(HTTPMethod), default=HTTPMethod.GET)
    status = Column(Enum(URLStatus), default=URLStatus.PENDING, index=True)

    # HTTP Response metadata
    response_status_code = Column(Integer)
    response_content_type = Column(String(100))
    response_content_length = Column(Integer)
    response_headers = Column(JSONB)
    response_body_preview = Column(String(2000))

    # Page metadata
    page_title = Column(String(255))
    page_description = Column(String(500))
    technologies = Column(JSONB)

    # Discovery source
    discovered_from = Column(String(100))  # "crawl", "wayback", "gau", "katana", etc.
    discovered_date = Column(DateTime)
    first_seen_date = Column(DateTime, default=datetime.utcnow)
    last_probed_date = Column(DateTime)

    # Analysis
    has_form = Column(Boolean, default=False)
    has_redirect = Column(Boolean, default=False)
    redirect_to = Column(String(1000))
    has_login = Column(Boolean, default=False)
    is_authenticated = Column(Boolean, default=False)

    # Screenshot and evidence
    screenshot_path = Column(String(500))
    favicon_hash = Column(String(100))

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    subdomain = relationship("Subdomain", foreign_keys=[subdomain_id])
    scan = relationship("Scan", foreign_keys=[scan_id])

    __table_args__ = (
        Index("ix_url_endpoints_engagement_id", "engagement_id"),
        Index("ix_url_endpoints_asset_id", "asset_id"),
        Index("ix_url_endpoints_url", "url"),
        Index("ix_url_endpoints_status", "status"),
    )
