from typing import Dict, Optional, Any, Type
from uuid import UUID
from sqlalchemy.orm import Session
from app.plugins.registry import plugin_registry
from app.plugins.base import BasePlugin, PluginStatus
from app.plugins.config_manager import PluginConfigurationManager
from app.utils.logger import logger
import importlib


class PluginLoader:
    """Dynamic plugin loader and lifecycle manager."""

    def __init__(self):
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

    def discover_and_register(self, module_path: str) -> bool:
        """Discover and register plugins from a module."""
        try:
            module = importlib.import_module(module_path)
            for item_name in dir(module):
                item = getattr(module, item_name)
                if isinstance(item, type) and issubclass(item, BasePlugin) and item != BasePlugin:
                    instance = item()
                    metadata = instance.get_metadata()
                    plugin_registry.register(metadata.name, item, metadata=metadata)
                    logger.info("plugin_discovered", plugin_id=metadata.name, module=module_path)
            return True
        except Exception as e:
            logger.error("plugin_discovery_failed", module=module_path, error=str(e))
            return False

    def load(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Load a plugin by ID."""
        if plugin_id in self.loaded_plugins:
            logger.warning("plugin_already_loaded", plugin_id=plugin_id)
            return True

        try:
            plugin_class = plugin_registry.get_plugin_class(plugin_id)
            if not plugin_class:
                raise ValueError(f"Plugin {plugin_id} not found in registry")

            plugin = plugin_class()
            config = config or {}

            if not plugin.validate_config(config):
                raise ValueError("Invalid plugin configuration")

            plugin.initialize(config)
            self.loaded_plugins[plugin_id] = plugin
            self.plugin_configs[plugin_id] = config

            logger.info("plugin_loaded", plugin_id=plugin_id)
            return True

        except Exception as e:
            logger.error("plugin_load_failed", plugin_id=plugin_id, error=str(e))
            return False

    def unload(self, plugin_id: str) -> bool:
        """Unload a plugin."""
        if plugin_id not in self.loaded_plugins:
            return False

        try:
            plugin = self.loaded_plugins[plugin_id]
            plugin.cleanup()
            del self.loaded_plugins[plugin_id]
            del self.plugin_configs[plugin_id]
            logger.info("plugin_unloaded", plugin_id=plugin_id)
            return True
        except Exception as e:
            logger.error("plugin_unload_failed", plugin_id=plugin_id, error=str(e))
            return False

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get a loaded plugin instance."""
        return self.loaded_plugins.get(plugin_id)

    def execute(self, plugin_id: str, input_data: Any) -> Optional[Any]:
        """Execute a plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            logger.error("plugin_not_loaded", plugin_id=plugin_id)
            return None

        if plugin.health_check() != PluginStatus.HEALTHY:
            logger.error("plugin_unhealthy", plugin_id=plugin_id)
            return None

        try:
            result = plugin.execute(input_data)
            logger.info("plugin_executed", plugin_id=plugin_id)
            return result
        except Exception as e:
            logger.error("plugin_execution_failed", plugin_id=plugin_id, error=str(e))
            return None

    def health_check(self, plugin_id: str) -> PluginStatus:
        """Check plugin health."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return PluginStatus.UNAVAILABLE
        return plugin.health_check()

    def list_loaded(self) -> list:
        """List all loaded plugins."""
        plugins = []
        for plugin_id, plugin in self.loaded_plugins.items():
            metadata = plugin.get_metadata()
            plugins.append({
                "id": plugin_id,
                "name": metadata.name,
                "version": metadata.version,
                "type": metadata.plugin_type.value,
                "status": self.health_check(plugin_id).value,
            })
        return plugins

    def reload(self, plugin_id: str) -> bool:
        """Reload a plugin."""
        config = self.plugin_configs.get(plugin_id, {})
        if not self.unload(plugin_id):
            return False
        return self.load(plugin_id, config)

    def load_with_configuration(
        self,
        db: Session,
        plugin_id: str,
        config_id: Optional[UUID] = None,
    ) -> bool:
        """Load a plugin with its configuration from database.

        If config_id is provided, loads that specific configuration.
        Otherwise, loads the default (active) configuration.
        """
        try:
            # Get plugin registration
            from app.models.plugin import PluginRegistration
            plugin_reg = db.query(PluginRegistration).filter(
                PluginRegistration.name == plugin_id
            ).first()

            if not plugin_reg:
                logger.error("plugin_not_found_in_db", plugin_id=plugin_id)
                return False

            # Get configuration
            if config_id:
                config = PluginConfigurationManager.get_configuration(db, config_id)
            else:
                config = PluginConfigurationManager.get_active_configuration(db, plugin_reg.id)

            if not config:
                logger.warning("no_configuration_found", plugin_id=plugin_id)
                config_settings = {}
            else:
                config_settings = config.settings or {}
                # Track usage
                PluginConfigurationManager.track_configuration_usage(db, config.id)

            # Load plugin with settings
            return self.load(plugin_id, config_settings)

        except Exception as e:
            logger.error(
                "load_with_configuration_failed",
                plugin_id=plugin_id,
                config_id=str(config_id) if config_id else None,
                error=str(e),
            )
            return False

    def get_plugin_configurations(
        self,
        db: Session,
        plugin_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get all configurations for a plugin from database"""
        try:
            from app.models.plugin import PluginRegistration
            plugin_reg = db.query(PluginRegistration).filter(
                PluginRegistration.name == plugin_id
            ).first()

            if not plugin_reg:
                return None

            configs, _ = PluginConfigurationManager.list_configurations(
                db,
                plugin_reg.id,
                skip=0,
                limit=100,
            )

            return {
                config.name: {
                    "id": str(config.id),
                    "settings": config.settings,
                    "is_default": config.is_default,
                    "status": config.status.value,
                }
                for config in configs
            }

        except Exception as e:
            logger.error("get_configurations_failed", plugin_id=plugin_id, error=str(e))
            return None


# Global plugin loader instance
plugin_loader = PluginLoader()
