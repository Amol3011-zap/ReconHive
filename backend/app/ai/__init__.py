"""AI Orchestration Layer for ReconHive

This module provides LangChain/LangGraph integration for:
- Supervisor agent routing
- Specialized agents (Recon, Findings, Reports, AI Security)
- Vector search via pgvector
- Conversation management
- Summary generation
"""

from .agents.supervisor import SupervisorAgent

__all__ = ["SupervisorAgent"]
