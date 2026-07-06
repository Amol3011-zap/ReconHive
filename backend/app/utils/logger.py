import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def _format_log(self, event: str, level: str, **kwargs) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "level": level,
            **kwargs
        }
        return json.dumps(log_entry)

    def info(self, event: str, **kwargs):
        self.logger.info(self._format_log(event, "INFO", **kwargs))

    def error(self, event: str, **kwargs):
        self.logger.error(self._format_log(event, "ERROR", **kwargs))

    def warning(self, event: str, **kwargs):
        self.logger.warning(self._format_log(event, "WARNING", **kwargs))

    def debug(self, event: str, **kwargs):
        self.logger.debug(self._format_log(event, "DEBUG", **kwargs))

logger = StructuredLogger("reconhive")
