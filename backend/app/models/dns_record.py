from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class DNSRecordType(PyEnum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    PTR = "PTR"
    SOA = "SOA"
    SRV = "SRV"
    CAA = "CAA"

class DNSRecord(Base):
    __tablename__ = "dns_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    subdomain_id = Column(UUID(as_uuid=True), ForeignKey("subdomains.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    hostname = Column(String(255), nullable=False, index=True)
    record_type = Column(Enum(DNSRecordType), nullable=False, index=True)
    value = Column(String(500), nullable=False)
    ttl = Column(Integer)

    # Resolution metadata
    resolver_used = Column(String(100))
    resolved_at = Column(DateTime)
    is_active = Column(String(10), default="unknown")  # "yes", "no", "unknown"

    # Evidence
    raw_response = Column(JSONB)
    extra_data = Column(JSONB)

    discovered_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    subdomain = relationship("Subdomain", back_populates="dns_records", foreign_keys=[subdomain_id])
    scan = relationship("Scan", foreign_keys=[scan_id])

    __table_args__ = (
        Index("ix_dns_records_engagement_id", "engagement_id"),
        Index("ix_dns_records_subdomain_id", "subdomain_id"),
        Index("ix_dns_records_hostname", "hostname"),
        Index("ix_dns_records_type", "record_type"),
    )
