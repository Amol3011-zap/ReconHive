"""Tests for Plugin Configuration Manager"""

import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.plugin import PluginRegistration
from app.models.plugin_config import PluginConfiguration, ConfigStatus, ConfigurationHistory
from app.plugins.config_manager import PluginConfigurationManager
from app.core.exceptions import NotFoundError, ValidationError, ConflictError


@pytest.fixture
def plugin_registration(db: Session):
    """Create a test plugin registration"""
    plugin = PluginRegistration(
        name="test_plugin",
        version="1.0.0",
        type="scanner",
        plugin_class_path="tests.dummy_plugin.TestPlugin",
        config_schema={
            "type": "object",
            "properties": {
                "timeout": {"type": "integer", "minimum": 1},
                "retries": {"type": "integer", "minimum": 0},
            },
            "required": ["timeout"],
        },
    )
    db.add(plugin)
    db.commit()
    db.refresh(plugin)
    return plugin


class TestCreateConfiguration:
    def test_create_configuration_success(self, db: Session, plugin_registration):
        """Test successful configuration creation"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="default",
            settings={"timeout": 30, "retries": 3},
            description="Default scanner config",
            created_by="test_user",
        )

        assert config.id is not None
        assert config.name == "default"
        assert config.settings == {"timeout": 30, "retries": 3}
        assert config.status == ConfigStatus.DRAFT
        assert config.created_by == "test_user"

    def test_create_configuration_with_defaults(self, db: Session, plugin_registration):
        """Test configuration with minimal settings"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="minimal",
            settings={},
        )

        assert config.settings == {}
        assert config.is_default is False
        assert config.is_validated is False

    def test_create_duplicate_configuration_fails(self, db: Session, plugin_registration):
        """Test that duplicate config names fail"""
        PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="unique",
            settings={"timeout": 60},
        )

        with pytest.raises(ConflictError):
            PluginConfigurationManager.create_configuration(
                db=db,
                plugin_id=plugin_registration.id,
                name="unique",
                settings={"timeout": 120},
            )

    def test_create_configuration_invalid_plugin(self, db: Session):
        """Test creation with invalid plugin ID"""
        with pytest.raises(NotFoundError):
            PluginConfigurationManager.create_configuration(
                db=db,
                plugin_id=uuid4(),
                name="test",
                settings={},
            )


class TestValidateConfiguration:
    def test_validate_valid_configuration(self, db: Session, plugin_registration):
        """Test validation of valid configuration"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="valid",
            settings={"timeout": 30, "retries": 3},
        )

        is_valid, errors = PluginConfigurationManager.validate_configuration(db, config.id)

        assert is_valid is True
        assert len(errors) == 0
        assert config.is_validated is True

    def test_validate_invalid_configuration(self, db: Session, plugin_registration):
        """Test validation of invalid configuration"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="invalid",
            settings={"timeout": -1},  # negative timeout
        )

        is_valid, errors = PluginConfigurationManager.validate_configuration(db, config.id)

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_missing_required_field(self, db: Session, plugin_registration):
        """Test validation with missing required field"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="missing_required",
            settings={"retries": 3},  # missing required 'timeout'
        )

        is_valid, errors = PluginConfigurationManager.validate_configuration(db, config.id)

        assert is_valid is False
        assert len(errors) > 0


class TestActivateConfiguration:
    def test_activate_valid_configuration(self, db: Session, plugin_registration):
        """Test activating a valid configuration"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="to_activate",
            settings={"timeout": 60},
        )

        activated = PluginConfigurationManager.activate_configuration(
            db=db,
            config_id=config.id,
            activated_by="admin",
        )

        assert activated.status == ConfigStatus.ACTIVE
        assert activated.is_default is True
        assert activated.activated_at is not None

    def test_activate_invalid_configuration_fails(self, db: Session, plugin_registration):
        """Test that activating invalid config fails"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="invalid_activate",
            settings={"timeout": -1},
        )

        with pytest.raises(ValidationError):
            PluginConfigurationManager.activate_configuration(db, config.id)

    def test_activate_replaces_previous_default(self, db: Session, plugin_registration):
        """Test that activating a new config replaces previous default"""
        config1 = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="first",
            settings={"timeout": 30},
        )
        config2 = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="second",
            settings={"timeout": 60},
        )

        PluginConfigurationManager.activate_configuration(db, config1.id)
        PluginConfigurationManager.activate_configuration(db, config2.id)

        # Refresh config1
        db.refresh(config1)

        assert config2.is_default is True
        assert config1.is_default is False


class TestUpdateConfiguration:
    def test_update_configuration_settings(self, db: Session, plugin_registration):
        """Test updating configuration settings"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="to_update",
            settings={"timeout": 30},
        )

        updated = PluginConfigurationManager.update_configuration(
            db=db,
            config_id=config.id,
            settings={"timeout": 60, "retries": 5},
            updated_by="admin",
            reason="Performance tuning",
        )

        assert updated.settings == {"timeout": 60, "retries": 5}
        assert updated.is_validated is False  # Reset after update

    def test_update_creates_history_entry(self, db: Session, plugin_registration):
        """Test that updates create history entries"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="history_test",
            settings={"timeout": 30},
        )

        PluginConfigurationManager.update_configuration(
            db=db,
            config_id=config.id,
            settings={"timeout": 60},
            updated_by="admin",
            reason="Test update",
        )

        history = db.query(ConfigurationHistory).filter(
            ConfigurationHistory.config_id == config.id
        ).all()

        assert len(history) >= 1
        assert history[-1].action == "updated"
        assert history[-1].changed_by == "admin"


class TestGetActiveConfiguration:
    def test_get_active_configuration(self, db: Session, plugin_registration):
        """Test retrieving active configuration"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="active_config",
            settings={"timeout": 30},
        )
        PluginConfigurationManager.activate_configuration(db, config.id)

        active = PluginConfigurationManager.get_active_configuration(
            db=db,
            plugin_id=plugin_registration.id,
        )

        assert active is not None
        assert active.id == config.id
        assert active.is_default is True

    def test_get_active_when_none_exists(self, db: Session, plugin_registration):
        """Test getting active config when none exists"""
        active = PluginConfigurationManager.get_active_configuration(
            db=db,
            plugin_id=plugin_registration.id,
        )

        assert active is None


class TestConfigurationHistory:
    def test_get_configuration_history(self, db: Session, plugin_registration):
        """Test retrieving configuration history"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="history_config",
            settings={"timeout": 30},
        )

        PluginConfigurationManager.update_configuration(
            db=db,
            config_id=config.id,
            settings={"timeout": 60},
            updated_by="admin",
        )

        history, total = PluginConfigurationManager.get_configuration_history(
            db=db,
            config_id=config.id,
        )

        assert total >= 1
        assert len(history) >= 1


class TestDeleteConfiguration:
    def test_delete_configuration(self, db: Session, plugin_registration):
        """Test archiving (soft delete) a configuration"""
        config = PluginConfigurationManager.create_configuration(
            db=db,
            plugin_id=plugin_registration.id,
            name="to_delete",
            settings={"timeout": 30},
        )

        PluginConfigurationManager.delete_configuration(db, config.id, deleted_by="admin")

        # Refresh to get updated status
        db.refresh(config)

        assert config.status == ConfigStatus.ARCHIVED
        assert config.is_default is False
