"""
LangGraph-based reconnaissance workflow orchestration

This module integrates LangGraph for multi-agent coordination and workflow management.
Phase 3 focuses on the core architecture and agent routing.
Phase 4 will add real LLM-based decision making.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowState:
    """State for a running workflow"""
    workflow_id: str
    scan_id: UUID
    engagement_id: UUID
    target: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    total_steps: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress_percent: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "scan_id": str(self.scan_id),
            "engagement_id": str(self.engagement_id),
            "target": self.target,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "results": self.results,
            "errors": self.errors,
            "progress_percent": self.progress_percent,
            "metadata": self.metadata,
        }


class ReconGraph:
    """
    LangGraph-based reconnaissance workflow graph.

    Phase 3: Core architecture and agent routing
    Phase 4: Real LLM-based conditional routing
    Phase 5: Multi-agent collaboration and optimization
    """

    def __init__(self):
        self.agents: Dict[str, Callable] = {}
        self.edges: Dict[str, List[str]] = {}
        self.conditions: Dict[Tuple[str, str], Callable] = {}
        self.entry_point: Optional[str] = None

    def add_agent(self, name: str, agent: Callable):
        """Register an agent in the graph"""
        self.agents[name] = agent
        self.edges[name] = []
        logger.info(f"Added agent: {name}")

    def add_edge(self, from_agent: str, to_agent: str):
        """Add a directed edge between agents"""
        if from_agent not in self.edges:
            self.edges[from_agent] = []
        self.edges[from_agent].append(to_agent)
        logger.info(f"Added edge: {from_agent} -> {to_agent}")

    def add_conditional_edge(
        self,
        from_agent: str,
        condition: Callable[[Dict[str, Any]], str],
        mapping: Dict[str, str]
    ):
        """
        Add conditional routing between agents.

        Args:
            from_agent: Source agent
            condition: Function that determines which edge to take
            mapping: Maps condition return value to target agent
        """
        self.conditions[(from_agent, "condition")] = (condition, mapping)
        logger.info(f"Added conditional edge from {from_agent}")

    def set_entry_point(self, agent_name: str):
        """Set the starting agent"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not registered")
        self.entry_point = agent_name
        logger.info(f"Set entry point: {agent_name}")

    def get_next_agents(self, current_agent: str, state: Dict[str, Any]) -> List[str]:
        """
        Determine next agents to execute.

        Phase 3: Simple deterministic routing
        Phase 4: LLM-based conditional routing

        Args:
            current_agent: Current agent name
            state: Current workflow state

        Returns:
            List of next agents to execute
        """
        next_agents = []

        # Check conditional edges first (Phase 4 feature)
        if (current_agent, "condition") in self.conditions:
            condition, mapping = self.conditions[(current_agent, "condition")]
            try:
                result = condition(state)
                if result in mapping:
                    next_agents.append(mapping[result])
            except Exception as e:
                logger.warning(f"Conditional edge failed: {str(e)}")

        # Fall back to standard edges
        if not next_agents:
            next_agents = self.edges.get(current_agent, [])

        return next_agents

    def execute(
        self,
        state: WorkflowState,
        max_iterations: int = 100
    ) -> WorkflowState:
        """
        Execute the reconnaissance workflow graph.

        Phase 3: Sequential execution with mock results
        Phase 4: Conditional routing based on results
        Phase 5: Parallel execution with dependencies

        Args:
            state: Initial workflow state
            max_iterations: Max steps before timeout

        Returns:
            Final workflow state with results
        """
        if not self.entry_point:
            state.errors.append("No entry point set")
            state.status = WorkflowStatus.FAILED
            return state

        state.status = WorkflowStatus.RUNNING
        executed_agents = []
        current = self.entry_point
        iteration = 0

        while current and iteration < max_iterations:
            iteration += 1

            # Execute agent
            if current not in self.agents:
                state.errors.append(f"Agent not found: {current}")
                break

            try:
                logger.info(f"Executing agent: {current}")
                agent = self.agents[current]
                result = agent(state=state)

                # Store result
                state.results[current] = result
                executed_agents.append(current)

                # Update progress
                state.current_step += 1
                state.progress_percent = int(
                    (state.current_step / max(state.total_steps, 1)) * 100
                )

                # Get next agents
                next_agents = self.get_next_agents(current, state.to_dict())
                if next_agents:
                    current = next_agents[0]  # Phase 3: Sequential
                else:
                    current = None  # End of workflow

            except Exception as e:
                logger.error(f"Agent execution failed: {current} - {str(e)}")
                state.errors.append(f"{current}: {str(e)}")
                # Try to continue with next agent in queue
                next_agents = self.get_next_agents(current, state.to_dict())
                current = next_agents[0] if next_agents else None

        # Finalize state
        if current or iteration >= max_iterations:
            state.status = WorkflowStatus.FAILED
        else:
            state.status = WorkflowStatus.COMPLETED

        logger.info(f"Workflow completed: {len(executed_agents)} agents executed")
        return state

    def to_dict(self) -> Dict[str, Any]:
        """Export graph structure"""
        return {
            "agents": list(self.agents.keys()),
            "edges": self.edges,
            "entry_point": self.entry_point,
            "total_agents": len(self.agents),
            "total_edges": sum(len(e) for e in self.edges.values()),
        }


