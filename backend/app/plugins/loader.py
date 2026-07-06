from typing import Dict, Optional, Any, Type
from app.plugins.registry import plugin_registry
from app.plugins.base import BasePlugin, PluginStatus
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


# Global plugin loader instance
plugin_loader = PluginLoader()
