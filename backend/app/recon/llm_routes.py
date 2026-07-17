"""
API routes for LLM integration and tool execution.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from app.recon.llm_integration import LLMClient, LLMConfig, LLMProvider
from app.tools.executor import ToolExecutor
from app.tools.implementations import (
    SubfinderTool, DNSXTool, HTTPXTool, NaabuTool, NucleiTool
)
from app.recon.agent_tool_integration import AgentToolIntegration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

# Global instances
_llm_client: Optional[LLMClient] = None
_tool_executor: Optional[ToolExecutor] = None
_integration: Optional[AgentToolIntegration] = None


def initialize_llm_services(api_key: str, provider: str = "openai"):
    """Initialize LLM and tool services"""
    global _llm_client, _tool_executor, _integration

    # Initialize LLM client
    llm_config = LLMConfig(
        provider=LLMProvider.OPENAI if provider == "openai" else LLMProvider.ANTHROPIC,
        api_key=api_key,
        model="gpt-4-turbo" if provider == "openai" else "claude-opus",
    )
    _llm_client = LLMClient(llm_config)

    # Initialize tool executor
    _tool_executor = ToolExecutor()
    _tool_executor.register_tool(SubfinderTool())
    _tool_executor.register_tool(DNSXTool())
    _tool_executor.register_tool(HTTPXTool())
    _tool_executor.register_tool(NaabuTool())
    _tool_executor.register_tool(NucleiTool())

    # Initialize integration
    _integration = AgentToolIntegration(_tool_executor, _llm_client)

    logger.info(f"Initialized LLM services with provider: {provider}")


@router.get("/status")
async def llm_status():
    """Check LLM service status"""
    return {
        "llm_initialized": _llm_client is not None,
        "tools_available": list(_tool_executor.list_tools().keys()) if _tool_executor else [],
        "integration_ready": _integration is not None,
    }


@router.get("/tools")
async def list_available_tools():
    """List all available reconnaissance tools"""
    if not _tool_executor:
        raise HTTPException(status_code=503, detail="Tool executor not initialized")

    return _tool_executor.list_tools()


@router.get("/tools/{tool_name}/status")
async def tool_status(tool_name: str):
    """Check status of specific tool"""
    if not _tool_executor:
        raise HTTPException(status_code=503, detail="Tool executor not initialized")

    tool = _tool_executor.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")

    available, msg = tool.check_availability()
    return {
        "tool_name": tool_name,
        "available": available,
        "message": msg,
        "version": tool.tool_version,
    }


@router.post("/select-tools")
async def select_tools_endpoint(
    target: str,
    phase: str = "full",
    context: str = ""
):
    """
    Use LLM to select best tools for target.

    Args:
        target: Reconnaissance target
        phase: Reconnaissance phase (passive, dns, web, port, vuln, full)
        context: Additional context

    Returns:
        Selected tools with reasoning
    """
    if not _integration:
        raise HTTPException(status_code=503, detail="Integration not initialized")

    try:
        tools = _integration.select_tools_for_phase(target, phase, context)
        return {
            "target": target,
            "phase": phase,
            "selected_tools": tools,
            "llm_enabled": _llm_client is not None,
        }
    except Exception as e:
        logger.error(f"Tool selection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-tools")
async def execute_tools_endpoint(
    tools: List[str],
    target: str,
    engagement_id: Optional[UUID] = None,
    scan_id: Optional[UUID] = None
):
    """
    Execute tools against target.

    Args:
        tools: List of tool names to execute
        target: Reconnaissance target
        engagement_id: Associated engagement
        scan_id: Associated scan

    Returns:
        Tool execution results
    """
    if not _integration:
        raise HTTPException(status_code=503, detail="Integration not initialized")

    try:
        results = _integration.execute_tools(
            tools=tools,
            target=target,
            engagement_id=engagement_id,
            scan_id=scan_id
        )

        return {
            "target": target,
            "tools_executed": list(results.keys()),
            "results": {
                name: result.to_dict()
                for name, result in results.items()
            },
            "summary": _integration.get_execution_summary(),
        }
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-results")
async def analyze_results_endpoint(
    target: str,
    results: Dict[str, Any]
):
    """
    Use LLM to analyze tool results.

    Args:
        target: Reconnaissance target
        results: Tool execution results

    Returns:
        LLM analysis with findings and recommendations
    """
    if not _integration:
        raise HTTPException(status_code=503, detail="Integration not initialized")

    try:
        analysis = _integration.analyze_results(target, results)
        return {
            "target": target,
            "analysis": analysis,
            "llm_enabled": _llm_client is not None,
        }
    except Exception as e:
        logger.error(f"Results analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution-summary")
async def execution_summary():
    """Get summary of all tool executions"""
    if not _integration:
        raise HTTPException(status_code=503, detail="Integration not initialized")

    return _integration.get_execution_summary()


@router.get("/tool-stats/{tool_name}")
async def tool_stats(tool_name: str):
    """Get execution statistics for a tool"""
    if not _tool_executor:
        raise HTTPException(status_code=503, detail="Tool executor not initialized")

    stats = _tool_executor.get_tool_stats(tool_name)
    if not stats:
        raise HTTPException(status_code=404, detail=f"No statistics for tool: {tool_name}")

    return stats
