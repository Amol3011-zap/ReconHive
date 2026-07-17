"""
Supervisor agent - Orchestrates reconnaissance workflow
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
import logging
import time

from app.recon.agents.base import BaseReconAgent, AgentConfig, AgentResult

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseReconAgent):
    """
    Supervisor agent for orchestrating reconnaissance workflows.

    Responsibilities:
    - Route reconnaissance tasks to appropriate agents
    - Manage workflow execution order
    - Deduplicate discovered assets
    - Aggregate results
    - Track progress
    - Handle retries and failures
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        super().__init__(config)
        self.workflow_steps = [
            "passive_recon",
            "dns_resolution",
            "web_discovery",
            "technology_detection",
            "javascript_analysis",
            "api_discovery",
            "parameter_discovery",
            "content_discovery",
            "cloud_enumeration",
            "network_scanning",
            "vulnerability_validation",
            "evidence_collection",
            "report_generation",
        ]

    @property
    def agent_name(self) -> str:
        return "SupervisorAgent"

    @property
    def agent_description(self) -> str:
        return (
            "Orchestrates multi-agent reconnaissance workflows. "
            "Routes tasks, manages execution, deduplicates results, and aggregates findings."
        )

    def execute(
        self,
        target: str,
        engagement_id: UUID,
        scan_id: UUID,
        workflow: Optional[List[str]] = None,
        **kwargs
    ) -> AgentResult:
        """
        Execute reconnaissance workflow orchestration.

        Args:
            target: Target to scan
            engagement_id: Engagement UUID
            scan_id: Scan UUID
            workflow: Custom workflow steps (uses default if not provided)
            **kwargs: Additional parameters

        Returns:
            AgentResult with workflow status
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not self.validate_target(target):
                return self.create_result(
                    success=False,
                    message=f"Invalid target: {target}",
                    errors=["Target validation failed"]
                )

            # Use custom workflow or default
            workflow_steps = workflow or self.workflow_steps

            self.log_execution(
                "STARTED",
                {
                    "target": target,
                    "engagement_id": str(engagement_id),
                    "scan_id": str(scan_id),
                    "workflow_steps": len(workflow_steps),
                }
            )

            # Simulate workflow orchestration
            # In Phase 4, this will actually dispatch to agents via LangGraph
            results = self._orchestrate_workflow(
                target=target,
                engagement_id=engagement_id,
                scan_id=scan_id,
                workflow_steps=workflow_steps,
                **kwargs
            )

            execution_time = time.time() - start_time

            # Aggregate results
            all_items = sum(r.get("items", 0) for r in results.values())
            all_errors = []
            for r in results.values():
                all_errors.extend(r.get("errors", []))

            return self.create_result(
                success=True,
                message=f"Reconnaissance workflow completed: {len(results)}/{len(workflow_steps)} steps",
                data={
                    "workflow_results": results,
                    "target": target,
                    "total_items_discovered": all_items,
                    "workflow_steps_completed": len(results),
                    "workflow_steps_total": len(workflow_steps),
                },
                execution_time=execution_time,
                next_steps=["Review findings", "Generate report"],
            )

        except Exception as e:
            execution_time = time.time() - start_time
            result = self.handle_error(e, {
                "target": target,
                "engagement_id": str(engagement_id),
                "execution_time": execution_time,
            })
            result.execution_time = execution_time
            return result

    def _orchestrate_workflow(
        self,
        target: str,
        engagement_id: UUID,
        scan_id: UUID,
        workflow_steps: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Orchestrate the reconnaissance workflow.

        In Phase 4, this will dispatch to actual agents.
        For Phase 3, it returns mock results.

        Args:
            target: Target to scan
            engagement_id: Engagement UUID
            scan_id: Scan UUID
            workflow_steps: Steps to execute
            **kwargs: Additional parameters

        Returns:
            Dictionary of results per step
        """
        results = {}

        for step in workflow_steps:
            try:
                self.logger.info(f"Executing workflow step: {step}")

                # Mock result for Phase 3
                # Phase 4 will dispatch to actual agents
                step_result = self._execute_step(
                    step=step,
                    target=target,
                    engagement_id=engagement_id,
                    scan_id=scan_id,
                    **kwargs
                )

                results[step] = step_result
                self.log_execution(
                    "STEP_COMPLETED",
                    {
                        "step": step,
                        "items": step_result.get("items", 0),
                    }
                )

            except Exception as e:
                self.logger.error(f"Step failed: {step} - {str(e)}")
                results[step] = {
                    "success": False,
                    "items": 0,
                    "errors": [str(e)],
                }

        return results

    def _execute_step(
        self,
        step: str,
        target: str,
        engagement_id: UUID,
        scan_id: UUID,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step.

        In Phase 4, this dispatches to actual agents via LangGraph.
        For Phase 3, returns mock results.

        Args:
            step: Workflow step name
            target: Target to scan
            engagement_id: Engagement UUID
            scan_id: Scan UUID
            **kwargs: Additional parameters

        Returns:
            Step result dictionary
        """
        # Mock results for each step (Phase 3)
        # Phase 4 will replace with actual agent execution

        mock_results = {
            "passive_recon": {
                "success": True,
                "items": 5,
                "errors": [],
                "discoveries": {
                    "subdomains": 3,
                    "historical_hosts": 2,
                }
            },
            "dns_resolution": {
                "success": True,
                "items": 5,
                "errors": [],
                "discoveries": {
                    "a_records": 3,
                    "cname_records": 2,
                }
            },
            "web_discovery": {
                "success": True,
                "items": 10,
                "errors": [],
                "discoveries": {
                    "endpoints": 8,
                    "redirects": 2,
                }
            },
            "technology_detection": {
                "success": True,
                "items": 7,
                "errors": [],
                "discoveries": {
                    "web_servers": 1,
                    "frameworks": 3,
                    "libraries": 3,
                }
            },
            "javascript_analysis": {
                "success": True,
                "items": 12,
                "errors": [],
                "discoveries": {
                    "api_endpoints": 5,
                    "secrets": 0,
                    "hostnames": 7,
                }
            },
            "api_discovery": {
                "success": True,
                "items": 2,
                "errors": [],
                "discoveries": {
                    "rest_apis": 1,
                    "graphql_endpoints": 1,
                }
            },
            "parameter_discovery": {
                "success": True,
                "items": 8,
                "errors": [],
                "discoveries": {
                    "query_params": 5,
                    "body_params": 3,
                }
            },
            "content_discovery": {
                "success": True,
                "items": 15,
                "errors": [],
                "discoveries": {
                    "directories": 10,
                    "files": 5,
                }
            },
            "cloud_enumeration": {
                "success": True,
                "items": 1,
                "errors": [],
                "discoveries": {
                    "s3_buckets": 1,
                }
            },
            "network_scanning": {
                "success": True,
                "items": 20,
                "errors": [],
                "discoveries": {
                    "open_ports": 5,
                    "services": 5,
                }
            },
            "vulnerability_validation": {
                "success": True,
                "items": 3,
                "errors": [],
                "discoveries": {
                    "critical": 1,
                    "high": 2,
                }
            },
            "evidence_collection": {
                "success": True,
                "items": 50,
                "errors": [],
                "discoveries": {
                    "screenshots": 20,
                    "responses": 30,
                }
            },
            "report_generation": {
                "success": True,
                "items": 1,
                "errors": [],
                "discoveries": {
                    "executive_summary": 1,
                }
            },
        }

        return mock_results.get(step, {
            "success": False,
            "items": 0,
            "errors": [f"Unknown step: {step}"],
        })

    def get_workflow_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get dependencies between workflow steps.

        Returns:
            Dictionary mapping steps to their dependencies
        """
        return {
            "passive_recon": [],
            "dns_resolution": ["passive_recon"],
            "web_discovery": ["dns_resolution"],
            "technology_detection": ["web_discovery"],
            "javascript_analysis": ["web_discovery"],
            "api_discovery": ["web_discovery"],
            "parameter_discovery": ["api_discovery"],
            "content_discovery": ["web_discovery"],
            "cloud_enumeration": ["passive_recon"],
            "network_scanning": ["passive_recon"],
            "vulnerability_validation": [
                "web_discovery",
                "technology_detection",
                "parameter_discovery",
            ],
            "evidence_collection": [
                "web_discovery",
                "technology_detection",
                "javascript_analysis",
                "api_discovery",
            ],
            "report_generation": [
                "evidence_collection",
                "vulnerability_validation",
            ],
        }

    def get_optimal_workflow_order(self) -> List[str]:
        """
        Calculate optimal workflow execution order based on dependencies.

        Returns:
            Ordered list of workflow steps
        """
        # Topological sort of workflow steps
        dependencies = self.get_workflow_dependency_graph()
        ordered = []
        remaining = set(dependencies.keys())

        while remaining:
            # Find steps with no remaining dependencies
            available = [
                step for step in remaining
                if not any(
                    dep in remaining
                    for dep in dependencies.get(step, [])
                )
            ]

            if not available:
                # Cycle detected
                break

            # Sort alphabetically for consistency
            available.sort()
            ordered.extend(available)
            remaining -= set(available)

        return ordered
