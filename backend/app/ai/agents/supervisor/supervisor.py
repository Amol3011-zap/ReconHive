"""LangGraph Supervisor Agent - Routes requests to specialized agents"""

import json
import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

class SupervisorAgent:
    """Routes user requests to appropriate agents"""

    AGENT_NAMES = ["recon", "findings", "reports", "ai_security"]

    ROUTING_RULES = {
        # Keywords that route to Recon Agent
        "recon": ["asset", "scan", "technology", "service", "attack surface", "inventory"],
        # Keywords that route to Findings Agent
        "findings": ["finding", "severity", "cvss", "vulnerability", "remediation", "impact"],
        # Keywords that route to Report Agent
        "reports": ["summary", "executive", "technical", "report", "overview"],
        # Keywords that route to AI Security Agent
        "ai_security": ["owasp llm", "mitre att&ck", "prompt injection", "rag", "jailbreak", "ai security", "llm"]
    }

    async def route(self, user_message: str) -> dict:
        """
        Route a user message to the appropriate agent.

        Args:
            user_message: The user's request

        Returns:
            Dict with agent name, reasoning, and request
        """
        message_lower = user_message.lower()

        # Find matching agent based on keywords
        agent_scores = {agent: 0 for agent in self.AGENT_NAMES}

        for agent, keywords in self.ROUTING_RULES.items():
            for keyword in keywords:
                if keyword in message_lower:
                    agent_scores[agent] += 1

        # Get agent with highest score
        best_agent = max(agent_scores, key=agent_scores.get)

        # If no clear match, default to reports (general summaries)
        if agent_scores[best_agent] == 0:
            best_agent = "reports"

        return {
            "agent": best_agent,
            "reasoning": f"User message contains keywords matching {best_agent} agent",
            "request": user_message,
            "confidence": agent_scores[best_agent] / max(1, sum(agent_scores.values()))
        }


class ReconAgent:
    """Recon Agent - Summarizes assets, scans, and technologies"""

    async def process(self, engagement_data: dict, query: str) -> str:
        """
        Process reconnaissance request.

        Args:
            engagement_data: Data about the engagement
            query: User's query

        Returns:
            Summary text
        """
        # This is MOCKED for Phase 1
        # In production, this would query the database and use an LLM

        summary = f"""
## Reconnaissance Summary

**Assets:** {engagement_data.get('asset_count', 0)} total
- Web Applications: {engagement_data.get('web_apps', 0)}
- Servers: {engagement_data.get('servers', 0)}
- Network Infrastructure: {engagement_data.get('network_devices', 0)}

**Scans Completed:** {engagement_data.get('scans_completed', 0)}
- Web Scans: {engagement_data.get('web_scans', 0)}
- Network Scans: {engagement_data.get('network_scans', 0)}

**Technologies Discovered:**
- Frameworks: {engagement_data.get('frameworks', [])}
- Databases: {engagement_data.get('databases', [])}
- Services: {engagement_data.get('services', [])}

**Attack Surface:** {engagement_data.get('attack_surface', 'MEDIUM')}
"""
        return summary.strip()


class FindingsAgent:
    """Findings Agent - Analyzes and summarizes security findings"""

    async def process(self, findings_data: dict, query: str) -> str:
        """
        Process findings request.

        Args:
            findings_data: Data about findings
            query: User's query

        Returns:
            Analysis text
        """
        # This is MOCKED for Phase 1

        summary = f"""
## Findings Summary

**Critical Findings:** {findings_data.get('critical', 0)}
- Avg CVSS: 9.2
- Most Common: {findings_data.get('top_critical', 'Not Found')}

**High Findings:** {findings_data.get('high', 0)}
- Avg CVSS: 7.5
- Most Common: {findings_data.get('top_high', 'Invalid Credentials')}

**Medium Findings:** {findings_data.get('medium', 0)}
**Low Findings:** {findings_data.get('low', 0)}

**Total Risk Score:** {findings_data.get('risk_score', 6.5)}/10.0

**Remediation Priority:**
1. Fix critical findings (patch immediately)
2. Address high findings (within 30 days)
3. Medium findings (within 90 days)
"""
        return summary.strip()


class ReportAgent:
    """Report Agent - Generates summaries for different audiences"""

    async def process(self, engagement_data: dict, query: str, audience: str = "executive") -> str:
        """
        Generate a report.

        Args:
            engagement_data: Engagement context
            query: User's request
            audience: Target audience (executive, technical, manager)

        Returns:
            Report text
        """
        # This is MOCKED for Phase 1

        if "executive" in query.lower():
            return self._executive_summary(engagement_data)
        elif "technical" in query.lower():
            return self._technical_summary(engagement_data)
        else:
            return self._executive_summary(engagement_data)

    def _executive_summary(self, data: dict) -> str:
        return f"""
## Executive Summary

This engagement assessed {data.get('asset_count', 0)} assets across the organization's attack surface.

**Key Findings:**
- {data.get('critical', 0)} critical risks require immediate attention
- {data.get('high', 0)} high-risk items need remediation within 30 days
- Overall risk score: {data.get('risk_score', 6.5)}/10.0 (HIGH)

**Recommended Actions:**
1. Patch critical vulnerabilities immediately
2. Implement WAF rules for web application threats
3. Enforce strong authentication across all systems
4. Establish regular scanning schedule

**Timeline:** 90 days for full remediation
"""

    def _technical_summary(self, data: dict) -> str:
        return f"""
## Technical Summary

Assessment of {data.get('asset_count', 0)} assets identified {data.get('total_findings', 0)} findings.

**Findings by Severity:**
- CRITICAL: {data.get('critical', 0)} (CVSS 9.0+)
- HIGH: {data.get('high', 0)} (CVSS 7.0-8.9)
- MEDIUM: {data.get('medium', 0)} (CVSS 4.0-6.9)
- LOW: {data.get('low', 0)} (CVSS 0.1-3.9)

**Technologies:**
- {len(data.get('frameworks', []))} distinct frameworks
- {len(data.get('databases', []))} database systems
- {len(data.get('services', []))} exposed services

**Remediation Effort:** {data.get('remediation_effort', 'MEDIUM')}
"""


class AISecurityAgent:
    """AI Security Agent - Maps findings to frameworks"""

    async def process(self, findings: dict, query: str) -> str:
        """
        Map findings to AI security frameworks.

        Args:
            findings: Security findings
            query: User's request

        Returns:
            Framework mapping text
        """
        # This is MOCKED for Phase 1

        return f"""
## AI Security Mapping

**OWASP LLM Top 10:**
- LLM01 (Prompt Injection): {findings.get('prompt_injection', 'Not Found')}
- LLM06 (Sensitive Information Disclosure): {findings.get('info_disclosure', 'Not Found')}

**MITRE ATT&CK AI:**
- Reconnaissance: Model Enumeration
- Execution: Prompt Injection
- Exfiltration: Training Data Extraction

**Red Team Phases:**
- Reconnaissance ✓
- Initial Access ✓
- Execution (Pending)

**Risk Assessment:** MEDIUM-HIGH

**Defensive Controls:**
1. Implement prompt validation
2. Rate limit API endpoints
3. Monitor for injection attempts
4. Encrypt sensitive data
"""
