"""Plugin Configuration Management System"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from jsonschema import validate, ValidationError as JSONValidationError

from app.models.plugin import PluginRegistration
from app.models.plugin_config import PluginConfiguration, ConfigurationHistory, ConfigStatus
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.utils.logger import logger


class PluginConfigurationManager:
    """Manages plugin configurations with validation, versioning, and audit trail"""

    @staticmethod
    def create_configuration(
        db: Session,
        plugin_id: UUID,
        name: str,
        settings: Dict,
        description: str = None,
        created_by: str = None,
        is_default: bool = False,
    ) -> PluginConfiguration:
        """Create a new configuration for a plugin"""

        # Verify plugin exists
        plugin = db.query(PluginRegistration).filter(PluginRegistration.id == plugin_id).first()
        if not plugin:
            raise NotFoundError(f"Plugin {plugin_id} not found")

        # Check for duplicate names
        existing = db.query(PluginConfiguration).filter(
            PluginConfiguration.plugin_id == plugin_id,
            PluginConfiguration.name == name,
            PluginConfiguration.status != ConfigStatus.ARCHIVED,
        ).first()
        if existing:
            raise ConflictError(f"Configuration '{name}' already exists for this plugin")

        # Create configuration
        config = PluginConfiguration(
            plugin_id=plugin_id,
            name=name,
            description=description,
            settings=settings or {},
            created_by=created_by,
            is_default=is_default,
            status=ConfigStatus.DRAFT,
        )

        db.add(config)
        db.commit()
        db.refresh(config)

        logger.info(
            "config_created",
            config_id=str(config.id),
            plugin_id=str(plugin_id),
            name=name,
        )

        return config

    @staticmethod
    def validate_configuration(
        db: Session,
        config_id: UUID,
    ) -> Tuple[bool, List[str]]:
        """Validate configuration against plugin's config_schema"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if not config:
            raise NotFoundError(f"Configuration {config_id} not found")

        plugin = db.query(PluginRegistration).filter(PluginRegistration.id == config.plugin_id).first()
        if not plugin:
            raise NotFoundError(f"Plugin {config.plugin_id} not found")

        # If no schema defined, consider valid
        if not plugin.config_schema:
            config.is_validated = True
            config.validation_errors = []
            db.add(config)
            db.commit()
            return True, []

        # Validate against schema
        errors = []
        try:
            validate(instance=config.settings, schema=plugin.config_schema)
            config.is_validated = True
            config.validation_errors = []
        except JSONValidationError as e:
            config.is_validated = False
            errors = [str(e)]
            config.validation_errors = errors

        db.add(config)
        db.commit()

        logger.info(
            "config_validated",
            config_id=str(config_id),
            is_valid=config.is_validated,
            errors_count=len(errors),
        )

        return config.is_validated, errors

    @staticmethod
    def activate_configuration(
        db: Session,
        config_id: UUID,
        activated_by: str = None,
    ) -> PluginConfiguration:
        """Activate a configuration (make it the live config)"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if not config:
            raise NotFoundError(f"Configuration {config_id} not found")

        # Validate before activating
        is_valid, errors = PluginConfigurationManager.validate_configuration(db, config_id)
        if not is_valid:
            raise ValidationError(f"Cannot activate invalid configuration: {errors}")

        # Deactivate other default configs for this plugin
        db.query(PluginConfiguration).filter(
            PluginConfiguration.plugin_id == config.plugin_id,
            PluginConfiguration.is_default == True,
            PluginConfiguration.id != config_id,
        ).update({"is_default": False})

        # Activate this config
        config.status = ConfigStatus.ACTIVE
        config.is_default = True
        config.activated_at = datetime.utcnow()

        # Record history
        history = ConfigurationHistory(
            config_id=config_id,
            action="activated",
            changed_by=activated_by,
            new_settings=config.settings,
            reason="Configuration activated for use",
        )

        db.add(config)
        db.add(history)
        db.commit()
        db.refresh(config)

        logger.info(
            "config_activated",
            config_id=str(config_id),
            activated_by=activated_by,
        )

        return config

    @staticmethod
    def update_configuration(
        db: Session,
        config_id: UUID,
        settings: Dict = None,
        env_vars: Dict = None,
        description: str = None,
        updated_by: str = None,
        reason: str = None,
    ) -> PluginConfiguration:
        """Update configuration settings"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if not config:
            raise NotFoundError(f"Configuration {config_id} not found")

        # Store old settings for history
        old_settings = config.settings.copy() if config.settings else {}

        # Update fields
        if settings is not None:
            config.settings = settings
        if env_vars is not None:
            config.env_vars = env_vars
        if description is not None:
            config.description = description

        # Reset validation if settings changed
        if settings is not None:
            config.is_validated = False
            config.validation_errors = []

        # Record history
        history = ConfigurationHistory(
            config_id=config_id,
            action="updated",
            changed_by=updated_by,
            old_settings=old_settings,
            new_settings=config.settings,
            reason=reason,
        )

        db.add(config)
        db.add(history)
        db.commit()
        db.refresh(config)

        logger.info(
            "config_updated",
            config_id=str(config_id),
            updated_by=updated_by,
            reason=reason,
        )

        return config

    @staticmethod
    def deactivate_configuration(
        db: Session,
        config_id: UUID,
        deactivated_by: str = None,
    ) -> PluginConfiguration:
        """Deactivate a configuration"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if not config:
            raise NotFoundError(f"Configuration {config_id} not found")

        config.status = ConfigStatus.INACTIVE
        config.is_default = False

        history = ConfigurationHistory(
            config_id=config_id,
            action="deactivated",
            changed_by=deactivated_by,
            reason="Configuration deactivated",
        )

        db.add(config)
        db.add(history)
        db.commit()
        db.refresh(config)

        logger.info("config_deactivated", config_id=str(config_id), deactivated_by=deactivated_by)

        return config

    @staticmethod
    def get_active_configuration(
        db: Session,
        plugin_id: UUID,
    ) -> Optional[PluginConfiguration]:
        """Get the active (default) configuration for a plugin"""

        config = db.query(PluginConfiguration).filter(
            PluginConfiguration.plugin_id == plugin_id,
            PluginConfiguration.is_default == True,
            PluginConfiguration.status == ConfigStatus.ACTIVE,
        ).first()

        return config

    @staticmethod
    def get_configuration(
        db: Session,
        config_id: UUID,
    ) -> PluginConfiguration:
        """Get a specific configuration"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if not config:
            raise NotFoundError(f"Configuration {config_id} not found")

        return config

    @staticmethod
    def list_configurations(
        db: Session,
        plugin_id: UUID,
        status: ConfigStatus = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[PluginConfiguration], int]:
        """List configurations for a plugin"""

        query = db.query(PluginConfiguration).filter(PluginConfiguration.plugin_id == plugin_id)

        if status:
            query = query.filter(PluginConfiguration.status == status)

        total = query.count()
        configs = query.offset(skip).limit(limit).all()

        return configs, total

    @staticmethod
    def get_configuration_history(
        db: Session,
        config_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ConfigurationHistory], int]:
        """Get audit trail for a configuration"""

        query = db.query(ConfigurationHistory).filter(ConfigurationHistory.config_id == config_id)
        total = query.count()
        history = query.order_by(ConfigurationHistory.created_at.desc()).offset(skip).limit(limit).all()

        return history, total

    @staticmethod
    def delete_configuration(
        db: Session,
        config_id: UUID,
        deleted_by: str = None,
    ) -> None:
        """Archive a configuration (soft delete)"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if not config:
            raise NotFoundError(f"Configuration {config_id} not found")

        config.status = ConfigStatus.ARCHIVED
        config.is_default = False

        history = ConfigurationHistory(
            config_id=config_id,
            action="archived",
            changed_by=deleted_by,
            reason="Configuration archived",
        )

        db.add(config)
        db.add(history)
        db.commit()

        logger.info("config_archived", config_id=str(config_id), deleted_by=deleted_by)

    @staticmethod
    def track_configuration_usage(
        db: Session,
        config_id: UUID,
    ) -> None:
        """Track when a configuration is used"""

        config = db.query(PluginConfiguration).filter(PluginConfiguration.id == config_id).first()
        if config:
            config.last_used_at = datetime.utcnow()
            try:
                config.use_count = str(int(config.use_count or 0) + 1)
            except:
                config.use_count = "1"
            db.add(config)
            db.commit()
