from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Tuple
from app.models.job import Job, JobStatus
from app.core.exceptions import NotFoundError
from app.utils.logger import logger
from datetime import datetime

class JobService:
    @staticmethod
    def create_job(db: Session, scan_id: UUID, plugin_name: str, priority: int = 5) -> Job:
        db_job = Job(
            scan_id=scan_id,
            plugin_name=plugin_name,
            priority=priority,
            status=JobStatus.QUEUED,
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        logger.info("job_created", job_id=str(db_job.id), plugin=plugin_name, priority=priority)
        return db_job

    @staticmethod
    def get_job(db: Session, job_id: UUID) -> Job:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise NotFoundError(f"Job {job_id} not found")
        return job

    @staticmethod
    def list_jobs(db: Session, scan_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[Job], int]:
        query = db.query(Job).filter(Job.scan_id == scan_id)
        total = query.count()
        jobs = query.order_by(Job.priority.desc()).offset(skip).limit(limit).all()
        return jobs, total

    @staticmethod
    def update_job_status(db: Session, job_id: UUID, status: JobStatus, error_msg: str = None) -> Job:
        job = JobService.get_job(db, job_id)
        job.status = status
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in (JobStatus.COMPLETED, JobStatus.FAILED):
            job.completed_at = datetime.utcnow()
            if job.started_at:
                job.duration_seconds = int((job.completed_at - job.started_at).total_seconds())
        if error_msg and status == JobStatus.FAILED:
            job.last_error = error_msg
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info("job_status_updated", job_id=str(job_id), status=status.value)
        return job

    @staticmethod
    def update_progress(db: Session, job_id: UUID, progress: int) -> Job:
        job = JobService.get_job(db, job_id)
        job.progress_percent = min(100, max(0, progress))
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def retry_job(db: Session, job_id: UUID) -> Job:
        job = JobService.get_job(db, job_id)
        if job.retries >= job.max_retries:
            raise ValueError(f"Max retries exceeded")
        job.retries += 1
        job.status = JobStatus.QUEUED
        job.started_at = None
        job.completed_at = None
        job.progress_percent = 0
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info("job_retried", job_id=str(job_id), retry_count=job.retries)
        return job

    @staticmethod
    def assign_worker(db: Session, job_id: UUID, worker_id: str) -> Job:
        job = JobService.get_job(db, job_id)
        job.worker_id = worker_id
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info("worker_assigned", job_id=str(job_id), worker_id=worker_id)
        return job
