from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass


class PluginType(str, Enum):
    SCANNER = "scanner"
    NORMALIZER = "normalizer"
    REPORTER = "reporter"
    ENRICHER = "enricher"
    ANALYZER = "analyzer"


class PluginStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    plugin_type: PluginType
    description: str
    author: str
    capabilities: List[str]
    config_schema: Optional[Dict[str, Any]] = None


class BasePlugin(ABC):
    """Base class for all ReconHive plugins."""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute plugin with input data."""
        pass

    @abstractmethod
    def health_check(self) -> PluginStatus:
        """Check plugin health status."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass


class ScannerPlugin(BasePlugin):
    """Base class for scanner plugins."""

    @abstractmethod
    def scan(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scan on target."""
        pass

    def execute(self, input_data: Any) -> Any:
        """Execute scanner."""
        return self.scan(input_data.get("target"), input_data.get("config", {}))


class NormalizerPlugin(BasePlugin):
    """Base class for normalizer plugins."""

    @abstractmethod
    def normalize(self, raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize raw scan results to standard format."""
        pass

    def execute(self, input_data: Any) -> Any:
        """Execute normalizer."""
        return self.normalize(input_data)


class ReporterPlugin(BasePlugin):
    """Base class for reporter plugins."""

    @abstractmethod
    def generate_report(self, findings: List[Dict[str, Any]], engagement_data: Dict[str, Any]) -> bytes:
        """Generate report from findings."""
        pass

    def execute(self, input_data: Any) -> Any:
        """Execute reporter."""
        return self.generate_report(
            input_data.get("findings", []),
            input_data.get("engagement_data", {})
        )
