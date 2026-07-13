from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class AIMessage(BaseModel):
    id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class AIConversation(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[str] = None
    engagement_id: Optional[UUID] = None
    messages: Optional[list[AIMessage]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AISummary(BaseModel):
    id: Optional[UUID] = None
    engagement_id: Optional[UUID] = None
    summary_type: str  # "engagement", "findings", "evidence", "risk"
    content: str
    risk_score: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AIFeedback(BaseModel):
    id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    feedback: str
    rating: Optional[int] = None  # 1-5
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    """AI Copilot chat request"""
    conversation_id: Optional[UUID] = None
    engagement_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    """AI Copilot chat response"""
    conversation_id: UUID
    message_id: UUID
    response: str
    agent_used: str
    timestamp: datetime

class SummarizeRequest(BaseModel):
    """Summarization request"""
    engagement_id: UUID
    summary_type: str  # "engagement", "findings", "evidence", "risk"

class SummarizeResponse(BaseModel):
    """Summarization response"""
    summary_id: UUID
    content: str
    risk_score: Optional[float] = None
