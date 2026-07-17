"""
Reconnaissance Service - Core business logic for recon operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from app.models import (
    Subdomain, SubdomainStatus, DNSRecord, DNSRecordType,
    URLEndpoint, URLStatus, Technology, TechCategory,
    JavaScriptAsset, APIEndpoint, Parameter,
    CloudAsset, CloudProvider, ToolRun, ToolRunStatus,
    Asset, AssetType, Scan, ScanStatus
)

logger = logging.getLogger(__name__)

class SubdomainService:
    """Service for managing subdomains"""

    @staticmethod
    def create_subdomain(
        db: Session,
        engagement_id: UUID,
        asset_id: UUID,
        name: str,
        domain: str,
        sources: List[str],
        scan_id: Optional[UUID] = None,
        is_wildcard: bool = False
    ) -> Subdomain:
        """Create a new subdomain record"""
        subdomain = Subdomain(
            engagement_id=engagement_id,
            asset_id=asset_id,
            scan_id=scan_id,
            name=name,
            domain=domain,
            is_wildcard=is_wildcard,
            sources={"sources": sources},
            first_discovered_date=datetime.utcnow(),
            status=SubdomainStatus.DISCOVERED
        )
        db.add(subdomain)
        db.commit()
        db.refresh(subdomain)
        logger.info(f"Created subdomain: {name}", extra={"subdomain_id": str(subdomain.id)})
        return subdomain

    @staticmethod
    def get_subdomains(
        db: Session,
        engagement_id: UUID,
        status: Optional[SubdomainStatus] = None,
        is_takeover_candidate: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple:
        """Get subdomains for an engagement"""
        query = db.query(Subdomain).filter(Subdomain.engagement_id == engagement_id)

        if status:
            query = query.filter(Subdomain.status == status)

        if is_takeover_candidate is not None:
            query = query.filter(Subdomain.is_takeover_candidate == is_takeover_candidate)

        total = query.count()
        subdomains = query.offset(skip).limit(limit).all()
        return subdomains, total

    @staticmethod
    def update_subdomain_status(
        db: Session,
        subdomain_id: UUID,
        status: SubdomainStatus,
        last_verified_date: Optional[datetime] = None
    ) -> Subdomain:
        """Update subdomain status"""
        subdomain = db.query(Subdomain).filter(Subdomain.id == subdomain_id).first()
        if not subdomain:
            raise ValueError(f"Subdomain {subdomain_id} not found")

        subdomain.status = status
        if last_verified_date:
            subdomain.last_verified_date = last_verified_date
        if status == SubdomainStatus.ALIVE:
            subdomain.last_active_date = datetime.utcnow()

        db.commit()
        db.refresh(subdomain)
        return subdomain

    @staticmethod
    def mark_takeover_candidate(db: Session, subdomain_id: UUID) -> Subdomain:
        """Mark subdomain as potential takeover target"""
        subdomain = db.query(Subdomain).filter(Subdomain.id == subdomain_id).first()
        if not subdomain:
            raise ValueError(f"Subdomain {subdomain_id} not found")

        subdomain.is_takeover_candidate = True
        db.commit()
        db.refresh(subdomain)
        logger.warning(f"Subdomain marked as takeover candidate: {subdomain.name}")
        return subdomain


class DNSService:
    """Service for managing DNS records"""

    @staticmethod
    def create_dns_record(
        db: Session,
        engagement_id: UUID,
        subdomain_id: UUID,
        hostname: str,
        record_type: DNSRecordType,
        value: str,
        ttl: Optional[int] = None,
        resolver_used: Optional[str] = None,
        scan_id: Optional[UUID] = None
    ) -> DNSRecord:
        """Create a DNS record"""
        record = DNSRecord(
            engagement_id=engagement_id,
            subdomain_id=subdomain_id,
            scan_id=scan_id,
            hostname=hostname,
            record_type=record_type,
            value=value,
            ttl=ttl,
            resolver_used=resolver_used,
            discovered_date=datetime.utcnow(),
            is_active="unknown"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_dns_records_by_hostname(
        db: Session,
        engagement_id: UUID,
        hostname: str
    ) -> List[DNSRecord]:
        """Get all DNS records for a hostname"""
        return db.query(DNSRecord).filter(
            and_(
                DNSRecord.engagement_id == engagement_id,
                DNSRecord.hostname == hostname
            )
        ).all()

    @staticmethod
    def get_dns_records_by_type(
        db: Session,
        engagement_id: UUID,
        record_type: DNSRecordType
    ) -> List[DNSRecord]:
        """Get DNS records by type"""
        return db.query(DNSRecord).filter(
            and_(
                DNSRecord.engagement_id == engagement_id,
                DNSRecord.record_type == record_type
            )
        ).all()


class URLService:
    """Service for managing URL endpoints"""

    @staticmethod
    def create_url_endpoint(
        db: Session,
        engagement_id: UUID,
        asset_id: UUID,
        url: str,
        discovered_from: str = "unknown",
        scan_id: Optional[UUID] = None,
        subdomain_id: Optional[UUID] = None
    ) -> URLEndpoint:
        """Create a URL endpoint record"""
        endpoint = URLEndpoint(
            engagement_id=engagement_id,
            asset_id=asset_id,
            subdomain_id=subdomain_id,
            scan_id=scan_id,
            url=url,
            discovered_from=discovered_from,
            discovered_date=datetime.utcnow(),
            first_seen_date=datetime.utcnow(),
            status=URLStatus.PENDING
        )
        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)
        return endpoint

    @staticmethod
    def update_url_response(
        db: Session,
        endpoint_id: UUID,
        status_code: int,
        content_type: str,
        content_length: int,
        headers: Dict[str, Any],
        response_body_preview: Optional[str] = None,
        page_title: Optional[str] = None
    ) -> URLEndpoint:
        """Update URL endpoint with HTTP response data"""
        endpoint = db.query(URLEndpoint).filter(URLEndpoint.id == endpoint_id).first()
        if not endpoint:
            raise ValueError(f"Endpoint {endpoint_id} not found")

        endpoint.response_status_code = status_code
        endpoint.response_content_type = content_type
        endpoint.response_content_length = content_length
        endpoint.response_headers = headers
        endpoint.response_body_preview = response_body_preview
        endpoint.page_title = page_title
        endpoint.last_probed_date = datetime.utcnow()

        # Determine status
        if 200 <= status_code < 300:
            endpoint.status = URLStatus.ALIVE
        elif 300 <= status_code < 400:
            endpoint.status = URLStatus.REDIRECT
        elif 400 <= status_code < 500:
            endpoint.status = URLStatus.ALIVE  # Still alive, just not accessible
        elif status_code >= 500:
            endpoint.status = URLStatus.ERROR
        else:
            endpoint.status = URLStatus.UNKNOWN

        db.commit()
        db.refresh(endpoint)
        return endpoint

    @staticmethod
    def get_alive_endpoints(
        db: Session,
        engagement_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> tuple:
        """Get alive URL endpoints"""
        query = db.query(URLEndpoint).filter(
            and_(
                URLEndpoint.engagement_id == engagement_id,
                URLEndpoint.status == URLStatus.ALIVE
            )
        )
        total = query.count()
        endpoints = query.offset(skip).limit(limit).all()
        return endpoints, total


class TechnologyService:
    """Service for managing detected technologies"""

    @staticmethod
    def create_technology(
        db: Session,
        engagement_id: UUID,
        asset_id: UUID,
        name: str,
        category: str,
        version: Optional[str] = None,
        confidence: float = 0.0,
        detected_method: str = "unknown",
        detected_from_url: Optional[str] = None,
        scan_id: Optional[UUID] = None,
        subdomain_id: Optional[UUID] = None
    ) -> Technology:
        """Create a technology record"""
        tech = Technology(
            engagement_id=engagement_id,
            asset_id=asset_id,
            subdomain_id=subdomain_id,
            scan_id=scan_id,
            name=name,
            category=category,
            version=version,
            confidence=confidence,
            detected_method=detected_method,
            detected_from_url=detected_from_url,
            detected_at=datetime.utcnow()
        )
        db.add(tech)
        db.commit()
        db.refresh(tech)
        return tech

    @staticmethod
    def get_technologies_by_asset(
        db: Session,
        asset_id: UUID,
        category: Optional[str] = None
    ) -> List[Technology]:
        """Get technologies for an asset"""
        query = db.query(Technology).filter(Technology.asset_id == asset_id)
        if category:
            query = query.filter(Technology.category == category)
        return query.all()

    @staticmethod
    def get_technology_summary(db: Session, engagement_id: UUID) -> Dict[str, Any]:
        """Get technology summary for engagement"""
        technologies = db.query(Technology).filter(
            Technology.engagement_id == engagement_id
        ).all()

        summary = {
            "total_technologies": len(technologies),
            "by_category": {},
            "frontend_frameworks": [],
            "backend_frameworks": [],
            "web_servers": [],
            "vulnerable_count": 0
        }

        for tech in technologies:
            category = tech.category
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1

            if tech.is_known_vulnerable == "yes":
                summary["vulnerable_count"] += 1

            if category == "frontend_framework":
                summary["frontend_frameworks"].append(f"{tech.name} v{tech.version or 'unknown'}")
            elif category == "backend_framework":
                summary["backend_frameworks"].append(f"{tech.name} v{tech.version or 'unknown'}")
            elif category == "web_server":
                summary["web_servers"].append(f"{tech.name} v{tech.version or 'unknown'}")

        return summary


class ToolRunService:
    """Service for managing tool execution runs"""

    @staticmethod
    def create_tool_run(
        db: Session,
        engagement_id: UUID,
        scan_id: UUID,
        job_id: UUID,
        tool_name: str,
        target: str,
        arguments: Dict[str, Any],
        tool_category: str = "unknown",
        tool_version: Optional[str] = None
    ) -> ToolRun:
        """Create a tool run record"""
        run = ToolRun(
            engagement_id=engagement_id,
            scan_id=scan_id,
            job_id=job_id,
            tool_name=tool_name,
            tool_version=tool_version,
            tool_category=tool_category,
            target=target,
            arguments=arguments,
            status=ToolRunStatus.QUEUED
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def update_tool_run_status(
        db: Session,
        run_id: UUID,
        status: ToolRunStatus,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> ToolRun:
        """Update tool run status"""
        run = db.query(ToolRun).filter(ToolRun.id == run_id).first()
        if not run:
            raise ValueError(f"Tool run {run_id} not found")

        run.status = status.value
        run.exit_code = exit_code
        if stdout:
            run.stdout = stdout[:10000]  # Store first 10KB
        if stderr:
            run.stderr = stderr[:10000]
        if error_message:
            run.error_message = error_message
        run.updated_at = datetime.utcnow()

        if status == ToolRunStatus.COMPLETED:
            run.completed_at = datetime.utcnow()
            if run.started_at:
                run.duration_seconds = int((run.completed_at - run.started_at).total_seconds())

        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def get_tool_runs_by_scan(
        db: Session,
        scan_id: UUID,
        status: Optional[str] = None
    ) -> List[ToolRun]:
        """Get tool runs for a scan"""
        query = db.query(ToolRun).filter(ToolRun.scan_id == scan_id)
        if status:
            query = query.filter(ToolRun.status == status)
        return query.all()
