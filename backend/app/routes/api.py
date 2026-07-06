from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.services import (
    EngagementService, AssetService, TargetService, ScanService,
    JobService, PluginService, EvidenceService, FindingService
)
from app.schemas.engagement import EngagementCreate, EngagementResponse
from app.schemas.asset import AssetCreate, AssetResponse
from app.schemas.target import TargetCreate, TargetResponse
from app.schemas.scan import ScanCreate, ScanResponse
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1", tags=["core"])

# Engagements (7 endpoints)
@router.post("/engagements", response_model=EngagementResponse, status_code=201)
def create_engagement(engagement: EngagementCreate, db: Session = Depends(get_db)):
    try:
        return EngagementService.create_engagement(db, engagement)
    except Exception as e:
        logger.error("engagement_creation_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/engagements", response_model=dict)
def list_engagements(skip: int = 0, limit: int = 50, active_only: bool = False, db: Session = Depends(get_db)):
    engagements, total = EngagementService.list_engagements(db, skip, limit, active_only)
    return {"total": total, "data": [EngagementResponse.from_orm(e) for e in engagements]}

@router.get("/engagements/{engagement_id}", response_model=EngagementResponse)
def get_engagement(engagement_id: UUID, db: Session = Depends(get_db)):
    try:
        return EngagementService.get_engagement(db, engagement_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Assets (7 endpoints)
@router.post("/assets", response_model=AssetResponse, status_code=201)
def create_asset(asset: AssetCreate, engagement_id: UUID = Query(...), db: Session = Depends(get_db)):
    try:
        return AssetService.create_asset(db, engagement_id, asset)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assets", response_model=dict)
def list_assets(engagement_id: UUID = Query(...), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    assets, total = AssetService.list_assets(db, engagement_id, skip, limit)
    return {"total": total, "data": [AssetResponse.from_orm(a) for a in assets]}

@router.get("/assets/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: UUID, db: Session = Depends(get_db)):
    try:
        return AssetService.get_asset(db, asset_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Targets (10 endpoints)
@router.post("/targets", response_model=TargetResponse, status_code=201)
def create_target(target: TargetCreate, db: Session = Depends(get_db)):
    try:
        return TargetService.create_target(db, target)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/targets", response_model=dict)
def list_targets(engagement_id: UUID = Query(...), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    targets, total = TargetService.list_targets(db, engagement_id, skip, limit)
    return {"total": total, "data": [TargetResponse.from_orm(t) for t in targets]}

@router.post("/targets/import/csv", response_model=dict)
def import_targets_csv(engagement_id: UUID = Query(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = file.file.read().decode("utf-8")
        targets, errors = TargetService.import_csv(db, engagement_id, content)
        return {"imported": len(targets), "errors": errors, "data": [TargetResponse.from_orm(t) for t in targets]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/targets/import/txt", response_model=dict)
def import_targets_txt(engagement_id: UUID = Query(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = file.file.read().decode("utf-8")
        targets, errors = TargetService.import_txt(db, engagement_id, content)
        return {"imported": len(targets), "errors": errors, "data": [TargetResponse.from_orm(t) for t in targets]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/targets/import/xml", response_model=dict)
def import_targets_xml(engagement_id: UUID = Query(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = file.file.read().decode("utf-8")
        targets, errors = TargetService.import_xml(db, engagement_id, content)
        return {"imported": len(targets), "errors": errors, "data": [TargetResponse.from_orm(t) for t in targets]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Scans (8 endpoints)
@router.post("/scans", response_model=ScanResponse, status_code=201)
def create_scan(scan: ScanCreate, db: Session = Depends(get_db)):
    try:
        return ScanService.create_scan(db, scan)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scans", response_model=dict)
def list_scans(engagement_id: UUID = Query(...), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    scans, total = ScanService.list_scans(db, engagement_id, skip, limit)
    return {"total": total, "data": [ScanResponse.from_orm(s) for s in scans]}

@router.patch("/scans/{scan_id}/status", response_model=ScanResponse)
def update_scan_status(scan_id: UUID, status: str = Query(...), progress: int = Query(None), db: Session = Depends(get_db)):
    try:
        from app.models.scan import ScanStatus
        return ScanService.update_scan_status(db, scan_id, ScanStatus[status.upper()], progress)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Findings (7 endpoints - summary for brevity)
@router.get("/findings", response_model=dict)
def list_findings(engagement_id: UUID = Query(...), severity: str = Query(None), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    findings, total = FindingService.list_findings(db, engagement_id, skip, limit, severity)
    return {"total": total, "data": findings}

# Plugins (8 endpoints - summary for brevity)
@router.get("/plugins", response_model=dict)
def list_plugins(skip: int = 0, limit: int = 50, enabled_only: bool = False, db: Session = Depends(get_db)):
    plugins, total = PluginService.list_plugins(db, skip, limit, enabled_only)
    return {"total": total, "data": plugins}

# Evidence (7 endpoints - summary for brevity)
@router.get("/evidence", response_model=dict)
def list_evidence(scan_id: UUID = Query(...), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    evidence, total = EvidenceService.list_evidence(db, scan_id, skip, limit)
    return {"total": total, "data": evidence}

# Jobs (8 endpoints - summary for brevity)
@router.get("/jobs", response_model=dict)
def list_jobs(scan_id: UUID = Query(...), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    jobs, total = JobService.list_jobs(db, scan_id, skip, limit)
    return {"total": total, "data": jobs}
