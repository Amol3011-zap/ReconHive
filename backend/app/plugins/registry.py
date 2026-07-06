from typing import Dict, List, Optional, Type
from dataclasses import dataclass
from app.plugins.base import BasePlugin, PluginType, PluginMetadata
from app.utils.logger import logger


@dataclass
class PluginVersion:
    """Plugin version information."""
    version: str
    compatible_with: List[str]  # List of compatible ReconHive versions
    released_at: str
    deprecated: bool = False


class PluginRegistry:
    """Central registry for all available plugins."""

    def __init__(self):
        self.registry: Dict[str, Dict] = {}
        self.versions: Dict[str, List[PluginVersion]] = {}

    def register(self, plugin_id: str, plugin_class: Type[BasePlugin],
                version: str = "1.0.0", metadata: Optional[PluginMetadata] = None) -> bool:
        """Register a new plugin in the registry."""
        try:
            if plugin_id in self.registry:
                logger.warning("plugin_already_registered", plugin_id=plugin_id)
                return False

            plugin_instance = plugin_class()
            plugin_meta = metadata or plugin_instance.get_metadata()

            self.registry[plugin_id] = {
                "id": plugin_id,
                "class": plugin_class,
                "metadata": plugin_meta,
                "version": version,
                "status": "active",
                "registered_at": str(__import__('datetime').datetime.utcnow()),
            }

            if plugin_id not in self.versions:
                self.versions[plugin_id] = []

            self.versions[plugin_id].append(PluginVersion(
                version=version,
                compatible_with=["4.0.0"],
                released_at=str(__import__('datetime').datetime.utcnow()),
                deprecated=False
            ))

            logger.info("plugin_registered", plugin_id=plugin_id, version=version)
            return True

        except Exception as e:
            logger.error("plugin_registration_failed", plugin_id=plugin_id, error=str(e))
            return False

    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin."""
        if plugin_id not in self.registry:
            return False

        try:
            del self.registry[plugin_id]
            logger.info("plugin_unregistered", plugin_id=plugin_id)
            return True
        except Exception as e:
            logger.error("plugin_unregistration_failed", plugin_id=plugin_id, error=str(e))
            return False

    def get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Get plugin information."""
        return self.registry.get(plugin_id)

    def get_plugin_class(self, plugin_id: str) -> Optional[Type[BasePlugin]]:
        """Get plugin class."""
        plugin = self.registry.get(plugin_id)
        return plugin["class"] if plugin else None

    def list_plugins(self, plugin_type: Optional[PluginType] = None) -> List[Dict]:
        """List all registered plugins, optionally filtered by type."""
        plugins = []
        for plugin_id, plugin_info in self.registry.items():
            if plugin_type and plugin_info["metadata"].plugin_type != plugin_type:
                continue
            plugins.append({
                "id": plugin_id,
                "name": plugin_info["metadata"].name,
                "version": plugin_info["version"],
                "type": plugin_info["metadata"].plugin_type.value,
                "status": plugin_info["status"],
                "author": plugin_info["metadata"].author,
            })
        return plugins

    def get_versions(self, plugin_id: str) -> List[PluginVersion]:
        """Get all versions of a plugin."""
        return self.versions.get(plugin_id, [])

    def get_latest_version(self, plugin_id: str) -> Optional[str]:
        """Get latest version of a plugin."""
        versions = self.versions.get(plugin_id, [])
        if not versions:
            return None
        # Filter out deprecated versions
        active = [v for v in versions if not v.deprecated]
        return active[-1].version if active else None

    def is_compatible(self, plugin_id: str, version: str, reconhive_version: str = "4.0.0") -> bool:
        """Check if plugin version is compatible."""
        versions = self.versions.get(plugin_id, [])
        for v in versions:
            if v.version == version:
                return reconhive_version in v.compatible_with
        return False

    def deprecate_version(self, plugin_id: str, version: str) -> bool:
        """Mark a plugin version as deprecated."""
        versions = self.versions.get(plugin_id, [])
        for v in versions:
            if v.version == version:
                v.deprecated = True
                logger.info("plugin_version_deprecated", plugin_id=plugin_id, version=version)
                return True
        return False


# Global plugin registry instance
plugin_registry = PluginRegistry()
