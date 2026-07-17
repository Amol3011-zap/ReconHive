"""
Worker health monitoring and statistics
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from celery.app.utils import Settings

from app.workers.celery_app import celery_app, CeleryTaskManager
from app.db.session import SessionLocal
from app.models import ToolRun, ToolRunStatus, Scan
from sqlalchemy import func

logger = logging.getLogger(__name__)


class WorkerMonitor:
    """Monitor and manage worker health and performance"""

    @staticmethod
    def get_worker_stats() -> Dict[str, Any]:
        """Get statistics for all workers"""
        try:
            inspect = celery_app.control.inspect()
            stats = inspect.stats()

            if not stats:
                return {
                    "workers": {},
                    "total_workers": 0,
                    "online": False
                }

            worker_summary = {}
            for worker_name, worker_data in stats.items():
                worker_summary[worker_name] = {
                    "pool": worker_data.get("pool", {}),
                    "total_tasks": sum(
                        worker_data.get("pool", {}).get("max-concurrency", 0) for _ in [1]
                    ),
                }

            return {
                "workers": worker_summary,
                "total_workers": len(worker_summary),
                "online": True,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get worker stats: {str(e)}")
            return {
                "workers": {},
                "total_workers": 0,
                "online": False,
                "error": str(e)
            }

    @staticmethod
    def get_active_tasks() -> Dict[str, Any]:
        """Get all active tasks"""
        try:
            inspect = celery_app.control.inspect()
            active = inspect.active()

            if not active:
                return {
                    "active_tasks": [],
                    "total_active": 0
                }

            all_tasks = []
            for worker_name, tasks in active.items():
                for task in tasks:
                    task["worker"] = worker_name
                    all_tasks.append(task)

            return {
                "active_tasks": all_tasks,
                "total_active": len(all_tasks),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get active tasks: {str(e)}")
            return {
                "active_tasks": [],
                "total_active": 0,
                "error": str(e)
            }

    @staticmethod
    def get_registered_tasks() -> Dict[str, List[str]]:
        """Get all registered tasks"""
        try:
            inspect = celery_app.control.inspect()
            registered = inspect.registered()

            if not registered:
                return {"tasks": [], "total": 0}

            all_tasks = set()
            for worker_name, tasks in registered.items():
                all_tasks.update(tasks)

            return {
                "tasks": sorted(list(all_tasks)),
                "total": len(all_tasks),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get registered tasks: {str(e)}")
            return {
                "tasks": [],
                "total": 0,
                "error": str(e)
            }

    @staticmethod
    def get_queue_stats() -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            inspect = celery_app.control.inspect()
            active = inspect.active()

            queue_stats = {}
            if active:
                for worker_name, tasks in active.items():
                    for task in tasks:
                        queue = task.get("delivery_info", {}).get("routing_key", "unknown")
                        if queue not in queue_stats:
                            queue_stats[queue] = {
                                "active": 0,
                                "workers": set()
                            }
                        queue_stats[queue]["active"] += 1
                        queue_stats[queue]["workers"].add(worker_name)

            # Convert sets to lists for JSON serialization
            for queue_name in queue_stats:
                queue_stats[queue_name]["workers"] = list(queue_stats[queue_name]["workers"])
                queue_stats[queue_name]["worker_count"] = len(queue_stats[queue_name]["workers"])

            return {
                "queues": queue_stats,
                "total_queues": len(queue_stats),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get queue stats: {str(e)}")
            return {
                "queues": {},
                "total_queues": 0,
                "error": str(e)
            }

    @staticmethod
    def get_tool_run_stats(db=None) -> Dict[str, Any]:
        """Get tool run statistics from database"""
        if db is None:
            db = SessionLocal()
            should_close = True
        else:
            should_close = False

        try:
            total_runs = db.query(ToolRun).count()
            completed = db.query(ToolRun).filter(ToolRun.status == "completed").count()
            failed = db.query(ToolRun).filter(ToolRun.status == "failed").count()
            running = db.query(ToolRun).filter(ToolRun.status == "running").count()

            # Average execution time
            avg_duration = db.query(func.avg(ToolRun.duration_seconds)).scalar()

            # By tool
            tool_stats = {}
            tool_runs = db.query(ToolRun.tool_name, func.count(ToolRun.id).label("count")).group_by(ToolRun.tool_name).all()
            for tool_name, count in tool_runs:
                tool_stats[tool_name] = count

            # Recent runs (last 24 hours)
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent = db.query(ToolRun).filter(ToolRun.created_at >= last_24h).count()

            return {
                "total_runs": total_runs,
                "completed": completed,
                "failed": failed,
                "running": running,
                "success_rate": f"{(completed/total_runs*100):.1f}%" if total_runs > 0 else "0%",
                "average_duration_seconds": avg_duration,
                "tools": tool_stats,
                "recent_24h": recent,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get tool run stats: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            if should_close:
                db.close()

    @staticmethod
    def get_scan_progress(scan_id: str, db=None) -> Dict[str, Any]:
        """Get progress of a specific scan"""
        if db is None:
            db = SessionLocal()
            should_close = True
        else:
            should_close = False

        try:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                return {
                    "error": f"Scan {scan_id} not found"
                }

            # Get tool runs for this scan
            tool_runs = db.query(ToolRun).filter(ToolRun.scan_id == scan_id).all()

            completed = sum(1 for r in tool_runs if r.status == "completed")
            failed = sum(1 for r in tool_runs if r.status == "failed")
            running = sum(1 for r in tool_runs if r.status == "running")
            queued = sum(1 for r in tool_runs if r.status == "queued")

            total = len(tool_runs)
            progress = (completed / total * 100) if total > 0 else 0

            return {
                "scan_id": str(scan_id),
                "status": scan.status.value if scan.status else "unknown",
                "progress_percent": progress,
                "total_tools": total,
                "completed": completed,
                "running": running,
                "failed": failed,
                "queued": queued,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "tool_runs": [
                    {
                        "tool_name": r.tool_name,
                        "status": r.status,
                        "started": r.started_at.isoformat() if r.started_at else None,
                        "completed": r.completed_at.isoformat() if r.completed_at else None,
                    }
                    for r in tool_runs
                ],
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get scan progress: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            if should_close:
                db.close()

    @staticmethod
    def get_health_check() -> Dict[str, Any]:
        """Comprehensive health check"""
        workers = WorkerMonitor.get_worker_stats()
        queues = WorkerMonitor.get_queue_stats()
        tasks = WorkerMonitor.get_registered_tasks()
        active = WorkerMonitor.get_active_tasks()

        is_healthy = (
            workers.get("online", False) and
            workers.get("total_workers", 0) > 0
        )

        return {
            "healthy": is_healthy,
            "workers_online": workers.get("total_workers", 0),
            "active_tasks": active.get("total_active", 0),
            "registered_tasks": tasks.get("total", 0),
            "queues_running": queues.get("total_queues", 0),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "OPERATIONAL" if is_healthy else "DEGRADED"
        }
