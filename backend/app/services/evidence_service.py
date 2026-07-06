from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.evidence import Evidence
from app.core.exceptions import NotFoundError
from app.utils.logger import logger

class EvidenceService:
    @staticmethod
    def create_evidence(db: Session, engagement_id: UUID, scan_id: UUID, name: str,
                       evidence_type: str, description: str = None, file_path: str = None,
                       data: str = None) -> Evidence:
        db_evidence = Evidence(
            engagement_id=engagement_id,
            scan_id=scan_id,
            name=name,
            type=evidence_type,
            description=description,
            file_path=file_path,
            data=data,
        )
        db.add(db_evidence)
        db.commit()
        db.refresh(db_evidence)
        logger.info("evidence_created", evidence_id=str(db_evidence.id), type=evidence_type)
        return db_evidence

    @staticmethod
    def get_evidence(db: Session, evidence_id: UUID) -> Evidence:
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        return evidence

    @staticmethod
    def list_evidence(db: Session, scan_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[Evidence], int]:
        query = db.query(Evidence).filter(Evidence.scan_id == scan_id)
        total = query.count()
        evidence = query.offset(skip).limit(limit).all()
        return evidence, total

    @staticmethod
    def delete_evidence(db: Session, evidence_id: UUID) -> None:
        evidence = EvidenceService.get_evidence(db, evidence_id)
        db.delete(evidence)
        db.commit()
        logger.info("evidence_deleted", evidence_id=str(evidence_id))

    @staticmethod
    def add_tag(db: Session, evidence_id: UUID, tag: str) -> Evidence:
        evidence = EvidenceService.get_evidence(db, evidence_id)
        if not evidence.tags:
            evidence.tags = []
        if tag not in evidence.tags:
            evidence.tags.append(tag)
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence
