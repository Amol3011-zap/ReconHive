from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Tuple, Optional
from uuid import UUID
from app.core.exceptions import NotFoundError
from app.utils.logger import logger

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service class with common CRUD operations."""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, entity_id: UUID) -> T:
        """Get entity by ID."""
        entity = db.query(self.model).filter(self.model.id == entity_id).first()
        if not entity:
            raise NotFoundError(f"{self.model.__name__} {entity_id} not found")
        return entity

    def list_paginated(self, db: Session, skip: int = 0, limit: int = 50,
                      filters: dict = None) -> Tuple[List[T], int]:
        """List entities with pagination."""
        query = db.query(self.model)

        if filters:
            for field, value in filters.items():
                if value is not None and hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        return entities, total

    def create(self, db: Session, **kwargs) -> T:
        """Create new entity."""
        entity = self.model(**kwargs)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        logger.info(f"{self.model.__name__.lower()}_created",
                   id=str(entity.id) if hasattr(entity, 'id') else None)
        return entity

    def update(self, db: Session, entity_id: UUID, **kwargs) -> T:
        """Update entity."""
        entity = self.get_by_id(db, entity_id)
        for field, value in kwargs.items():
            if value is not None and hasattr(entity, field):
                setattr(entity, field, value)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        logger.info(f"{self.model.__name__.lower()}_updated", id=str(entity_id))
        return entity

    def delete(self, db: Session, entity_id: UUID) -> None:
        """Delete entity."""
        entity = self.get_by_id(db, entity_id)
        db.delete(entity)
        db.commit()
        logger.info(f"{self.model.__name__.lower()}_deleted", id=str(entity_id))

    def exists(self, db: Session, entity_id: UUID) -> bool:
        """Check if entity exists."""
        return db.query(self.model).filter(self.model.id == entity_id).first() is not None
