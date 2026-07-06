from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.engagement import EngagementStatus, EngagementType

class EngagementCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: EngagementType
    client: str = Field(..., min_length=1, max_length=255)
    scope: Optional[str] = None
    owner: str = Field(..., min_length=1, max_length=255)
    team_members: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

class EngagementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[EngagementStatus] = None
    scope: Optional[str] = None
    team_members: Optional[str] = None
    end_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class EngagementResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    type: EngagementType
    status: EngagementStatus
    client: str
    owner: str
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EngagementDetailResponse(EngagementResponse):
    scope: Optional[str]
    team_members: Optional[str]
    due_date: Optional[datetime]
