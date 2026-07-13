from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base

class Target(Base):
    __tablename__ = "targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), index=True)

    host = Column(String(255), nullable=False)
    port = Column(String(10))
    service = Column(String(100))
    protocol = Column(String(50))

    auth_type = Column(String(50))
    auth_credentials = Column(JSON)

    is_in_scope = Column(Boolean, default=True, index=True)
    priority = Column(String(20), default="medium")

    custom_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="targets")
    asset = relationship("Asset", back_populates="targets")
    scans = relationship("Scan", back_populates="target")

    __table_args__ = (
        Index("ix_targets_engagement_id", "engagement_id"),
        Index("ix_targets_asset_id", "asset_id"),
        Index("ix_targets_host", "host"),
        Index("ix_targets_is_in_scope", "is_in_scope"),
    )
