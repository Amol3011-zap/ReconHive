"""
Celery task definitions for reconnaissance workers
"""

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from typing import Optional, Dict, Any
from uuid import UUID
import logging
from datetime import datetime

from app.workers.celery_app import celery_app
from app.workers.base import BaseWorker, WorkerResult, WorkerConfig, ReconWorker
from app.db.session import SessionLocal
from app.models import ToolRun, ToolRunStatus, Scan, ScanStatus
from app.services.recon_service import ToolRunService

logger = logging.getLogger(__name__)


# ============================================================================
# GENERIC TASK WRAPPER
# ============================================================================

def execute_worker_task(
    worker_class,
    worker_config: Optional[Dict[str, Any]] = None,
    task_id: str = None,
    engagement_id: str = None,
    scan_id: str = None,
    **worker_kwargs
) -> Dict[str, Any]:
    """
    Generic wrapper to execute any worker and track results in database.

    Args:
        worker_class: The worker class to instantiate
        worker_config: Configuration for the worker
        task_id: Celery task ID for tracking
        engagement_id: Engagement UUID
        scan_id: Scan UUID
        **worker_kwargs: Arguments to pass to worker.execute()

    Returns:
        Result dictionary
    """
    db = SessionLocal()
    tool_run = None

    try:
        # Initialize worker
        config = WorkerConfig(**worker_config) if worker_config else WorkerConfig()
        worker = worker_class(config=config)

        # Create tool run record
        if engagement_id and scan_id:
            try:
                tool_run = ToolRunService.create_tool_run(
                    db=db,
                    engagement_id=UUID(engagement_id),
                    scan_id=UUID(scan_id),
                    job_id=UUID(task_id) if task_id else None,
                    tool_name=worker.__class__.__name__,
                    target=worker_kwargs.get("target", "unknown"),
                    arguments=worker_kwargs,
                    tool_category=getattr(worker, "tool_category", "unknown")
                )
            except Exception as e:
                logger.error(f"Failed to create tool run: {str(e)}")

        # Execute worker
        logger.info(f"Executing worker: {worker.__class__.__name__}", extra=worker_kwargs)
        result = worker.execute(**worker_kwargs)

        # Update tool run status
        if tool_run:
            ToolRunService.update_tool_run_status(
                db=db,
                run_id=tool_run.id,
                status=ToolRunStatus.COMPLETED if result.success else ToolRunStatus.FAILED,
                exit_code=0 if result.success else 1,
                stdout=result.to_json() if result else None,
                error_message=result.message if not result.success else None
            )

        logger.info(f"Worker completed: {worker.__class__.__name__}", extra=result.to_dict())
        return result.to_dict()

    except SoftTimeLimitExceeded:
        error_msg = "Task timeout - soft limit exceeded"
        logger.error(error_msg)
        if tool_run:
            ToolRunService.update_tool_run_status(
                db=db,
                run_id=tool_run.id,
                status=ToolRunStatus.TIMEOUT,
                error_message=error_msg
            )
        return WorkerResult(
            success=False,
            message=error_msg,
            errors=["Soft time limit exceeded"]
        ).to_dict()

    except Exception as e:
        error_msg = f"Worker execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if tool_run:
            ToolRunService.update_tool_run_status(
                db=db,
                run_id=tool_run.id,
                status=ToolRunStatus.FAILED,
                error_message=error_msg
            )
        return WorkerResult(
            success=False,
            message=error_msg,
            errors=[str(e)]
        ).to_dict()

    finally:
        db.close()