class DefaultReconGraph(ReconGraph):
    """
    Default reconnaissance graph with all agents connected.

    Execution order (Phase 3):
    1. Passive Recon (entry point)
    2. DNS Resolution
    3. Web Discovery
    4. Technology Detection + JavaScript Analysis (parallel in Phase 5)
    5. API Discovery
    6. Parameter Discovery
    7. Content Discovery
    8. Cloud Discovery
    9. Network Scanning
    10. Vulnerability Validation
    11. Evidence Collection
    12. Report Generation
    """

    def __init__(self):
        super().__init__()

        # Import agents (Phase 4 will use actual agent instances)
        from app.recon.agents.supervisor import SupervisorAgent
        from app.recon.agents.agents import (
            PassiveReconAgent, DNSAgent, WebDiscoveryAgent,
            TechnologyAgent, JavaScriptAgent, APIDiscoveryAgent,
            ParameterDiscoveryAgent, ContentDiscoveryAgent,
            CloudDiscoveryAgent, NetworkAgent, VulnerabilityAgent,
            EvidenceAgent, ReportAgent
        )

        # Create agent instances
        self.supervisor = SupervisorAgent()
        self.passive_recon = PassiveReconAgent()
        self.dns = DNSAgent()
        self.web = WebDiscoveryAgent()
        self.tech = TechnologyAgent()
        self.js = JavaScriptAgent()
        self.api = APIDiscoveryAgent()
        self.params = ParameterDiscoveryAgent()
        self.content = ContentDiscoveryAgent()
        self.cloud = CloudDiscoveryAgent()
        self.network = NetworkAgent()
        self.vuln = VulnerabilityAgent()
        self.evidence = EvidenceAgent()
        self.report = ReportAgent()

        # Register agents
        self.add_agent("supervisor", self._supervisor_wrapper)
        self.add_agent("passive_recon", self._agent_wrapper(self.passive_recon))
        self.add_agent("dns", self._agent_wrapper(self.dns))
        self.add_agent("web_discovery", self._agent_wrapper(self.web))
        self.add_agent("technology", self._agent_wrapper(self.tech))
        self.add_agent("javascript", self._agent_wrapper(self.js))
        self.add_agent("api_discovery", self._agent_wrapper(self.api))
        self.add_agent("parameter_discovery", self._agent_wrapper(self.params))
        self.add_agent("content_discovery", self._agent_wrapper(self.content))
        self.add_agent("cloud_discovery", self._agent_wrapper(self.cloud))
        self.add_agent("network", self._agent_wrapper(self.network))
        self.add_agent("vulnerability", self._agent_wrapper(self.vuln))
        self.add_agent("evidence", self._agent_wrapper(self.evidence))
        self.add_agent("report", self._agent_wrapper(self.report))

        # Add edges (execution order)
        self.add_edge("supervisor", "passive_recon")
        self.add_edge("passive_recon", "dns")
        self.add_edge("dns", "web_discovery")
        self.add_edge("web_discovery", "technology")
        self.add_edge("web_discovery", "javascript")
        self.add_edge("web_discovery", "api_discovery")
        self.add_edge("web_discovery", "content_discovery")
        self.add_edge("passive_recon", "cloud_discovery")
        self.add_edge("passive_recon", "network")
        self.add_edge("api_discovery", "parameter_discovery")
        self.add_edge("technology", "vulnerability")
        self.add_edge("javascript", "vulnerability")
        self.add_edge("content_discovery", "vulnerability")
        self.add_edge("network", "vulnerability")
        self.add_edge("vulnerability", "evidence")
        self.add_edge("evidence", "report")

        # Set entry point
        self.set_entry_point("supervisor")

    def _agent_wrapper(self, agent):
        """Wrap agent for graph execution"""
        def wrapper(state: WorkflowState) -> Dict[str, Any]:
            result = agent.execute(
                target=state.target,
                engagement_id=state.engagement_id,
                scan_id=state.scan_id,
            )
            return result.to_dict()
        return wrapper

    def _supervisor_wrapper(self, state: WorkflowState) -> Dict[str, Any]:
        """Supervisor agent wrapper"""
        result = self.supervisor.execute(
            target=state.target,
            engagement_id=state.engagement_id,
            scan_id=state.scan_id,
        )
        return result.to_dict()
