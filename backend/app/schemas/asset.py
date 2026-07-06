from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.asset import AssetType, Environment, Criticality, AssetStatus

class AssetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: AssetType
    environment: Optional[Environment] = None
    criticality: Optional[Criticality] = None
    owner: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    tags: Optional[List[str]] = None
    technology_stack: Optional[List[str]] = None
    operating_system: Optional[str] = None

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    criticality: Optional[Criticality] = None
    environment: Optional[Environment] = None
    tags: Optional[List[str]] = None
    status: Optional[AssetStatus] = None

class AssetResponse(BaseModel):
    id: UUID
    name: str
    type: AssetType
    environment: Optional[Environment]
    criticality: Optional[Criticality]
    status: AssetStatus
    risk_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AssetDetailResponse(AssetResponse):
    description: Optional[str]
    owner: Optional[str]
    display_name: Optional[str]
    tags: Optional[List[str]]
    technology_stack: Optional[List[str]]
