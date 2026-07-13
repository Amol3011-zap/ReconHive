from sqlalchemy import Column, String, DateTime, JSON, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base
from datetime import datetime

class PluginRegistration(Base):
    __tablename__ = "plugin_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    version = Column(String(50), nullable=False)
    type = Column(String(100), nullable=False, index=True)
    description = Column(String(500))

    plugin_class_path = Column(String(255), nullable=False)
    config_schema = Column(JSON)

    custom_metadata = Column(JSON)
    capabilities = Column(JSON)

    enabled = Column(Boolean, default=True, index=True)
    health_status = Column(String(50), default="unknown")
    last_health_check = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_plugin_registrations_name", "name", unique=True),
        Index("ix_plugin_registrations_type", "type"),
        Index("ix_plugin_registrations_enabled", "enabled"),
    )
