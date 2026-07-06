from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.scan import ScanStatus

class ScanCreate(BaseModel):
    engagement_id: UUID
    asset_id: UUID
    name: str
    plugin_names: List[str]
    configuration: Optional[dict] = None

class ScanResponse(BaseModel):
    id: UUID
    name: str
    status: ScanStatus
    progress_percent: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
