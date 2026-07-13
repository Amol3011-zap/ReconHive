from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta
import random
import json
from app.models import Scan, ScanStatus, Job, JobStatus, Worker, Finding, Severity, Evidence, EvidenceType
from app.utils.logger import logger

class ScanExecutorService:
    """Service to execute scans, manage jobs, and generate findings."""

    @staticmethod
    def start_scan(db: Session, scan_id: UUID) -> Scan:
        """Start a queued scan and assign a worker."""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        if scan.status != ScanStatus.QUEUED:
            raise ValueError(f"Scan {scan_id} is not in QUEUED state")

        worker = ScanExecutorService._select_worker(db, scan)
        if not worker:
            raise ValueError("No available workers")

        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.utcnow()
        scan.worker_id = str(worker.id)
        scan.current_stage = "Initialize"
        db.commit()

        job = ScanExecutorService._create_job(db, scan, worker)
        logger.info("scan_started", scan_id=scan_id, worker_id=worker.id)

        return scan

    @staticmethod
    def _select_worker(db: Session, scan: Scan) -> Worker:
        """Select an available worker based on plugin requirements."""
        from app.models import WorkerStatus
        workers = db.query(Worker).filter(
            Worker.is_enabled == True,
            Worker.status.in_([WorkerStatus.ONLINE, WorkerStatus.BUSY])
        ).order_by(Worker.active_jobs).all()

        return workers[0] if workers else None

    @staticmethod
    def _create_job(db: Session, scan: Scan, worker: Worker) -> Job:
        """Create a job for the scan."""
        job = Job(
            scan_id=scan.id,
            plugin_name=scan.plugin_names[0] if scan.plugin_names else "Nuclei",
            status=JobStatus.RUNNING,
            worker_id=str(worker.id),
            configuration=scan.configuration or {},
            target_filter={"target": "acme.com"},
            logs=""
        )
        db.add(job)
        db.commit()
        return job

    @staticmethod
    def simulate_scan_progress(db: Session, scan_id: UUID) -> Scan:
        """Simulate scan execution and update progress."""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan or scan.status != ScanStatus.RUNNING:
            return scan

        job = db.query(Job).filter(Job.scan_id == scan_id).first()
        if not job:
            return scan

        current_progress = scan.progress_percent

        if current_progress < 25:
            scan.current_stage = "Initialize"
            scan.progress_percent = random.randint(current_progress + 1, 25)
            job.logs += f"[{datetime.utcnow().strftime('%H:%M')}] Target validation started\n"

        elif current_progress < 50:
            scan.current_stage = "Scanning"
            scan.progress_percent = random.randint(current_progress + 1, 50)
            job.logs += f"[{datetime.utcnow().strftime('%H:%M')}] Scanning in progress ({scan.progress_percent}%)\n"

        elif current_progress < 75:
            scan.current_stage = "Scanning"
            scan.progress_percent = random.randint(current_progress + 1, 75)
            job.logs += f"[{datetime.utcnow().strftime('%H:%M')}] Found vulnerabilities ({scan.progress_percent}%)\n"

        else:
            scan.current_stage = "Reporting"
            scan.progress_percent = min(100, random.randint(current_progress + 1, 100))

            if scan.progress_percent >= 100:
                ScanExecutorService.complete_scan(db, scan, job)
                return scan

            job.logs += f"[{datetime.utcnow().strftime('%H:%M')}] Generating report ({scan.progress_percent}%)\n"

        job.progress_percent = scan.progress_percent
        db.commit()
        return scan

    @staticmethod
    def complete_scan(db: Session, scan: Scan, job: Job) -> Scan:
        """Complete scan and generate findings."""
        scan.status = ScanStatus.COMPLETED
        scan.progress_percent = 100
        scan.completed_at = datetime.utcnow()
        scan.current_stage = "Completed"

        duration = (scan.completed_at - scan.started_at).total_seconds()
        scan.duration_seconds = int(duration)

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.duration_seconds = int(duration)
        job.logs += f"[{datetime.utcnow().strftime('%H:%M')}] Scan completed in {int(duration)}s\n"

        ScanExecutorService._generate_findings(db, scan)
        ScanExecutorService._generate_evidence(db, scan, job)

        db.commit()
        logger.info("scan_completed", scan_id=scan.id)

        return scan

    @staticmethod
    def _generate_findings(db: Session, scan: Scan) -> list:
        """Generate realistic findings for the scan."""
        findings_data = [
            {
                "title": "Exposed Admin Panel",
                "severity": Severity.HIGH,
                "cvss_score": 7.5,
                "description": "An admin panel is publicly accessible without authentication",
                "remediation": "Restrict access to admin panel with authentication"
            },
            {
                "title": "Missing SPF Record",
                "severity": Severity.MEDIUM,
                "cvss_score": 5.3,
                "description": "Domain lacks SPF record for email spoofing protection",
                "remediation": "Configure SPF record in DNS"
            },
            {
                "title": "Weak TLS Configuration",
                "severity": Severity.HIGH,
                "cvss_score": 7.1,
                "description": "TLS 1.0 and 1.1 protocols are enabled",
                "remediation": "Disable legacy TLS versions"
            },
            {
                "title": "Outdated Apache Version",
                "severity": Severity.CRITICAL,
                "cvss_score": 9.0,
                "description": "Apache 2.4.1 detected with known vulnerabilities",
                "remediation": "Update to latest Apache version"
            },
            {
                "title": "Directory Listing Enabled",
                "severity": Severity.LOW,
                "cvss_score": 4.3,
                "description": "/uploads directory allows directory listing",
                "remediation": "Disable directory listing in server config"
            },
        ]

        findings = []
        for finding_data in findings_data:
            finding = Finding(
                engagement_id=scan.engagement_id,
                asset_id=scan.asset_id,
                scan_id=scan.id,
                title=finding_data["title"],
                severity=finding_data["severity"],
                cvss_score=finding_data["cvss_score"],
                description=finding_data["description"],
                remediation=finding_data["remediation"],
                status="open",
                detected_by="Nuclei",
                references=["https://owasp.org/www-community/attacks"],
            )
            db.add(finding)
            findings.append(finding)

        db.commit()
        return findings

    @staticmethod
    def _generate_evidence(db: Session, scan: Scan, job: Job) -> list:
        """Generate evidence artifacts."""
        evidence_data = [
            {
                "name": "HTTP Response Headers",
                "type": EvidenceType.HTTP_RESPONSE,
                "data": "HTTP/1.1 200 OK\nServer: Apache/2.4.1\nSet-Cookie: PHPSESSID=abc123"
            },
            {
                "name": "Scan Logs",
                "type": EvidenceType.LOG_FILE,
                "data": job.logs
            },
            {
                "name": "Nuclei Results",
                "type": EvidenceType.JSON_DATA,
                "data": json.dumps({"vulnerabilities": 5, "high": 2, "medium": 3})
            },
        ]

        evidence_list = []
        for evidence_data in evidence_data:
            evidence = Evidence(
                engagement_id=scan.engagement_id,
                scan_id=scan.id,
                asset_id=scan.asset_id,
                name=evidence_data["name"],
                type=evidence_data["type"],
                data=evidence_data["data"],
                mime_type="text/plain"
            )
            db.add(evidence)
            evidence_list.append(evidence)

        db.commit()
        return evidence_list

    @staticmethod
    def fail_scan(db: Session, scan_id: UUID, error_message: str) -> Scan:
        """Mark scan as failed."""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        scan.status = ScanStatus.FAILED
        scan.error_message = error_message
        scan.completed_at = datetime.utcnow()

        job = db.query(Job).filter(Job.scan_id == scan_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.last_error = error_message
            job.completed_at = datetime.utcnow()

        db.commit()
        logger.error("scan_failed", scan_id=scan_id, error=error_message)

        return scan