# ============================================================================
# TASK DEFINITIONS
# ============================================================================

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="default"
)
def ping_task(self):
    """Simple ping task for testing"""
    try:
        from app.workers.base import PingWorker
        return execute_worker_task(
            worker_class=PingWorker,
            task_id=self.request.id,
            message="Celery worker is running"
        )
    except Exception as e:
        logger.error(f"Ping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="recon"
)
def passive_recon_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    sources: list = None
):
    """Execute passive reconnaissance"""
    try:
        logger.info(f"Starting passive recon: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target,
            sources=sources or []
        )
    except Exception as e:
        logger.error(f"Passive recon failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="dns"
)
def dns_resolution_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    resolver: str = "8.8.8.8"
):
    """Execute DNS resolution"""
    try:
        logger.info(f"Starting DNS resolution: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target,
            resolver=resolver
        )
    except Exception as e:
        logger.error(f"DNS resolution failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="web"
)
def web_discovery_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Execute web discovery"""
    try:
        logger.info(f"Starting web discovery: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target
        )
    except Exception as e:
        logger.error(f"Web discovery failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="tech"
)
def technology_detection_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Detect technologies"""
    try:
        logger.info(f"Starting technology detection: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target
        )
    except Exception as e:
        logger.error(f"Technology detection failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="api"
)
def api_discovery_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Discover APIs"""
    try:
        logger.info(f"Starting API discovery: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target
        )
    except Exception as e:
        logger.error(f"API discovery failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="cloud"
)
def cloud_enumeration_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Enumerate cloud assets"""
    try:
        logger.info(f"Starting cloud enumeration: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target
        )
    except Exception as e:
        logger.error(f"Cloud enumeration failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,
    time_limit=3600,
    queue="network"
)
def network_scan_task(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str
):
    """Execute network scan"""
    try:
        logger.info(f"Starting network scan: {target}")
        # Implementation will be added in worker plugins
        return execute_worker_task(
            worker_class=ReconWorker,
            task_id=self.request.id,
            engagement_id=engagement_id,
            scan_id=scan_id,
            target=target
        )
    except Exception as e:
        logger.error(f"Network scan failed: {str(e)}")
        raise self.retry(exc=e, countdown=60)


# ============================================================================
# ORCHESTRATION TASKS
# ============================================================================

@shared_task(
    bind=True,
    queue="default"
)
def orchestrate_recon_workflow(
    self,
    engagement_id: str,
    asset_id: str,
    scan_id: str,
    target: str,
    workflow: list = None
):
    """
    Orchestrate complete reconnaissance workflow.

    Workflow order:
    1. Passive recon
    2. DNS resolution
    3. Web discovery
    4. Technology detection
    5. API discovery
    6. Cloud enumeration
    7. Network scanning
    """
    workflow = workflow or [
        "passive_recon",
        "dns_resolution",
        "web_discovery",
        "technology_detection",
        "api_discovery",
        "cloud_enumeration",
        "network_scan"
    ]

    logger.info(f"Starting reconnaissance workflow: {target}")

    db = SessionLocal()
    try:
        # Update scan status
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.status = ScanStatus.RUNNING
            scan.started_at = datetime.utcnow()
            db.commit()

        # Queue tasks in order
        from celery import chain, group

        task_chain = chain()
        for step in workflow:
            if step == "passive_recon":
                task_chain |= passive_recon_task.s(engagement_id, asset_id, scan_id, target)
            elif step == "dns_resolution":
                task_chain |= dns_resolution_task.s(engagement_id, asset_id, scan_id, target)
            elif step == "web_discovery":
                task_chain |= web_discovery_task.s(engagement_id, asset_id, scan_id, target)
            elif step == "technology_detection":
                task_chain |= technology_detection_task.s(engagement_id, asset_id, scan_id, target)
            elif step == "api_discovery":
                task_chain |= api_discovery_task.s(engagement_id, asset_id, scan_id, target)
            elif step == "cloud_enumeration":
                task_chain |= cloud_enumeration_task.s(engagement_id, asset_id, scan_id, target)
            elif step == "network_scan":
                task_chain |= network_scan_task.s(engagement_id, asset_id, scan_id, target)

        # Execute chain
        result = task_chain.apply_async()
        logger.info(f"Workflow queued: {result.id}")

        return {
            "success": True,
            "message": "Reconnaissance workflow started",
            "workflow_id": str(result.id),
            "steps": workflow
        }

    except Exception as e:
        logger.error(f"Workflow orchestration failed: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
            "errors": [str(e)]
        }
    finally:
        db.close()
