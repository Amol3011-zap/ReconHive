from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from jsonschema import validate, ValidationError as JSONValidationError
from app.models.plugin import PluginRegistration
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.logger import logger

class PluginService:
    @staticmethod
    def register_plugin(db: Session, name: str, version: str, plugin_type: str,
                       plugin_class_path: str, config_schema: dict = None,
                       description: str = None) -> PluginRegistration:
        existing = db.query(PluginRegistration).filter(PluginRegistration.name == name).first()
        if existing:
            raise ConflictError(f"Plugin {name} already registered")

        db_plugin = PluginRegistration(
            name=name,
            version=version,
            type=plugin_type,
            plugin_class_path=plugin_class_path,
            config_schema=config_schema or {},
            description=description,
            enabled=True,
        )
        db.add(db_plugin)
        db.commit()
        db.refresh(db_plugin)
        logger.info("plugin_registered", plugin_id=str(db_plugin.id), name=name, version=version)
        return db_plugin

    @staticmethod
    def get_plugin(db: Session, plugin_id: UUID) -> PluginRegistration:
        plugin = db.query(PluginRegistration).filter(PluginRegistration.id == plugin_id).first()
        if not plugin:
            raise NotFoundError(f"Plugin {plugin_id} not found")
        return plugin

    @staticmethod
    def get_plugin_by_name(db: Session, name: str) -> PluginRegistration:
        plugin = db.query(PluginRegistration).filter(PluginRegistration.name == name).first()
        if not plugin:
            raise NotFoundError(f"Plugin {name} not found")
        return plugin

    @staticmethod
    def list_plugins(db: Session, skip: int = 0, limit: int = 50, enabled_only: bool = False) -> Tuple[List[PluginRegistration], int]:
        query = db.query(PluginRegistration)
        if enabled_only:
            query = query.filter(PluginRegistration.enabled == True)
        total = query.count()
        plugins = query.offset(skip).limit(limit).all()
        return plugins, total

    @staticmethod
    def list_plugins_by_type(db: Session, plugin_type: str) -> List[PluginRegistration]:
        plugins = db.query(PluginRegistration).filter(
            PluginRegistration.type == plugin_type,
            PluginRegistration.enabled == True
        ).all()
        return plugins

    @staticmethod
    def enable_plugin(db: Session, plugin_id: UUID) -> PluginRegistration:
        plugin = PluginService.get_plugin(db, plugin_id)
        plugin.enabled = True
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        logger.info("plugin_enabled", plugin_id=str(plugin_id), name=plugin.name)
        return plugin

    @staticmethod
    def disable_plugin(db: Session, plugin_id: UUID) -> PluginRegistration:
        plugin = PluginService.get_plugin(db, plugin_id)
        plugin.enabled = False
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        logger.info("plugin_disabled", plugin_id=str(plugin_id), name=plugin.name)
        return plugin

    @staticmethod
    def validate_config(db: Session, plugin_name: str, config: dict) -> bool:
        plugin = PluginService.get_plugin_by_name(db, plugin_name)
        if not plugin.config_schema:
            return True
        try:
            validate(instance=config, schema=plugin.config_schema)
            return True
        except JSONValidationError as e:
            raise ValidationError(f"Config validation failed: {e.message}")
