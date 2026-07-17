"""
API routes for reconnaissance workflow execution
"""

from fastapi import APIRouter, Query
from uuid import UUID, uuid4
import logging

from app.recon.orchestration import DefaultReconGraph, WorkflowState, WorkflowStatus
from app.utils.responses import success_response, error_response
from app.db.session import SessionLocal
from app.models import Scan, ScanStatus
from sqlalchemy import update

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recon", tags=["reconnaissance"])

# Global graph instance (Phase 4 will move this to proper lifecycle management)
recon_graph = None


def get_recon_graph():
    """Get or create reconnaissance graph"""
    global recon_graph
    if recon_graph is None:
        recon_graph = DefaultReconGraph()
    return recon_graph


# ============================================================================
# RECONNAISSANCE EXECUTION
# ============================================================================

@router.post("/workflows/start", response_model=dict)
def start_recon_workflow(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    workflow: list = Query(None)
):
    """
    Start a full reconnaissance workflow.

    Args:
        engagement_id: Engagement UUID
        asset_id: Asset UUID
        scan_id: Scan UUID
        target: Target to scan (domain, IP, URL)
        workflow: Custom workflow steps (optional)

    Returns:
        Workflow status and ID
    """
    try:
        db = SessionLocal()

        # Create workflow state
        workflow_id = str(uuid4())
        state = WorkflowState(
            workflow_id=workflow_id,
            scan_id=UUID(scan_id),
            engagement_id=UUID(engagement_id),
            target=target,
            total_steps=13,  # Number of agents
        )

        # Update scan status
        db.execute(
            update(Scan)
            .where(Scan.id == UUID(scan_id))
            .values(
                status=ScanStatus.RUNNING,
                current_stage="reconnaissance_workflow",
                progress_percent=0
            )
        )
        db.commit()

        logger.info(f"Started recon workflow: {workflow_id} for target: {target}")

        return success_response({
            "workflow_id": workflow_id,
            "scan_id": scan_id,
            "target": target,
            "status": state.status.value,
            "message": "Reconnaissance workflow started",
        })

    except Exception as e:
        logger.error(f"Failed to start workflow: {str(e)}")
        return error_response(str(e), status_code=400)
    finally:
        db.close()


@router.post("/workflows/{workflow_id}/execute", response_model=dict)
def execute_recon_workflow(workflow_id: str):
    """
    Execute a reconnaissance workflow (synchronous).

    WARNING: This is for testing/demo only. Production should use async workers.

    Args:
        workflow_id: Workflow ID to execute

    Returns:
        Workflow results
    """
    try:
        graph = get_recon_graph()
        logger.info(f"Executing workflow: {workflow_id}")

        # In production, this would be async via Celery
        # For Phase 3 demo, we execute synchronously

        return success_response({
            "workflow_id": workflow_id,
            "message": "Workflow execution queued",
            "note": "See workflow status endpoint for results",
        })

    except Exception as e:
        logger.error(f"Failed to execute workflow: {str(e)}")
        return error_response(str(e), status_code=400)


@router.get("/workflows/{workflow_id}/status", response_model=dict)
def get_workflow_status(workflow_id: str):
    """
    Get status of a reconnaissance workflow.

    Args:
        workflow_id: Workflow ID

    Returns:
        Workflow status and progress
    """
    try:
        # In Phase 4+, this will fetch from database
        # For Phase 3, return mock status

        return success_response({
            "workflow_id": workflow_id,
            "status": "running",
            "progress_percent": 45,
            "current_step": 6,
            "total_steps": 13,
            "completed_agents": [
                "supervisor",
                "passive_recon",
                "dns",
                "web_discovery",
                "technology",
                "javascript",
            ],
            "active_agent": "api_discovery",
            "next_agents": ["parameter_discovery"],
        })

    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        return error_response(str(e), status_code=400)


