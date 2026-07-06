from typing import Dict, Optional, List
from uuid import UUID
from app.plugins.base import BasePlugin, PluginStatus, PluginMetadata
from app.utils.logger import logger
from importlib import import_module


class PluginManager:
    """Manage plugin lifecycle and execution."""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs: Dict[str, Dict] = {}

    def load_plugin(self, plugin_class_path: str, plugin_id: str, config: Dict) -> bool:
        """Load a plugin from a module path."""
        try:
            module_path, class_name = plugin_class_path.rsplit(".", 1)
            module = import_module(module_path)
            plugin_class = getattr(module, class_name)
            plugin = plugin_class()

            if not plugin.validate_config(config):
                raise ValueError("Invalid plugin configuration")

            plugin.initialize(config)
            self.plugins[plugin_id] = plugin
            self.plugin_configs[plugin_id] = config

            logger.info("plugin_loaded", plugin_id=plugin_id, metadata=plugin.get_metadata().name)
            return True
        except Exception as e:
            logger.error("plugin_load_failed", plugin_id=plugin_id, error=str(e))
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin and cleanup resources."""
        if plugin_id not in self.plugins:
            return False

        try:
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            del self.plugins[plugin_id]
            del self.plugin_configs[plugin_id]
            logger.info("plugin_unloaded", plugin_id=plugin_id)
            return True
        except Exception as e:
            logger.error("plugin_unload_failed", plugin_id=plugin_id, error=str(e))
            return False

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get a loaded plugin."""
        return self.plugins.get(plugin_id)

    def execute_plugin(self, plugin_id: str, input_data: any) -> any:
        """Execute a plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            raise ValueError(f"Plugin {plugin_id} not found")

        if plugin.health_check() != PluginStatus.HEALTHY:
            raise RuntimeError(f"Plugin {plugin_id} is not healthy")

        try:
            result = plugin.execute(input_data)
            logger.info("plugin_executed", plugin_id=plugin_id)
            return result
        except Exception as e:
            logger.error("plugin_execution_failed", plugin_id=plugin_id, error=str(e))
            raise

    def get_plugin_health(self, plugin_id: str) -> PluginStatus:
        """Get plugin health status."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return PluginStatus.UNAVAILABLE
        return plugin.health_check()

    def list_plugins(self) -> List[Dict]:
        """List all loaded plugins."""
        plugins_list = []
        for plugin_id, plugin in self.plugins.items():
            metadata = plugin.get_metadata()
            plugins_list.append({
                "id": plugin_id,
                "name": metadata.name,
                "version": metadata.version,
                "type": metadata.plugin_type.value,
                "status": self.get_plugin_health(plugin_id).value,
            })
        return plugins_list


# Global plugin manager instance
plugin_manager = PluginManager()
