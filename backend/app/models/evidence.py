from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class EvidenceType(PyEnum):
    SCREENSHOT = "screenshot"
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    CURL_COMMAND = "curl_command"
    NMAP_XML = "nmap_xml"
    SERVICE_BANNER = "service_banner"
    LOG_FILE = "log_file"
    CONSOLE_OUTPUT = "console_output"
    JSON_DATA = "json_data"
    XML_DATA = "xml_data"
    PDF_REPORT = "pdf_report"
    PCAP_FILE = "pcap_file"
    VIDEO = "video"
    CUSTOM_FILE = "custom_file"

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"))

    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(Enum(EvidenceType), nullable=False, index=True)

    data = Column(Text)
    file_path = Column(String(500))
    file_size = Column(String(50))
    mime_type = Column(String(100))
    checksum = Column(String(128))

    preview_data = Column(Text)
    tags = Column(JSON)
    metadata = Column(JSON)

    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="evidence")
    scan = relationship("Scan", back_populates="evidence")
    asset = relationship("Asset", back_populates="evidence")

    __table_args__ = (
        Index("ix_evidence_engagement_id", "engagement_id"),
        Index("ix_evidence_scan_id", "scan_id"),
        Index("ix_evidence_type", "type"),
    )
