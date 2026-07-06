from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.asset import Asset, AssetStatus
from app.schemas.asset import AssetCreate, AssetUpdate
from app.core.exceptions import NotFoundError
from app.utils.logger import logger

class AssetService:
    @staticmethod
    def create_asset(db: Session, engagement_id: UUID, asset: AssetCreate) -> Asset:
        db_asset = Asset(
            engagement_id=engagement_id,
            name=asset.name,
            display_name=asset.display_name or asset.name,
            type=asset.type,
            environment=asset.environment,
            criticality=asset.criticality,
            owner=asset.owner,
            description=asset.description,
            tags=asset.tags,
            technology_stack=asset.technology_stack,
            operating_system=asset.operating_system,
        )
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        logger.info("asset_created", asset_id=str(db_asset.id), engagement_id=str(engagement_id))
        return db_asset

    @staticmethod
    def get_asset(db: Session, asset_id: UUID) -> Asset:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise NotFoundError(f"Asset {asset_id} not found")
        return asset

    @staticmethod
    def list_assets(db: Session, engagement_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[Asset], int]:
        query = db.query(Asset).filter(Asset.engagement_id == engagement_id)
        total = query.count()
        assets = query.offset(skip).limit(limit).all()
        return assets, total

    @staticmethod
    def update_asset(db: Session, asset_id: UUID, update: AssetUpdate) -> Asset:
        asset = AssetService.get_asset(db, asset_id)
        update_data = update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)
        db.add(asset)
        db.commit()
        db.refresh(asset)
        logger.info("asset_updated", asset_id=str(asset_id))
        return asset

    @staticmethod
    def delete_asset(db: Session, asset_id: UUID) -> None:
        asset = AssetService.get_asset(db, asset_id)
        db.delete(asset)
        db.commit()
        logger.info("asset_deleted", asset_id=str(asset_id))
