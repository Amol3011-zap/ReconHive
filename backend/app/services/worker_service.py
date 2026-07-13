from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
from app.models import Worker, WorkerStatus, WorkerType, Job, JobStatus
from app.utils.logger import logger

class WorkerService:
    """Service to manage workers and track their status."""

    @staticmethod
    def create_worker(db: Session, name: str, worker_type: WorkerType = WorkerType.RECONNAISSANCE) -> Worker:
        """Create a new worker."""
        existing = db.query(Worker).filter(Worker.name == name).first()
        if existing:
            raise ValueError(f"Worker {name} already exists")

        worker = Worker(
            name=name,
            type=worker_type,
            status=WorkerStatus.ONLINE,
            last_heartbeat=datetime.utcnow()
        )
        db.add(worker)
        db.commit()
        logger.info("worker_created", name=name, type=worker_type.value)
        return worker

    @staticmethod
    def list_workers(db: Session, skip: int = 0, limit: int = 50) -> tuple:
        """List all workers."""
        total = db.query(Worker).count()
        workers = db.query(Worker).offset(skip).limit(limit).all()
        return workers, total

    @staticmethod
    def get_worker(db: Session, worker_id: UUID) -> Worker:
        """Get a specific worker."""
        worker = db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise ValueError(f"Worker {worker_id} not found")
        return worker

    @staticmethod
    def update_worker_status(db: Session, worker_id: UUID, status: WorkerStatus) -> Worker:
        """Update worker status."""
        worker = WorkerService.get_worker(db, worker_id)
        worker.status = status
        worker.last_heartbeat = datetime.utcnow()
        db.commit()
        logger.info("worker_status_updated", worker_id=worker_id, status=status.value)
        return worker

    @staticmethod
    def update_worker_metrics(db: Session, worker_id: UUID, cpu_usage: float, memory_usage: float) -> Worker:
        """Update worker resource metrics."""
        worker = WorkerService.get_worker(db, worker_id)
        worker.cpu_usage = cpu_usage
        worker.memory_usage = memory_usage
        worker.last_heartbeat = datetime.utcnow()
        db.commit()
        return worker

    @staticmethod
    def heartbeat(db: Session, worker_id: UUID) -> Worker:
        """Update worker heartbeat (keep-alive)."""
        worker = WorkerService.get_worker(db, worker_id)
        worker.last_heartbeat = datetime.utcnow()

        if worker.status == WorkerStatus.OFFLINE:
            worker.status = WorkerStatus.ONLINE

        db.commit()
        return worker

    @staticmethod
    def update_job_count(db: Session, worker_id: UUID) -> Worker:
        """Update active job count based on database."""
        worker = WorkerService.get_worker(db, worker_id)
        active_jobs = db.query(Job).filter(
            Job.worker_id == str(worker_id),
            Job.status == JobStatus.RUNNING
        ).count()
        worker.active_jobs = active_jobs
        db.commit()
        return worker

    @staticmethod
    def seed_workers(db: Session) -> list:
        """Seed default workers if they don't exist."""
        workers_config = [
            ("recon-worker-1", WorkerType.RECONNAISSANCE),
            ("recon-worker-2", WorkerType.RECONNAISSANCE),
            ("nuclei-worker", WorkerType.VULNERABILITY_ASSESSMENT),
            ("evidence-worker", WorkerType.EVIDENCE),
            ("ai-copilot", WorkerType.REPORTING),
        ]

        created_workers = []
        for name, worker_type in workers_config:
            existing = db.query(Worker).filter(Worker.name == name).first()
            if not existing:
                worker = WorkerService.create_worker(db, name, worker_type)
                created_workers.append(worker)
            else:
                created_workers.append(existing)

        return created_workers

    @staticmethod
    def get_available_workers(db: Session) -> list:
        """Get list of available workers."""
        workers = db.query(Worker).filter(
            Worker.is_enabled == True,
            Worker.status.in_([WorkerStatus.ONLINE, WorkerStatus.BUSY])
        ).order_by(Worker.active_jobs).all()
        return workers
