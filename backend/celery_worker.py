"""
Celery worker entry point
"""

import os
import logging

from app.workers.celery_app import init_celery

# Initialize Celery
celery_app = init_celery()

# Import tasks so they're registered
from app.workers import tasks  # noqa

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s: %(levelname)s] %(name)s - %(message)s"
)

if __name__ == "__main__":
    celery_app.start()
