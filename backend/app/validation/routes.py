"""
API routes for proof validation engine.
Allows analysts to validate discovered vulnerabilities.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from app.validation.base import ValidatorRegistry, VulnerabilityType
from app.validation.validators.sqli import SQLiValidator
from app.validation.validators.xss import XSSValidator
from app.validation.validators.ssrf import SSRFValidator
from app.validation.payloads import PayloadLibrary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])

# Global validator registry
_validator_registry: Optional[ValidatorRegistry] = None


def initialize_validators():
    """Initialize all validators"""
    global _validator_registry

    _validator_registry = ValidatorRegistry()

    # Register all validators
    _validator_registry.register(SQLiValidator())
    _validator_registry.register(XSSValidator())
    _validator_registry.register(SSRFValidator())

    # TODO: Add more validators
    # - Broken Access Control
    # - XXE
    # - SSTI
    # - LFI/RFI
    # - Open Redirect
    # - File Upload
    # - API Authorization
    # - Security Misconfiguration

    logger.info("Validators initialized")


@router.on_event("startup")
async def startup():
    """Initialize validators on startup"""
    initialize_validators()


@router.get("/status")
async def validation_status():
    """Check validation engine status"""
    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    return {
        "status": "ready",
        "validators": _validator_registry.list_validators(),
        "total_validators": len(_validator_registry.validators),
    }


@router.get("/validators")
async def list_validators():
    """List all available validators"""
    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    return _validator_registry.list_validators()


@router.post("/validate/{vulnerability_type}")
async def validate_finding(
    vulnerability_type: str,
    target_url: str,
    parameter: str = "",
    method: str = Query("GET", regex="^(GET|POST|PUT|DELETE)$"),
    **kwargs
):
    """
    Validate a discovered vulnerability.

    Args:
        vulnerability_type: Type of vulnerability (sql_injection, xss, ssrf, etc.)
        target_url: URL to validate against
        parameter: Parameter name to test (for injection-type vulnerabilities)
        method: HTTP method to use

    Returns:
        Validation result with evidence and confidence score
    """

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    try:
        vuln_type = VulnerabilityType[vulnerability_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown vulnerability type: {vulnerability_type}"
        )

    try:
        result = _validator_registry.validate(
            vuln_type=vuln_type,
            target_url=target_url,
            parameter=parameter,
            method=method,
            **kwargs
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No validator for {vulnerability_type}"
            )

        return result.to_dict()

    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/xss")
async def validate_xss(
    target_url: str,
    parameter: str,
    xss_type: str = Query("reflected", regex="^(reflected|stored|dom)$"),
):
    """
    Validate XSS vulnerability.

    Args:
        target_url: URL to test
        parameter: Parameter name
        xss_type: Type of XSS (reflected, stored, dom)
    """

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    try:
        result = _validator_registry.validate(
            vuln_type=VulnerabilityType.REFLECTED_XSS,
            target_url=target_url,
            parameter=parameter,
            xss_type=xss_type,
        )

        return result.to_dict()

    except Exception as e:
        logger.error(f"XSS validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/batch")
async def validate_batch(
    findings: List[Dict[str, Any]],
):
    """
    Validate multiple findings in batch.

    Args:
        findings: List of findings to validate
            [{
                "vulnerability_type": "sql_injection",
                "target_url": "https://example.com",
                "parameter": "id",
                ...
            }]

    Returns:
        List of validation results
    """

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    results = []
    for finding in findings:
        try:
            vuln_type = VulnerabilityType[finding["vulnerability_type"].upper()]
            result = _validator_registry.validate(
                vuln_type=vuln_type,
                target_url=finding["target_url"],
                parameter=finding.get("parameter", ""),
                **{k: v for k, v in finding.items()
                   if k not in ["vulnerability_type", "target_url", "parameter"]}
            )
            if result:
                results.append(result.to_dict())
        except Exception as e:
            logger.error(f"Batch validation error: {str(e)}")
            results.append({
                "error": str(e),
                "vulnerability_type": finding.get("vulnerability_type"),
                "target_url": finding.get("target_url"),
            })

    return {"validations": results}


@router.get("/history")
async def validation_history(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get validation history"""

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    history = _validator_registry.get_history()
    return {
        "total": len(history),
        "limit": limit,
        "offset": offset,
        "validations": history[offset:offset+limit]
    }


@router.get("/stats")
async def validation_stats():
    """Get validation statistics"""

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    return _validator_registry.get_stats()


@router.post("/validate-finding/{finding_id}")
async def validate_specific_finding(
    finding_id: UUID,
    target_url: str,
    vulnerability_type: str,
    parameter: str = "",
):
    """
    Validate a specific finding from database.

    Args:
        finding_id: UUID of finding to validate
        target_url: URL to validate against
        vulnerability_type: Type of vulnerability
        parameter: Parameter name
    """

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    try:
        # TODO: Load finding from database using finding_id
        # For now, just validate the provided details

        vuln_type = VulnerabilityType[vulnerability_type.upper()]
        result = _validator_registry.validate(
            vuln_type=vuln_type,
            target_url=target_url,
            parameter=parameter,
        )

        if result:
            # TODO: Update finding in database with validation result
            return result.to_dict()

    except Exception as e:
        logger.error(f"Finding validation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payloads")
async def get_all_payloads():
    """Get all available payload categories"""
    return {
        "categories": PayloadLibrary.get_all_categories(),
        "total_payloads": sum(PayloadLibrary.get_all_categories().values()),
    }


@router.get("/payloads/{category}")
async def get_payloads_by_category(
    category: str,
    subcategory: str = Query("", description="Optional subcategory")
):
    """
    Get payloads for a specific category.

    Args:
        category: Payload category (sql_injection, xss, ssrf, etc.)
        subcategory: Optional subcategory (e.g., 'mysql', 'reflected')
    """
    payloads = PayloadLibrary.get_payloads(category, subcategory)

    if not payloads:
        raise HTTPException(
            status_code=404,
            detail=f"No payloads found for {category}/{subcategory}"
        )

    return {
        "category": category,
        "subcategory": subcategory,
        "total_payloads": len(payloads),
        "payloads": payloads,
    }


@router.post("/test-payload")
async def test_payload(
    target_url: str,
    vulnerability_type: str,
    payload: str,
    parameter: str = "",
    method: str = Query("GET", regex="^(GET|POST)$"),
):
    """
    Test a specific payload against a target.

    Args:
        target_url: Target URL
        vulnerability_type: Type of vulnerability
        payload: Payload to test
        parameter: Parameter to inject into
        method: HTTP method
    """

    if not _validator_registry:
        raise HTTPException(status_code=503, detail="Validators not initialized")

    try:
        # This would require custom implementation
        # For now, return the configuration
        return {
            "target_url": target_url,
            "vulnerability_type": vulnerability_type,
            "payload": payload,
            "parameter": parameter,
            "method": method,
            "status": "configured",
            "message": "Ready to test payload",
        }

    except Exception as e:
        logger.error(f"Payload test error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