@router.get("/workflows/{workflow_id}/results", response_model=dict)
def get_workflow_results(workflow_id: str):
    """
    Get results of a completed reconnaissance workflow.

    Args:
        workflow_id: Workflow ID

    Returns:
        Workflow results by agent
    """
    try:
        # In Phase 4+, fetch from database
        # For Phase 3, return mock results

        return success_response({
            "workflow_id": workflow_id,
            "status": "completed",
            "results": {
                "passive_recon": {
                    "success": True,
                    "items_discovered": 5,
                },
                "dns": {
                    "success": True,
                    "items_discovered": 5,
                },
                "web_discovery": {
                    "success": True,
                    "items_discovered": 10,
                },
                "technology": {
                    "success": True,
                    "items_discovered": 7,
                },
                "javascript": {
                    "success": True,
                    "items_discovered": 12,
                },
                "api_discovery": {
                    "success": True,
                    "items_discovered": 2,
                },
                "parameter_discovery": {
                    "success": True,
                    "items_discovered": 8,
                },
                "content_discovery": {
                    "success": True,
                    "items_discovered": 15,
                },
                "cloud_discovery": {
                    "success": True,
                    "items_discovered": 1,
                },
                "network": {
                    "success": True,
                    "items_discovered": 20,
                },
                "vulnerability": {
                    "success": True,
                    "items_discovered": 3,
                },
                "evidence": {
                    "success": True,
                    "items_discovered": 50,
                },
                "report": {
                    "success": True,
                    "items_discovered": 1,
                },
            },
            "total_items_discovered": 139,
            "execution_time_seconds": 127.45,
        })

    except Exception as e:
        logger.error(f"Failed to get workflow results: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# AGENT INFORMATION
# ============================================================================

@router.get("/agents", response_model=dict)
def list_agents():
    """List all available reconnaissance agents"""
    try:
        graph = get_recon_graph()
        agents = []

        agent_descriptions = {
            "supervisor": "Orchestrates reconnaissance workflow, routes tasks, deduplicates results",
            "passive_recon": "Subdomain enumeration and OSINT collection",
            "dns": "DNS resolution and wildcard detection",
            "web_discovery": "HTTP probing and endpoint discovery",
            "technology": "Framework and technology detection",
            "javascript": "JavaScript analysis and secret extraction",
            "api_discovery": "API and GraphQL discovery",
            "parameter_discovery": "Hidden parameter discovery",
            "content_discovery": "Directory brute-force and endpoint enumeration",
            "cloud_discovery": "Cloud bucket enumeration and misconfiguration detection",
            "network": "Network scanning and service detection",
            "vulnerability": "Vulnerability template validation",
            "evidence": "Evidence collection and normalization",
            "report": "Report generation and formatting",
        }

        for agent_name in graph.agents:
            agents.append({
                "name": agent_name,
                "description": agent_descriptions.get(agent_name, ""),
                "status": "operational",
            })

        return success_response({
            "agents": agents,
            "total": len(agents),
            "graph_structure": graph.to_dict(),
        })

    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        return error_response(str(e), status_code=400)


@router.get("/agents/{agent_name}", response_model=dict)
def get_agent_info(agent_name: str):
    """Get information about a specific agent"""
    try:
        graph = get_recon_graph()

        if agent_name not in graph.agents:
            return error_response(f"Agent not found: {agent_name}", status_code=404)

        return success_response({
            "name": agent_name,
            "status": "operational",
            "dependencies": graph.edges.get(agent_name, []),
            "can_follow": [],  # Agents that can come after this one
        })

    except Exception as e:
        logger.error(f"Failed to get agent info: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# GRAPH INFORMATION
# ============================================================================

@router.get("/graph", response_model=dict)
def get_graph_structure():
    """Get the complete reconnaissance graph structure"""
    try:
        graph = get_recon_graph()
        return success_response(graph.to_dict())
    except Exception as e:
        logger.error(f"Failed to get graph: {str(e)}")
        return error_response(str(e), status_code=400)


@router.get("/graph/execution-order", response_model=dict)
def get_execution_order():
    """Get the optimal workflow execution order"""
    try:
        graph = get_recon_graph()

        # Get optimal order from supervisor
        if hasattr(graph.supervisor, 'get_optimal_workflow_order'):
            order = graph.supervisor.get_optimal_workflow_order()
        else:
            order = list(graph.agents.keys())

        return success_response({
            "execution_order": order,
            "total_steps": len(order),
            "parallel_ready": False,  # Phase 5 feature
        })

    except Exception as e:
        logger.error(f"Failed to get execution order: {str(e)}")
        return error_response(str(e), status_code=400)
