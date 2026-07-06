from typing import Dict, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from uuid import uuid4
from app.utils.logger import logger
import asyncio


class JobStatus(str, Enum):
    """Job execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobMetrics:
    """Job execution metrics."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    memory_used_mb: float = 0.0
    status_code: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class ExecutionJob:
    """Represents a job in the execution queue."""
    job_id: str = field(default_factory=lambda: str(uuid4()))
    plugin_id: str = ""
    scan_id: str = ""
    input_data: Dict = field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED
    priority: int = 50  # 1-100, higher = priority
    metrics: JobMetrics = field(default_factory=JobMetrics)
    result: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    callbacks: List[Callable] = field(default_factory=list)

    def __lt__(self, other):
        """Priority comparison for queue ordering."""
        return self.priority > other.priority  # Higher priority first


class ExecutionQueue:
    """Job execution queue for plugin execution."""

    def __init__(self, max_workers: int = 4):
        self.queue: List[ExecutionJob] = []
        self.max_workers = max_workers
        self.active_jobs: Dict[str, ExecutionJob] = {}
        self.completed_jobs: Dict[str, ExecutionJob] = {}

    def enqueue(self, plugin_id: str, scan_id: str, input_data: Dict,
               priority: int = 50, max_retries: int = 3) -> str:
        """Add job to queue."""
        job = ExecutionJob(
            plugin_id=plugin_id,
            scan_id=scan_id,
            input_data=input_data,
            priority=min(100, max(1, priority)),
            max_retries=max_retries,
        )

        self.queue.append(job)
        self.queue.sort()
        logger.info("job_queued", job_id=job.job_id, plugin_id=plugin_id, position=len(self.queue))
        return job.job_id

    def get_next_job(self) -> Optional[ExecutionJob]:
        """Get next job to execute."""
        if len(self.active_jobs) >= self.max_workers:
            return None
        if not self.queue:
            return None

        job = self.queue.pop(0)
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.metrics.start_time = job.started_at
        self.active_jobs[job.job_id] = job
        logger.info("job_started", job_id=job.job_id, plugin_id=job.plugin_id)
        return job

    def complete_job(self, job_id: str, result: Optional[Dict] = None,
                    error: Optional[str] = None) -> bool:
        """Mark job as completed."""
        if job_id not in self.active_jobs:
            return False

        job = self.active_jobs[job_id]
        job.completed_at = datetime.utcnow()
        job.metrics.end_time = job.completed_at
        job.metrics.duration_seconds = (job.completed_at - job.started_at).total_seconds()

        if error:
            job.status = JobStatus.FAILED
            job.metrics.error_message = error
            logger.error("job_failed", job_id=job_id, error=error)

            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.QUEUED
                self.queue.append(job)
                logger.info("job_requeued", job_id=job_id, attempt=job.retry_count)
                return True
        else:
            job.status = JobStatus.COMPLETED
            job.result = result
            logger.info("job_completed", job_id=job_id)

        del self.active_jobs[job_id]
        self.completed_jobs[job_id] = job

        for callback in job.callbacks:
            try:
                callback(job)
            except Exception as e:
                logger.error("job_callback_failed", job_id=job_id, error=str(e))

        return True

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        if job_id in self.queue:
            self.queue = [j for j in self.queue if j.job_id != job_id]
            logger.info("job_cancelled", job_id=job_id)
            return True

        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = JobStatus.CANCELLED
            del self.active_jobs[job_id]
            self.completed_jobs[job_id] = job
            logger.info("job_cancelled", job_id=job_id)
            return True

        return False

    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get job status."""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id].status.value
        if job_id in self.completed_jobs:
            return self.completed_jobs[job_id].status.value
        return None

    def get_queue_length(self) -> int:
        """Get number of jobs in queue."""
        return len(self.queue)

    def get_active_count(self) -> int:
        """Get number of active jobs."""
        return len(self.active_jobs)

    def stats(self) -> Dict:
        """Get queue statistics."""
        return {
            "queued": len(self.queue),
            "active": len(self.active_jobs),
            "completed": len(self.completed_jobs),
            "max_workers": self.max_workers,
            "utilization": len(self.active_jobs) / self.max_workers,
        }


# Global execution queue instance
execution_queue = ExecutionQueue(max_workers=4)
