from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.finding import Finding, FindingStatus, Severity
from app.core.exceptions import NotFoundError
from app.utils.logger import logger

class FindingService:
    @staticmethod
    def create_finding(db: Session, engagement_id: UUID, title: str, severity: Severity,
                      description: str = None, asset_id: UUID = None, scan_id: UUID = None) -> Finding:
        db_finding = Finding(
            engagement_id=engagement_id,
            asset_id=asset_id,
            scan_id=scan_id,
            title=title,
            description=description,
            severity=severity,
            status=FindingStatus.OPEN,
        )
        db.add(db_finding)
        db.commit()
        db.refresh(db_finding)
        logger.info("finding_created", finding_id=str(db_finding.id), severity=severity.value)
        return db_finding

    @staticmethod
    def get_finding(db: Session, finding_id: UUID) -> Finding:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise NotFoundError(f"Finding {finding_id} not found")
        return finding

    @staticmethod
    def list_findings(db: Session, engagement_id: UUID, skip: int = 0, limit: int = 50,
                     severity_filter: str = None, status_filter: str = None) -> Tuple[List[Finding], int]:
        query = db.query(Finding).filter(Finding.engagement_id == engagement_id)
        if severity_filter:
            query = query.filter(Finding.severity == severity_filter)
        if status_filter:
            query = query.filter(Finding.status == status_filter)
        total = query.count()
        findings = query.order_by(Finding.created_at.desc()).offset(skip).limit(limit).all()
        return findings, total

    @staticmethod
    def update_finding_status(db: Session, finding_id: UUID, status: FindingStatus) -> Finding:
        finding = FindingService.get_finding(db, finding_id)
        finding.status = status
        db.add(finding)
        db.commit()
        db.refresh(finding)
        logger.info("finding_status_updated", finding_id=str(finding_id), status=status.value)
        return finding

    @staticmethod
    def add_remediation(db: Session, finding_id: UUID, remediation: str) -> Finding:
        finding = FindingService.get_finding(db, finding_id)
        finding.remediation = remediation
        db.add(finding)
        db.commit()
        db.refresh(finding)
        logger.info("remediation_added", finding_id=str(finding_id))
        return finding

    @staticmethod
    def get_findings_by_severity(db: Session, engagement_id: UUID, severity: Severity) -> List[Finding]:
        findings = db.query(Finding).filter(
            Finding.engagement_id == engagement_id,
            Finding.severity == severity
        ).all()
        return findings

    @staticmethod
    def get_open_findings(db: Session, engagement_id: UUID) -> List[Finding]:
        findings = db.query(Finding).filter(
            Finding.engagement_id == engagement_id,
            Finding.status == FindingStatus.OPEN
        ).all()
        return findings
