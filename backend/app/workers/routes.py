"""
API routes for worker management and monitoring
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from uuid import UUID
import logging

from app.workers.monitor import WorkerMonitor
from app.workers.celery_app import CeleryTaskManager, celery_app
from app.workers.tasks import (
    ping_task, passive_recon_task, dns_resolution_task,
    web_discovery_task, technology_detection_task,
    api_discovery_task, cloud_enumeration_task,
    network_scan_task, orchestrate_recon_workflow
)
from app.utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workers", tags=["workers"])


# ============================================================================
# HEALTH & MONITORING
# ============================================================================

@router.get("/health", response_model=dict)
def get_worker_health():
    """Get overall worker system health"""
    health = WorkerMonitor.get_health_check()
    return success_response(health)


@router.get("/status", response_model=dict)
def get_worker_status():
    """Get detailed worker status"""
    stats = WorkerMonitor.get_worker_stats()
    active = WorkerMonitor.get_active_tasks()
    queues = WorkerMonitor.get_queue_stats()
    tasks_info = WorkerMonitor.get_registered_tasks()

    return success_response({
        "workers": stats,
        "active_tasks": active,
        "queues": queues,
        "registered_tasks": tasks_info
    })


@router.get("/stats", response_model=dict)
def get_worker_statistics():
    """Get worker statistics"""
    worker_stats = WorkerMonitor.get_worker_stats()
    tool_run_stats = WorkerMonitor.get_tool_run_stats()

    return success_response({
        "workers": worker_stats,
        "tool_runs": tool_run_stats
    })


# ============================================================================
# TASK MANAGEMENT
# ============================================================================

@router.get("/tasks/active", response_model=dict)
def list_active_tasks():
    """List all active tasks"""
    tasks = WorkerMonitor.get_active_tasks()
    return success_response(tasks)


@router.get("/tasks/registered", response_model=dict)
def list_registered_tasks():
    """List all registered task types"""
    tasks = WorkerMonitor.get_registered_tasks()
    return success_response(tasks)


@router.get("/tasks/{task_id}", response_model=dict)
def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        status = CeleryTaskManager.get_task_status(task_id)
        return success_response(status)
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/{task_id}/revoke", response_model=dict)
def revoke_task(task_id: str, terminate: bool = False):
    """Revoke a task"""
    try:
        result = CeleryTaskManager.revoke_task(task_id, terminate=terminate)
        if result:
            return success_response({"revoked": True, "task_id": task_id})
        else:
            return error_response(f"Failed to revoke task {task_id}", status_code=400)
    except Exception as e:
        logger.error(f"Failed to revoke task: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# QUEUE MANAGEMENT
# ============================================================================

@router.get("/queues", response_model=dict)
def list_queues():
    """List all queues and their status"""
    queues = WorkerMonitor.get_queue_stats()
    return success_response(queues)


@router.post("/queues/{queue_name}/purge", response_model=dict)
def purge_queue(queue_name: str):
    """Clear all tasks from a queue"""
    try:
        result = CeleryTaskManager.purge_queue(queue_name)
        if result:
            return success_response({"purged": True, "queue": queue_name})
        else:
            return error_response(f"Failed to purge queue {queue_name}", status_code=400)
    except Exception as e:
        logger.error(f"Failed to purge queue: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# TEST TASKS
# ============================================================================

@router.post("/test/ping", response_model=dict)
def test_ping():
    """Test worker connectivity with ping task"""
    try:
        result = ping_task.apply_async()
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "message": "Ping task queued"
        })
    except Exception as e:
        logger.error(f"Failed to queue ping task: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# RECONNAISSANCE TASKS
# ============================================================================

@router.post("/tasks/passive-recon", response_model=dict)
def queue_passive_recon(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    sources: list = Query(None)
):
    """Queue a passive reconnaissance task"""
    try:
        result = passive_recon_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            kwargs={"sources": sources or []},
            queue="recon"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue passive recon: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/dns-resolution", response_model=dict)
def queue_dns_resolution(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    resolver: str = "8.8.8.8"
):
    """Queue a DNS resolution task"""
    try:
        result = dns_resolution_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            kwargs={"resolver": resolver},
            queue="dns"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue DNS resolution: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/web-discovery", response_model=dict)
def queue_web_discovery(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Queue a web discovery task"""
    try:
        result = web_discovery_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            queue="web"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue web discovery: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/technology-detection", response_model=dict)
def queue_technology_detection(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Queue a technology detection task"""
    try:
        result = technology_detection_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            queue="tech"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue technology detection: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/api-discovery", response_model=dict)
def queue_api_discovery(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Queue an API discovery task"""
    try:
        result = api_discovery_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            queue="api"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue API discovery: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/cloud-enumeration", response_model=dict)
def queue_cloud_enumeration(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Queue a cloud enumeration task"""
    try:
        result = cloud_enumeration_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            queue="cloud"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue cloud enumeration: {str(e)}")
        return error_response(str(e), status_code=400)


@router.post("/tasks/network-scan", response_model=dict)
def queue_network_scan(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Queue a network scan task"""
    try:
        result = network_scan_task.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            queue="network"
        )
        return success_response({
            "task_id": str(result.id),
            "state": result.state,
            "target": target
        })
    except Exception as e:
        logger.error(f"Failed to queue network scan: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# WORKFLOW ORCHESTRATION
# ============================================================================

@router.post("/workflows/recon", response_model=dict)
def start_recon_workflow(
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    workflow: list = Query(None)
):
    """Start a complete reconnaissance workflow"""
    try:
        result = orchestrate_recon_workflow.apply_async(
            args=(engagement_id, asset_id, scan_id, target),
            kwargs={"workflow": workflow}
        )
        return success_response({
            "workflow_id": str(result.id),
            "state": result.state,
            "target": target,
            "workflow": workflow or "default"
        })
    except Exception as e:
        logger.error(f"Failed to start recon workflow: {str(e)}")
        return error_response(str(e), status_code=400)


@router.get("/workflows/{workflow_id}", response_model=dict)
def get_workflow_status(workflow_id: str):
    """Get status of a reconnaissance workflow"""
    try:
        status = CeleryTaskManager.get_task_status(workflow_id)
        return success_response(status)
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        return error_response(str(e), status_code=400)


# ============================================================================
# SCAN PROGRESS
# ============================================================================

@router.get("/scans/{scan_id}/progress", response_model=dict)
def get_scan_progress(scan_id: str):
    """Get progress of a scan"""
    try:
        progress = WorkerMonitor.get_scan_progress(scan_id)
        if "error" in progress:
            return error_response(progress["error"], status_code=404)
        return success_response(progress)
    except Exception as e:
        logger.error(f"Failed to get scan progress: {str(e)}")
        return error_response(str(e), status_code=400)
