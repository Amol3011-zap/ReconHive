"""
Tool executor - manages tool execution and result collection
"""

from typing import Dict, List, Optional, Type, Any
from uuid import UUID
import logging
import time

from app.tools.base import BaseTool, ToolResult, ToolConfig

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Manages reconnaissance tool execution.

    Responsibilities:
    - Register tools
    - Execute tools against targets
    - Collect and parse results
    - Store execution history
    - Handle errors and retries
    """

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.execution_history: List[Dict[str, Any]] = []

    def register_tool(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.tool_name] = tool
        available, msg = tool.check_availability()
        logger.info(
            f"Registered tool: {tool.tool_name} "
            f"({msg}, {'available' if available else 'not available'})"
        )

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a registered tool by name"""
        return self.tools.get(tool_name)

    def list_tools(self) -> Dict[str, Dict[str, str]]:
        """List all registered tools"""
        tools_list = {}
        for name, tool in self.tools.items():
            available, msg = tool.check_availability()
            tools_list[name] = {
                "description": tool.tool_description,
                "version": tool.tool_version,
                "available": available,
                "status_message": msg,
            }
        return tools_list

    def execute_tool(
        self,
        tool_name: str,
        target: str,
        engagement_id: Optional[UUID] = None,
        scan_id: Optional[UUID] = None,
        **kwargs
    ) -> ToolResult:
        """
        Execute a tool against a target.

        Args:
            tool_name: Name of the tool to execute
            target: Target to scan
            engagement_id: Associated engagement UUID
            scan_id: Associated scan UUID
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with execution details
        """
        start_time = time.time()

        try:
            tool = self.get_tool(tool_name)
            if not tool:
                return ToolResult(
                    success=False,
                    tool_name=tool_name,
                    errors=[f"Tool not found: {tool_name}"],
                )

            # Check availability
            available, msg = tool.check_availability()
            if not available:
                return ToolResult(
                    success=False,
                    tool_name=tool_name,
                    errors=[f"Tool not available: {msg}"],
                )

            logger.info(
                f"Executing tool: {tool_name} against target: {target}",
                extra={"engagement_id": str(engagement_id), "scan_id": str(scan_id)}
            )

            # Execute tool
            result = tool.execute(target, **kwargs)
            result.execution_time = time.time() - start_time

            # Log execution
            self.execution_history.append({
                "tool_name": tool_name,
                "target": target,
                "success": result.success,
                "execution_time": result.execution_time,
                "items_discovered": result.items_discovered,
                "engagement_id": str(engagement_id),
                "scan_id": str(scan_id),
            })

            logger.info(
                f"Tool completed: {tool_name}",
                extra={
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "items_discovered": result.items_discovered,
                }
            )

            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {str(e)}", exc_info=True)
            return ToolResult(
                success=False,
                tool_name=tool_name,
                execution_time=time.time() - start_time,
                errors=[str(e)],
            )

    def get_execution_history(self, tool_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get execution history, optionally filtered by tool"""
        if tool_name:
            return [h for h in self.execution_history if h["tool_name"] == tool_name]
        return self.execution_history

    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get statistics for a tool"""
        executions = self.get_execution_history(tool_name)

        if not executions:
            return {
                "tool_name": tool_name,
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
            }

        successful = sum(1 for e in executions if e["success"])
        total_time = sum(e["execution_time"] for e in executions)
        total_discovered = sum(e["items_discovered"] for e in executions)

        return {
            "tool_name": tool_name,
            "total_executions": len(executions),
            "successful": successful,
            "failed": len(executions) - successful,
            "success_rate": f"{(successful / len(executions) * 100):.1f}%",
            "total_execution_time": total_time,
            "average_execution_time": total_time / len(executions),
            "total_items_discovered": total_discovered,
        }
