from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.engagement import Engagement, EngagementStatus
from app.schemas.engagement import EngagementCreate, EngagementUpdate
from app.services.base import BaseService
from app.core.exceptions import ConflictError
from app.utils.logger import logger


class EngagementService(BaseService[Engagement]):
    """Service for engagement management with CRUD operations."""

    def __init__(self):
        super().__init__(Engagement)

    def create_engagement(self, db: Session, engagement: EngagementCreate) -> Engagement:
        """Create new engagement with uniqueness check."""
        existing = db.query(Engagement).filter(Engagement.name == engagement.name).first()
        if existing:
            raise ConflictError(f"Engagement '{engagement.name}' already exists")

        return self.create(
            db,
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

    def get_engagement(self, db: Session, engagement_id: UUID) -> Engagement:
        """Get engagement by ID."""
        return self.get_by_id(db, engagement_id)

    def list_engagements(
        self, db: Session, skip: int = 0, limit: int = 50, active_only: bool = False
    ) -> Tuple[List[Engagement], int]:
        """List engagements with optional filtering."""
        filters = {"is_active": True} if active_only else None
        query = db.query(Engagement)

        if active_only:
            query = query.filter(Engagement.is_active == True)

        total = query.count()
        engagements = (
            query.order_by(Engagement.created_at.desc()).offset(skip).limit(limit).all()
        )
        return engagements, total

    def update_engagement(self, db: Session, engagement_id: UUID, update: EngagementUpdate) -> Engagement:
        """Update engagement."""
        update_data = update.dict(exclude_unset=True)
        return self.update(db, engagement_id, **update_data)

    def delete_engagement(self, db: Session, engagement_id: UUID) -> None:
        """Delete engagement."""
        self.delete(db, engagement_id)

    def get_engagement_summary(self, db: Session, engagement_id: UUID) -> dict:
        """Get engagement summary with related counts."""
        from sqlalchemy.orm import joinedload

        engagement = (
            db.query(Engagement)
            .options(
                joinedload(Engagement.assets),
                joinedload(Engagement.targets),
                joinedload(Engagement.scans),
                joinedload(Engagement.findings),
            )
            .filter(Engagement.id == engagement_id)
            .first()
        )

        if not engagement:
            raise Exception(f"Engagement {engagement_id} not found")

        return {
            "id": engagement.id,
            "name": engagement.name,
            "type": engagement.type.value,
            "status": engagement.status.value,
            "assets": len(engagement.assets) if engagement.assets else 0,
            "targets": len(engagement.targets) if engagement.targets else 0,
            "scans": len(engagement.scans) if engagement.scans else 0,
            "findings": len(engagement.findings) if engagement.findings else 0,
            "client": engagement.client,
            "owner": engagement.owner,
        }


# Global service instance
engagement_service = EngagementService()
