from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.security import verify_token, get_current_user
from app.services import (
    EngagementService, AssetService, TargetService, ScanService,
    JobService, PluginService, EvidenceService, FindingService
)
from app.schemas.engagement import EngagementCreate, EngagementResponse
from app.schemas.asset import AssetCreate, AssetResponse
from app.schemas.target import TargetCreate, TargetResponse
from app.schemas.scan import ScanCreate, ScanResponse
from app.utils.logger import logger
from app.utils.responses import success_response, paginated_response, error_response

router = APIRouter(prefix="/api/v1", tags=["core"])

# Engagements (7 endpoints)
@router.post("/engagements", response_model=dict, status_code=201)
def create_engagement(
    engagement: EngagementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new engagement."""
    try:
        result = EngagementService.create_engagement(db, engagement)
        logger.info("engagement_created", user_id=current_user["user_id"], engagement_id=result.id)
        return success_response(EngagementResponse.from_orm(result))
    except Exception as e:
        logger.error("engagement_creation_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/engagements", response_model=dict)
def list_engagements(
    skip: int = 0,
    limit: int = 50,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all engagements."""
    try:
        engagements, total = EngagementService.list_engagements(db, skip, limit, active_only)
        data = [EngagementResponse.from_orm(e) for e in engagements]
        logger.info("engagements_listed", user_id=current_user["user_id"], count=len(data))
        return paginated_response(data, total, skip, limit)
    except Exception as e:
        logger.error("engagements_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/engagements/{engagement_id}", response_model=dict)
def get_engagement(
    engagement_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific engagement."""
    try:
        result = EngagementService.get_engagement(db, engagement_id)
        logger.info("engagement_retrieved", user_id=current_user["user_id"], engagement_id=engagement_id)
        return success_response(EngagementResponse.from_orm(result))
    except Exception as e:
        logger.error("engagement_retrieval_failed", user_id=current_user["user_id"], engagement_id=engagement_id, error=str(e))
        return error_response(f"Engagement not found: {str(e)}", status_code=404)

# Assets (7 endpoints)
@router.post("/assets", response_model=dict, status_code=201)
def create_asset(
    asset: AssetCreate,
    engagement_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create asset in engagement."""
    try:
        result = AssetService.create_asset(db, engagement_id, asset)
        logger.info("asset_created", user_id=current_user["user_id"], asset_id=result.id)
        return success_response(AssetResponse.from_orm(result))
    except Exception as e:
        logger.error("asset_creation_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/assets", response_model=dict)
def list_assets(
    engagement_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List assets in engagement."""
    try:
        assets, total = AssetService.list_assets(db, engagement_id, skip, limit)
        data = [AssetResponse.from_orm(a) for a in assets]
        logger.info("assets_listed", user_id=current_user["user_id"], count=len(data))
        return paginated_response(data, total, skip, limit)
    except Exception as e:
        logger.error("assets_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/assets/{asset_id}", response_model=dict)
def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific asset."""
    try:
        result = AssetService.get_asset(db, asset_id)
        logger.info("asset_retrieved", user_id=current_user["user_id"], asset_id=asset_id)
        return success_response(AssetResponse.from_orm(result))
    except Exception as e:
        logger.error("asset_retrieval_failed", user_id=current_user["user_id"], asset_id=asset_id, error=str(e))
        return error_response(f"Asset not found: {str(e)}", status_code=404)

# Targets
@router.post("/targets", response_model=dict, status_code=201)
def create_target(
    target: TargetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create target."""
    try:
        result = TargetService.create_target(db, target)
        logger.info("target_created", user_id=current_user["user_id"], target_id=result.id)
        return success_response(TargetResponse.from_orm(result))
    except Exception as e:
        logger.error("target_creation_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/targets", response_model=dict)
def list_targets(
    engagement_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List targets."""
    try:
        targets, total = TargetService.list_targets(db, engagement_id, skip, limit)
        data = [TargetResponse.from_orm(t) for t in targets]
        logger.info("targets_listed", user_id=current_user["user_id"], count=len(data))
        return paginated_response(data, total, skip, limit)
    except Exception as e:
        logger.error("targets_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.post("/targets/import/csv", response_model=dict)
def import_targets_csv(
    engagement_id: UUID = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Import targets from CSV."""
    try:
        content = file.file.read().decode("utf-8")
        targets, errors = TargetService.import_csv(db, engagement_id, content)
        data = [TargetResponse.from_orm(t) for t in targets]
        logger.info("targets_csv_imported", user_id=current_user["user_id"], count=len(data), errors=len(errors))
        return success_response({
            "imported": len(targets),
            "errors": errors,
            "data": data
        })
    except Exception as e:
        logger.error("targets_csv_import_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.post("/targets/import/txt", response_model=dict)
def import_targets_txt(
    engagement_id: UUID = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Import targets from TXT."""
    try:
        content = file.file.read().decode("utf-8")
        targets, errors = TargetService.import_txt(db, engagement_id, content)
        data = [TargetResponse.from_orm(t) for t in targets]
        logger.info("targets_txt_imported", user_id=current_user["user_id"], count=len(data), errors=len(errors))
        return success_response({
            "imported": len(targets),
            "errors": errors,
            "data": data
        })
    except Exception as e:
        logger.error("targets_txt_import_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.post("/targets/import/xml", response_model=dict)
def import_targets_xml(
    engagement_id: UUID = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Import targets from XML."""
    try:
        content = file.file.read().decode("utf-8")
        targets, errors = TargetService.import_xml(db, engagement_id, content)
        data = [TargetResponse.from_orm(t) for t in targets]
        logger.info("targets_xml_imported", user_id=current_user["user_id"], count=len(data), errors=len(errors))
        return success_response({
            "imported": len(targets),
            "errors": errors,
            "data": data
        })
    except Exception as e:
        logger.error("targets_xml_import_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

# Scans
@router.post("/scans", response_model=dict, status_code=201)
def create_scan(
    scan: ScanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create scan."""
    try:
        result = ScanService.create_scan(db, scan)
        logger.info("scan_created", user_id=current_user["user_id"], scan_id=result.id)
        return success_response(ScanResponse.from_orm(result))
    except Exception as e:
        logger.error("scan_creation_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.get("/scans", response_model=dict)
def list_scans(
    engagement_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List scans."""
    try:
        scans, total = ScanService.list_scans(db, engagement_id, skip, limit)
        data = [ScanResponse.from_orm(s) for s in scans]
        logger.info("scans_listed", user_id=current_user["user_id"], count=len(data))
        return paginated_response(data, total, skip, limit)
    except Exception as e:
        logger.error("scans_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

@router.patch("/scans/{scan_id}/status", response_model=dict)
def update_scan_status(
    scan_id: UUID,
    status: str = Query(...),
    progress: int = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update scan status."""
    try:
        from app.models.scan import ScanStatus
        result = ScanService.update_scan_status(db, scan_id, ScanStatus[status.upper()], progress)
        logger.info("scan_status_updated", user_id=current_user["user_id"], scan_id=scan_id, status=status)
        return success_response(ScanResponse.from_orm(result))
    except Exception as e:
        logger.error("scan_status_update_failed", user_id=current_user["user_id"], scan_id=scan_id, error=str(e))
        return error_response(str(e), status_code=400)

# Findings
@router.get("/findings", response_model=dict)
def list_findings(
    engagement_id: UUID = Query(...),
    severity: str = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List findings."""
    try:
        findings, total = FindingService.list_findings(db, engagement_id, skip, limit, severity)
        logger.info("findings_listed", user_id=current_user["user_id"], count=len(findings))
        return paginated_response(findings, total, skip, limit)
    except Exception as e:
        logger.error("findings_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

# Plugins
@router.get("/plugins", response_model=dict)
def list_plugins(
    skip: int = 0,
    limit: int = 50,
    enabled_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List plugins."""
    try:
        plugins, total = PluginService.list_plugins(db, skip, limit, enabled_only)
        logger.info("plugins_listed", user_id=current_user["user_id"], count=len(plugins))
        return paginated_response(plugins, total, skip, limit)
    except Exception as e:
        logger.error("plugins_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

# Evidence
@router.get("/evidence", response_model=dict)
def list_evidence(
    scan_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List evidence."""
    try:
        evidence, total = EvidenceService.list_evidence(db, scan_id, skip, limit)
        logger.info("evidence_listed", user_id=current_user["user_id"], count=len(evidence))
        return paginated_response(evidence, total, skip, limit)
    except Exception as e:
        logger.error("evidence_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)

# Jobs
@router.get("/jobs", response_model=dict)
def list_jobs(
    scan_id: UUID = Query(...),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List jobs."""
    try:
        jobs, total = JobService.list_jobs(db, scan_id, skip, limit)
        logger.info("jobs_listed", user_id=current_user["user_id"], count=len(jobs))
        return paginated_response(jobs, total, skip, limit)
    except Exception as e:
        logger.error("jobs_list_failed", user_id=current_user["user_id"], error=str(e))
        return error_response(str(e), status_code=400)
