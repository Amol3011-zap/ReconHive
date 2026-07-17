"""
Celery application configuration and initialization
"""

from celery import Celery, signals
from celery.result import AsyncResult
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from kombu import Exchange, Queue
from typing import Optional, Dict, Any
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Celery app initialization
celery_app = Celery("reconhive")


def init_celery(app=None):
    """Initialize Celery with Flask/FastAPI app context"""

    # Configuration
    celery_config = {
        # Broker settings
        "broker_url": os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        "broker_connection_retry_on_startup": True,
        "broker_heartbeat": 30,

        # Result backend
        "result_backend": os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
        "result_expires": 3600,  # 1 hour

        # Task settings
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,

        # Task execution
        "task_acks_late": True,
        "worker_prefetch_multiplier": 1,
        "worker_max_tasks_per_child": 1000,

        # Retry settings
        "task_autoretry_for": (Exception,),
        "task_default_retry_delay": 60,
        "task_default_max_retries": 3,

        # Queue configuration
        "task_default_queue": "default",
        "task_default_exchange": "reconhive",
        "task_default_exchange_type": "direct",
        "task_default_routing_key": "default",

        # Queues
        "task_queues": (
            Queue("default", Exchange("reconhive", type="direct"), routing_key="default"),
            Queue("recon", Exchange("reconhive", type="direct"), routing_key="recon"),
            Queue("dns", Exchange("reconhive", type="direct"), routing_key="dns"),
            Queue("web", Exchange("reconhive", type="direct"), routing_key="web"),
            Queue("tech", Exchange("reconhive", type="direct"), routing_key="tech"),
            Queue("api", Exchange("reconhive", type="direct"), routing_key="api"),
            Queue("cloud", Exchange("reconhive", type="direct"), routing_key="cloud"),
            Queue("network", Exchange("reconhive", type="direct"), routing_key="network"),
            Queue("priority", Exchange("reconhive", type="direct"), routing_key="priority"),
        ),

        # Task routing
        "task_routes": {
            "app.workers.tasks.passive_recon": {"queue": "recon"},
            "app.workers.tasks.dns_resolve": {"queue": "dns"},
            "app.workers.tasks.web_discover": {"queue": "web"},
            "app.workers.tasks.tech_detect": {"queue": "tech"},
            "app.workers.tasks.api_discovery": {"queue": "api"},
            "app.workers.tasks.cloud_enum": {"queue": "cloud"},
            "app.workers.tasks.network_scan": {"queue": "network"},
        },

        # Worker settings
        "worker_log_format": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        "worker_task_log_format": "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
    }

    celery_app.config_from_object(celery_config)

    if app is not None:
        # Update with Flask/FastAPI config
        class ContextTask(celery_app.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app.Task = ContextTask

    return celery_app


# Celery signals
@signals.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    """Log task start"""
    logger.info(
        f"Task started: {task.name}",
        extra={
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@signals.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, result=None, **kwargs):
    """Log task completion"""
    logger.info(
        f"Task completed: {task.name}",
        extra={
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@signals.task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Log task failure"""
    logger.error(
        f"Task failed: {sender.name}",
        extra={
            "task_id": task_id,
            "exception": str(exception),
            "timestamp": datetime.utcnow().isoformat()
        },
        exc_info=True
    )


@signals.task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, **kwargs):
    """Log task retry"""
    logger.warning(
        f"Task retry: {sender.name}",
        extra={
            "task_id": task_id,
            "reason": str(reason),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


class CeleryTaskManager:
    """Manage Celery tasks programmatically"""

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get task status and result"""
        result = AsyncResult(task_id, app=celery_app)
        return {
            "task_id": task_id,
            "state": result.state,
            "result": result.result,
            "info": result.info,
            "ready": result.ready(),
            "successful": result.successful(),
            "failed": result.failed(),
        }

    @staticmethod
    def revoke_task(task_id: str, terminate: bool = False) -> bool:
        """Revoke a task"""
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task revoked: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task {task_id}: {str(e)}")
            return False

    @staticmethod
    def get_active_tasks() -> Dict[str, Any]:
        """Get all active tasks"""
        return celery_app.control.inspect().active()

    @staticmethod
    def get_registered_tasks() -> list:
        """Get all registered tasks"""
        return celery_app.control.inspect().registered()

    @staticmethod
    def get_worker_stats() -> Dict[str, Any]:
        """Get worker statistics"""
        return celery_app.control.inspect().stats()

    @staticmethod
    def get_queue_length(queue_name: str) -> int:
        """Get number of pending tasks in queue"""
        try:
            # This requires redis-py and direct redis access
            from redis import Redis
            redis = Redis.from_url(celery_app.conf.broker_url)
            return redis.llen(queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue length: {str(e)}")
            return -1

    @staticmethod
    def purge_queue(queue_name: str) -> bool:
        """Clear all tasks from a queue"""
        try:
            celery_app.control.purge()
            logger.warning(f"Queue purged: {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to purge queue: {str(e)}")
            return False
