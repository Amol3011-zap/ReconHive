from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class TargetCreate(BaseModel):
    engagement_id: UUID
    asset_id: Optional[UUID] = None
    host: str
    port: Optional[str] = None
    service: Optional[str] = None
    protocol: Optional[str] = None
    auth_type: Optional[str] = None

class TargetResponse(BaseModel):
    id: UUID
    host: str
    port: Optional[str]
    service: Optional[str]
    protocol: Optional[str]
    is_in_scope: bool
    created_at: datetime

    class Config:
        from_attributes = True
