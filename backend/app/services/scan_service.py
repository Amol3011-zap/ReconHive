from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.scan import Scan, ScanStatus
from app.schemas.scan import ScanCreate
from app.core.exceptions import NotFoundError
from app.utils.logger import logger
from datetime import datetime

class ScanService:
    @staticmethod
    def create_scan(db: Session, scan: ScanCreate) -> Scan:
        db_scan = Scan(
            engagement_id=scan.engagement_id,
            asset_id=scan.asset_id,
            name=scan.name,
            plugin_names=scan.plugin_names,
            configuration=scan.configuration,
            status=ScanStatus.QUEUED,
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        logger.info("scan_created", scan_id=str(db_scan.id), plugins=len(scan.plugin_names or []))
        return db_scan

    @staticmethod
    def get_scan(db: Session, scan_id: UUID) -> Scan:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise NotFoundError(f"Scan {scan_id} not found")
        return scan

    @staticmethod
    def list_scans(db: Session, engagement_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[Scan], int]:
        query = db.query(Scan).filter(Scan.engagement_id == engagement_id)
        total = query.count()
        scans = query.order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()
        return scans, total

    @staticmethod
    def update_scan_status(db: Session, scan_id: UUID, status: ScanStatus, progress: int = None) -> Scan:
        scan = ScanService.get_scan(db, scan_id)
        scan.status = status
        if progress is not None:
            scan.progress_percent = min(100, max(0, progress))
        if status == ScanStatus.RUNNING and not scan.started_at:
            scan.started_at = datetime.utcnow()
        elif status == ScanStatus.COMPLETED and not scan.completed_at:
            scan.completed_at = datetime.utcnow()
            if scan.started_at:
                scan.duration_seconds = int((scan.completed_at - scan.started_at).total_seconds())
        db.add(scan)
        db.commit()
        db.refresh(scan)
        logger.info("scan_status_updated", scan_id=str(scan_id), status=status.value)
        return scan

    @staticmethod
    def pause_scan(db: Session, scan_id: UUID) -> Scan:
        scan = ScanService.get_scan(db, scan_id)
        scan.status = ScanStatus.PAUSED
        db.add(scan)
        db.commit()
        db.refresh(scan)
        logger.info("scan_paused", scan_id=str(scan_id))
        return scan

    @staticmethod
    def resume_scan(db: Session, scan_id: UUID) -> Scan:
        scan = ScanService.get_scan(db, scan_id)
        if scan.status == ScanStatus.PAUSED:
            scan.status = ScanStatus.RUNNING
        db.add(scan)
        db.commit()
        db.refresh(scan)
        logger.info("scan_resumed", scan_id=str(scan_id))
        return scan

    @staticmethod
    def cancel_scan(db: Session, scan_id: UUID) -> Scan:
        scan = ScanService.get_scan(db, scan_id)
        scan.status = ScanStatus.CANCELLED
        db.add(scan)
        db.commit()
        db.refresh(scan)
        logger.info("scan_cancelled", scan_id=str(scan_id))
        return scan
