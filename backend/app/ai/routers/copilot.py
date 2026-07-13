"""AI Copilot API endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
import logging

from app.ai.schemas import ChatRequest, ChatResponse, SummarizeRequest, SummarizeResponse, AISummary
from app.ai.agents.supervisor.supervisor import SupervisorAgent, ReconAgent, FindingsAgent, ReportAgent, AISecurityAgent
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# Initialize agents
supervisor = SupervisorAgent()
recon_agent = ReconAgent()
findings_agent = FindingsAgent()
report_agent = ReportAgent()
ai_security_agent = AISecurityAgent()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    AI Copilot chat endpoint.

    Accepts a message and routes it to the appropriate agent.
    """
    try:
        # Route the message
        routing = await supervisor.route(request.message)
        agent_name = routing["agent"]

        # Mock engagement data (in production, query the database)
        engagement_data = {
            "asset_count": 0,
            "web_apps": 0,
            "servers": 0,
            "scans_completed": 0,
            "attack_surface": "MEDIUM",
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "risk_score": 0.0
        }

        # Process with appropriate agent
        if agent_name == "recon":
            response = await recon_agent.process(engagement_data, request.message)
        elif agent_name == "findings":
            response = await findings_agent.process(engagement_data, request.message)
        elif agent_name == "reports":
            response = await report_agent.process(engagement_data, request.message)
        elif agent_name == "ai_security":
            response = await ai_security_agent.process(engagement_data, request.message)
        else:
            response = "I'm not sure how to help with that request."

        # Generate response
        message_id = uuid4()
        return ChatResponse(
            conversation_id=request.conversation_id or uuid4(),
            message_id=message_id,
            response=response,
            agent_used=agent_name,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Generate an AI summary of an engagement.

    Supported types:
    - engagement: Overall engagement summary
    - findings: Security findings summary
    - evidence: Evidence summary
    - risk: Risk assessment summary
    """
    try:
        summary_id = uuid4()

        # Mock data
        engagement_data = {
            "asset_count": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "risk_score": 0.0
        }

        # Generate appropriate summary
        if request.summary_type == "engagement":
            summary = await report_agent.process(engagement_data, "engagement summary")
        elif request.summary_type == "findings":
            summary = await findings_agent.process(engagement_data, "findings summary")
        elif request.summary_type == "risk":
            summary = f"**Risk Summary**\n\nOverall Risk Score: {engagement_data.get('risk_score', 0.0)}/10.0\n\nCritical issues: {engagement_data.get('critical', 0)}"
        else:
            summary = "Summary type not supported"

        return SummarizeResponse(
            summary_id=summary_id,
            content=summary,
            risk_score=engagement_data.get("risk_score", 0.0)
        )

    except Exception as e:
        logger.error(f"Summarize error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def status():
    """
    Get AI Copilot status.

    Returns health and availability of all agents.
    """
    return {
        "status": "operational",
        "agents": {
            "supervisor": "ready",
            "recon": "ready",
            "findings": "ready",
            "reports": "ready",
            "ai_security": "ready"
        },
        "version": "0.1.0-phase1",
        "phase": "Phase 1 - Summarization",
        "capabilities": [
            "Chat routing",
            "Engagement summarization",
            "Findings analysis",
            "Report generation",
            "AI security mapping"
        ]
    }


@router.get("/conversations")
async def list_conversations(engagement_id: UUID = None, db: Session = Depends(get_db)):
    """
    List AI conversations for an engagement.

    Returns conversation IDs and metadata (MOCKED for Phase 1).
    """
    # Phase 1: Return empty list
    # Phase 2: Query from database
    return {
        "engagement_id": engagement_id,
        "conversations": [],
        "count": 0
    }
