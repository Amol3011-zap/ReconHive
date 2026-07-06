from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.engagement import Engagement, EngagementStatus
from app.schemas.engagement import EngagementCreate, EngagementUpdate
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.logger import logger

class EngagementService:
    @staticmethod
    def create_engagement(db: Session, engagement: EngagementCreate) -> Engagement:
        existing = db.query(Engagement).filter(Engagement.name == engagement.name).first()
        if existing:
            raise ConflictError(f"Engagement '{engagement.name}' already exists")

        db_engagement = Engagement(
            name=engagement.name,
            description=engagement.description,
            type=engagement.type,
            status=EngagementStatus.PLANNING,
            client=engagement.client,
            scope=engagement.scope,
            owner=engagement.owner,
            team_members=engagement.team_members,
            start_date=engagement.start_date,
            end_date=engagement.end_date,
            due_date=engagement.due_date,
        )
        db.add(db_engagement)
        db.commit()
        db.refresh(db_engagement)
        logger.info("engagement_created", engagement_id=str(db_engagement.id), name=engagement.name)
        return db_engagement

    @staticmethod
    def get_engagement(db: Session, engagement_id: UUID) -> Engagement:
        engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
        if not engagement:
            raise NotFoundError(f"Engagement {engagement_id} not found")
        return engagement

    @staticmethod
    def list_engagements(db: Session, skip: int = 0, limit: int = 50, active_only: bool = False) -> Tuple[List[Engagement], int]:
        query = db.query(Engagement)
        if active_only:
            query = query.filter(Engagement.is_active == True)
        total = query.count()
        engagements = query.order_by(Engagement.created_at.desc()).offset(skip).limit(limit).all()
        return engagements, total

    @staticmethod
    def update_engagement(db: Session, engagement_id: UUID, update: EngagementUpdate) -> Engagement:
        engagement = EngagementService.get_engagement(db, engagement_id)
        update_data = update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(engagement, field, value)
        db.add(engagement)
        db.commit()
        db.refresh(engagement)
        logger.info("engagement_updated", engagement_id=str(engagement_id), fields=list(update_data.keys()))
        return engagement

    @staticmethod
    def delete_engagement(db: Session, engagement_id: UUID) -> None:
        engagement = EngagementService.get_engagement(db, engagement_id)
        db.delete(engagement)
        db.commit()
        logger.info("engagement_deleted", engagement_id=str(engagement_id), name=engagement.name)

    @staticmethod
    def get_engagement_summary(db: Session, engagement_id: UUID) -> dict:
        engagement = EngagementService.get_engagement(db, engagement_id)
        assets_count = len(engagement.assets) if engagement.assets else 0
        targets_count = len(engagement.targets) if engagement.targets else 0
        scans_count = len(engagement.scans) if engagement.scans else 0
        findings_count = len(engagement.findings) if engagement.findings else 0
        return {
            "id": engagement.id,
            "name": engagement.name,
            "type": engagement.type.value,
            "status": engagement.status.value,
            "assets": assets_count,
            "targets": targets_count,
            "scans": scans_count,
            "findings": findings_count,
            "client": engagement.client,
            "owner": engagement.owner,
        }
