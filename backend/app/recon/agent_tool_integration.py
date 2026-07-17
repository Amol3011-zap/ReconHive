"""
Integration layer between agents and tools.
Manages agent-tool communication and result processing.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.recon.llm_integration import LLMClient
from app.tools.executor import ToolExecutor
from app.tools.base import ToolResult

logger = logging.getLogger(__name__)


class AgentToolIntegration:
    """
    Integrates agents with tool execution.

    Responsibilities:
    - Route agent requests to appropriate tools
    - Parse LLM tool calls into executable commands
    - Collect and aggregate tool results
    - Track tool execution as evidence
    """

    def __init__(
        self,
        tool_executor: ToolExecutor,
        llm_client: Optional[LLMClient] = None
    ):
        self.tool_executor = tool_executor
        self.llm_client = llm_client
        self.execution_log: List[Dict[str, Any]] = []

    def select_tools_for_phase(
        self,
        target: str,
        phase: str,
        context: str = ""
    ) -> List[str]:
        """
        Select tools for reconnaissance phase using LLM.

        Args:
            target: Reconnaissance target
            phase: Current phase (passive, active, etc.)
            context: Additional context

        Returns:
            List of tool names to execute
        """
        available_tools = self.tool_executor.list_tools()

        if self.llm_client:
            context_msg = f"Phase: {phase}. {context}"
            return self.llm_client.select_tools(target, available_tools, context_msg)
        else:
            # Default tool selection by phase
            return self._default_tools_for_phase(phase)

    def execute_tools(
        self,
        tools: List[str],
        target: str,
        engagement_id: Optional[UUID] = None,
        scan_id: Optional[UUID] = None
    ) -> Dict[str, ToolResult]:
        """
        Execute tools against target.

        Args:
            tools: List of tool names to execute
            target: Reconnaissance target
            engagement_id: Associated engagement
            scan_id: Associated scan

        Returns:
            Dict of tool results
        """
        results = {}

        for tool_name in tools:
            logger.info(f"Executing tool: {tool_name} against target: {target}")

            try:
                result = self.tool_executor.execute_tool(
                    tool_name=tool_name,
                    target=target,
                    engagement_id=engagement_id,
                    scan_id=scan_id
                )

                results[tool_name] = result

                # Log execution
                self.execution_log.append({
                    "tool": tool_name,
                    "target": target,
                    "success": result.success,
                    "items_discovered": result.items_discovered,
                    "execution_time": result.execution_time,
                })

                logger.info(
                    f"Tool {tool_name} completed: "
                    f"{result.items_discovered} items discovered"
                )

            except Exception as e:
                logger.error(f"Tool execution failed: {tool_name} - {str(e)}")
                results[tool_name] = self._create_error_result(tool_name, str(e))

        return results

    def analyze_results(
        self,
        target: str,
        tool_results: Dict[str, ToolResult],
        available_tools: Optional[Dict[str, Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze tool results and recommend next steps using LLM.

        Args:
            target: Reconnaissance target
            tool_results: Results from executed tools
            available_tools: Available tools for next phase

        Returns:
            Analysis with findings and recommendations
        """
        # Convert ToolResult objects to dicts for LLM
        results_dict = {
            name: result.to_dict()
            for name, result in tool_results.items()
        }

        if self.llm_client:
            available = available_tools or self.tool_executor.list_tools()
            analysis = self.llm_client.analyze_results(target, results_dict, available)
        else:
            analysis = self._default_analysis(results_dict)

        return analysis

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all tool executions"""
        total_tools = len(self.execution_log)
        successful = sum(1 for log in self.execution_log if log["success"])
        total_time = sum(log["execution_time"] for log in self.execution_log)
        total_discovered = sum(log["items_discovered"] for log in self.execution_log)

        return {
            "total_executions": total_tools,
            "successful": successful,
            "failed": total_tools - successful,
            "success_rate": f"{(successful / total_tools * 100):.1f}%" if total_tools > 0 else "0%",
            "total_execution_time": total_time,
            "total_items_discovered": total_discovered,
            "executions": self.execution_log,
        }

    @staticmethod
    def _default_tools_for_phase(phase: str) -> List[str]:
        """Default tool selection by phase"""
        phase_tools = {
            "passive": ["subfinder"],
            "dns": ["dnsx"],
            "web": ["httpx"],
            "port": ["naabu"],
            "vuln": ["nuclei"],
            "full": ["subfinder", "dnsx", "httpx", "naabu", "nuclei"],
        }
        return phase_tools.get(phase, ["subfinder"])

    @staticmethod
    def _default_analysis(results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Default analysis when LLM unavailable"""
        findings = []
        total_discovered = sum(
            r.get("items_discovered", 0) for r in results.values()
        )

        if total_discovered > 0:
            findings.append(f"Discovered {total_discovered} assets")

        return {
            "findings": findings,
            "gaps": ["Manual validation recommended"],
            "next_tools": [],
            "priority_targets": [],
            "confidence": 0.5,
            "summary": f"Tools executed - {total_discovered} items discovered"
        }

    @staticmethod
    def _create_error_result(tool_name: str, error: str) -> ToolResult:
        """Create error result when tool execution fails"""
        return ToolResult(
            success=False,
            tool_name=tool_name,
            errors=[error]
        )
