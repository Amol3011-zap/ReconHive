from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class CloudProvider(PyEnum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITALOCEAN = "digitalocean"
    LINODE = "linode"
    HEROKU = "heroku"
    VERCEL = "vercel"

class CloudAssetType(PyEnum):
    S3_BUCKET = "s3_bucket"
    GCS_BUCKET = "gcs_bucket"
    AZURE_BLOB = "azure_blob"
    EC2_INSTANCE = "ec2_instance"
    RDS_DATABASE = "rds_database"
    LAMBDA_FUNCTION = "lambda_function"
    API_GATEWAY = "api_gateway"
    CLOUDFRONT = "cloudfront"
    OTHER = "other"

class AccessLevel(PyEnum):
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    PRIVATE = "private"
    UNKNOWN = "unknown"

class CloudAsset(Base):
    __tablename__ = "cloud_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    # Cloud asset info
    provider = Column(String(50), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    asset_name = Column(String(255), nullable=False, index=True)
    asset_arn = Column(String(500))  # AWS ARN or equivalent
    asset_url = Column(String(500))

    # Location
    region = Column(String(100))
    account_id = Column(String(100))

    # Access control
    access_level = Column(String(50), nullable=False)
    is_publicly_accessible = Column(Boolean, default=False, index=True)
    is_authenticated_required = Column(Boolean, default=False)
    acl_details = Column(JSONB)  # Access control list information

    # Content
    object_count = Column(Integer)
    total_size_bytes = Column(Integer)
    last_modified = Column(DateTime)
    creation_date = Column(DateTime)

    # Sensitive data
    contains_sensitive_files = Column(Boolean, default=False)
    sensitive_file_patterns = Column(JSONB)  # File patterns found
    sample_files = Column(JSONB)  # Sample file names

    # Discovery
    discovered_by = Column(String(100))  # "cloud_enum", "s3scanner", "manual", etc.
    discovered_date = Column(DateTime, default=datetime.utcnow)
    verified_date = Column(DateTime)

    # Risk assessment
    risk_level = Column(String(20), default="unknown")  # low, medium, high, critical
    misconfiguration_count = Column(Integer, default=0)

    # Findings
    related_finding_ids = Column(JSONB)

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", foreign_keys=[engagement_id])
    asset = relationship("Asset", foreign_keys=[asset_id])
    scan = relationship("Scan", foreign_keys=[scan_id])

    __table_args__ = (
        Index("ix_cloud_assets_engagement_id", "engagement_id"),
        Index("ix_cloud_assets_asset_id", "asset_id"),
        Index("ix_cloud_assets_provider", "provider"),
        Index("ix_cloud_assets_asset_name", "asset_name"),
        Index("ix_cloud_assets_is_publicly_accessible", "is_publicly_accessible"),
    )
