from sqlalchemy import Column, String, DateTime, JSON, Index, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.db.base import Base
import enum


class ConfigStatus(str, enum.Enum):
    """Configuration lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class PluginConfiguration(Base):
    """Per-plugin configuration management"""
    __tablename__ = "plugin_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plugin_id = Column(UUID(as_uuid=True), ForeignKey("plugin_registrations.id"), nullable=False, index=True)

    # Configuration identity
    name = Column(String(255), nullable=False)  # e.g., "default", "aggressive", "light"
    description = Column(String(500))
    version = Column(String(50), default="1.0.0")

    # Configuration data
    settings = Column(JSON, nullable=False, default={})  # The actual config values
    env_vars = Column(JSON, default={})  # Environment variables
    secrets = Column(JSON, default={})  # Encrypted sensitive data (refs, not actual values)

    # Status management
    status = Column(SQLEnum(ConfigStatus), default=ConfigStatus.DRAFT, index=True)
    is_default = Column(Boolean, default=False, index=True)

    # Validation & tracking
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSON, default=[])

    # Audit fields
    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    activated_at = Column(DateTime)

    # Usage tracking
    last_used_at = Column(DateTime)
    use_count = Column(String, default="0")  # Counter for tracking usage

    __table_args__ = (
        Index("ix_plugin_config_plugin_id", "plugin_id"),
        Index("ix_plugin_config_status", "status"),
        Index("ix_plugin_config_is_default", "is_default"),
        Index("ix_plugin_config_active", "plugin_id", "status"),
    )


class ConfigurationHistory(Base):
    """Audit trail for configuration changes"""
    __tablename__ = "configuration_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("plugin_configurations.id"), nullable=False, index=True)

    # Change tracking
    action = Column(String(50), nullable=False)  # created, updated, activated, deactivated
    changed_by = Column(String(255))

    # Before/after
    old_settings = Column(JSON)
    new_settings = Column(JSON)

    # Metadata
    reason = Column(String(500))  # Why the change was made
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_config_history_config_id", "config_id"),
        Index("ix_config_history_action", "action"),
    )
