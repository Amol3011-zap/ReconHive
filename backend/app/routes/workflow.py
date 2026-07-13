from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.security import get_current_user
from app.services import ScanExecutorService, WorkerService, ScanService, EngagementService, FindingService
from app.models import WorkerType
from app.utils.responses import success_response, error_response
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1", tags=["workflow"])

# Scan Execution
@router.post("/scans/{scan_id}/start", response_model=dict, status_code=200)
def start_scan(
    scan_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start a queued scan."""
    try:
        result = ScanExecutorService.start_scan(db, scan_id)
        logger.info("scan_execution_started", scan_id=scan_id)
        return success_response({"id": str(result.id), "status": result.status.value, "worker_id": result.worker_id})
    except Exception as e:
        logger.error("scan_execution_failed", scan_id=scan_id, error=str(e))
        return error_response(str(e), status_code=400)

@router.post("/scans/{scan_id}/progress", response_model=dict, status_code=200)
def simulate_scan_progress(
    scan_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Simulate scan progress."""
    try:
        result = ScanExecutorService.simulate_scan_progress(db, scan_id)
        return success_response({
            "id": str(result.id),
            "status": result.status.value,
            "progress": result.progress_percent,
            "stage": result.current_stage
        })
    except Exception as e:
        logger.error("scan_progress_failed", scan_id=scan_id, error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/scans/{scan_id}/details", response_model=dict)
def get_scan_details(
    scan_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed scan information including jobs and findings."""
    try:
        from app.models import Scan, Job, Finding, Evidence
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        jobs = db.query(Job).filter(Job.scan_id == scan_id).all()
        findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
        evidence = db.query(Evidence).filter(Evidence.scan_id == scan_id).all()

        jobs_data = [{
            "id": str(j.id),
            "plugin": j.plugin_name,
            "status": j.status.value,
            "progress": j.progress_percent,
            "logs": j.logs.split('\n') if j.logs else []
        } for j in jobs]

        findings_data = [{
            "id": str(f.id),
            "title": f.title,
            "severity": f.severity.value,
            "cvss": f.cvss_score,
            "status": f.status.value
        } for f in findings]

        evidence_data = [{
            "id": str(e.id),
            "name": e.name,
            "type": e.type.value
        } for e in evidence]

        return success_response({
            "scan": {
                "id": str(scan.id),
                "name": scan.name,
                "status": scan.status.value,
                "progress": scan.progress_percent,
                "stage": scan.current_stage,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "worker_id": scan.worker_id,
                "duration_seconds": scan.duration_seconds
            },
            "jobs": jobs_data,
            "findings": findings_data,
            "evidence": evidence_data
        })
    except Exception as e:
        logger.error("scan_details_failed", scan_id=scan_id, error=str(e))
        return error_response(str(e), status_code=400)

# Workers
@router.post("/workers", response_model=dict, status_code=201)
def create_worker(
    name: str = Query(...),
    worker_type: str = Query("reconnaissance"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new worker."""
    try:
        wtype = WorkerType[worker_type.upper()]
        result = WorkerService.create_worker(db, name, wtype)
        logger.info("worker_created", worker_id=result.id)
        return success_response({
            "id": str(result.id),
            "name": result.name,
            "type": result.type.value,
            "status": result.status.value
        })
    except Exception as e:
        logger.error("worker_creation_failed", error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/workers", response_model=dict)
def list_workers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all workers."""
    try:
        workers, total = WorkerService.list_workers(db, skip, limit)
        workers_data = [{
            "id": str(w.id),
            "name": w.name,
            "type": w.type.value,
            "status": w.status.value,
            "cpu_usage": w.cpu_usage,
            "memory_usage": w.memory_usage,
            "active_jobs": w.active_jobs,
            "queue_depth": w.queue_depth,
            "completed_jobs": w.completed_jobs,
            "failed_jobs": w.failed_jobs,
            "is_enabled": w.is_enabled
        } for w in workers]
        from app.utils.responses import paginated_response
        return paginated_response(workers_data, total, skip, limit)
    except Exception as e:
        logger.error("workers_list_failed", error=str(e))
        return error_response(str(e), status_code=400)

@router.post("/workers/{worker_id}/heartbeat", response_model=dict)
def worker_heartbeat(
    worker_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update worker heartbeat."""
    try:
        result = WorkerService.heartbeat(db, worker_id)
        return success_response({
            "id": str(result.id),
            "status": result.status.value,
            "last_heartbeat": result.last_heartbeat.isoformat()
        })
    except Exception as e:
        logger.error("worker_heartbeat_failed", worker_id=worker_id, error=str(e))
        return error_response(str(e), status_code=400)

# Dashboard
@router.get("/dashboard/stats", response_model=dict)
def get_dashboard_stats(
    engagement_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    try:
        return success_response({
            "engagements": {
                "total": 0,
                "active": 0
            },
            "assets": {
                "total": 0
            },
            "scans": {
                "running": 0,
                "completed": 0
            },
            "findings": {
                "total": 0,
                "critical": 0,
                "high": 0
            },
            "evidence": {
                "total": 0
            },
            "workers": {
                "online": 0,
                "total": 0
            }
        })
    except Exception as e:
        logger.error("dashboard_stats_failed", error=str(e))
        return error_response(str(e), status_code=400)

# Activity Timeline
@router.get("/dashboard/activity", response_model=dict)
def get_activity_timeline(
    engagement_id: UUID = Query(None),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recent activity timeline."""
    return success_response({"activities": []})

# Complete Dashboard Data
@router.get("/dashboard/full", response_model=dict)
def get_dashboard_full(
    engagement_id: UUID = Query(None),
    db: Session = Depends(get_db)
):
    """Get complete dashboard data: findings by severity, top findings, assets, evidence."""
    return success_response({
        "findings_by_severity": {},
        "top_findings": [],
        "asset_summary": {},
        "evidence_summary": {},
        "scans_overview": []
    })
