"""
LLM integration for reconnaissance agents.
Connects agents to OpenAI/Anthropic for decision-making and tool calling.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseModel):
    """LLM configuration"""
    provider: LLMProvider = LLMProvider.OPENAI
    api_key: str
    model: str = "gpt-4-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30


class ToolDefinition(BaseModel):
    """Tool definition for LLM"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str] = []


class LLMResponse(BaseModel):
    """LLM response with tool calls"""
    content: str
    tool_calls: List[Dict[str, Any]] = []
    reasoning: str = ""
    confidence: float = 0.0


class LLMClient:
    """
    LLM client for reconnaissance decision-making.

    Handles:
    - Tool availability checking and selection
    - Evidence analysis and interpretation
    - Next-step planning based on findings
    - Result aggregation and summarization
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize LLM client based on provider"""
        if self.config.provider == LLMProvider.OPENAI:
            try:
                import openai
                openai.api_key = self.config.api_key
                self.client = openai.OpenAI(api_key=self.config.api_key)
                logger.info("Initialized OpenAI client")
            except ImportError:
                logger.error("OpenAI library not installed: pip install openai")
        elif self.config.provider == LLMProvider.ANTHROPIC:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
                logger.info("Initialized Anthropic client")
            except ImportError:
                logger.error("Anthropic library not installed: pip install anthropic")

    def select_tools(
        self,
        target: str,
        available_tools: Dict[str, Dict[str, str]],
        context: str = ""
    ) -> List[str]:
        """
        Use LLM to select best tools for target.

        Args:
            target: Reconnaissance target (domain, IP, etc.)
            available_tools: Dict of available tools with descriptions
            context: Additional context about the target

        Returns:
            List of tool names to execute
        """
        if not self.client:
            logger.warning("LLM client not initialized, using default tool selection")
            return self._default_tool_selection(target)

        prompt = f"""
You are a reconnaissance expert. Given a target and available tools, select the most relevant tools to execute.

Target: {target}
{f"Context: {context}" if context else ""}

Available tools:
{json.dumps(available_tools, indent=2)}

Consider:
1. What information is needed first (passive before active)
2. Tool dependencies (DNS before HTTP probing)
3. Minimal toolset needed for initial reconnaissance
4. Coverage of attack surface

Return a JSON object with:
{{
    "selected_tools": ["tool1", "tool2", ...],
    "reasoning": "explanation of selection",
    "confidence": 0.0-1.0
}}
"""

        try:
            response = self._call_llm(prompt)
            result = json.loads(response.content)
            return result.get("selected_tools", [])
        except Exception as e:
            logger.error(f"Tool selection failed: {str(e)}")
            return self._default_tool_selection(target)

    def analyze_results(
        self,
        target: str,
        tool_results: Dict[str, Dict[str, Any]],
        available_tools: Dict[str, Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze tool results and suggest next steps.

        Args:
            target: Reconnaissance target
            tool_results: Results from executed tools
            available_tools: Available tools for next phase

        Returns:
            Analysis with recommendations
        """
        if not self.client:
            logger.warning("LLM client not initialized, using default analysis")
            return self._default_analysis(tool_results)

        prompt = f"""
You are a reconnaissance analyst. Analyze the tool execution results and provide insights.

Target: {target}

Tool Results:
{json.dumps(tool_results, indent=2)}

Based on these results:
1. What key findings emerged?
2. What gaps remain in reconnaissance?
3. Which tools should run next?
4. What are the highest-priority targets for deeper analysis?

Return a JSON object with:
{{
    "findings": ["finding1", "finding2", ...],
    "gaps": ["gap1", "gap2", ...],
    "next_tools": ["tool1", "tool2", ...],
    "priority_targets": ["target1", "target2", ...],
    "confidence": 0.0-1.0,
    "summary": "brief executive summary"
}}
"""

        try:
            response = self._call_llm(prompt)
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Results analysis failed: {str(e)}")
            return self._default_analysis(tool_results)

    def generate_report(
        self,
        target: str,
        all_results: Dict[str, Any],
        scan_metadata: Dict[str, Any]
    ) -> str:
        """
        Use LLM to generate reconnaissance report.

        Args:
            target: Reconnaissance target
            all_results: All collected reconnaissance data
            scan_metadata: Scan timing and metadata

        Returns:
            Formatted reconnaissance report
        """
        if not self.client:
            logger.warning("LLM client not initialized, using default report")
            return self._default_report(target, all_results)

        prompt = f"""
You are a penetration testing report writer. Generate a professional reconnaissance report.

Target: {target}

Reconnaissance Data:
{json.dumps(all_results, indent=2, default=str)[:4000]}  # Truncate to fit context

Scan Metadata:
{json.dumps(scan_metadata, indent=2)}

Generate a professional reconnaissance report with:
1. Executive Summary
2. Target Overview
3. Key Findings (organized by category)
4. Attack Surface Analysis
5. Recommendations for Follow-up Testing

Format as clear, professional markdown.
"""

        try:
            response = self._call_llm(prompt, max_tokens=4000)
            return response.content
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return self._default_report(target, all_results)

    def _call_llm(self, prompt: str, max_tokens: Optional[int] = None) -> LLMResponse:
        """Call LLM API"""
        if not self.client:
            raise RuntimeError("LLM client not initialized")

        max_tokens = max_tokens or self.config.max_tokens

        try:
            if self.config.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=max_tokens,
                    timeout=self.config.timeout,
                )
                content = response.choices[0].message.content
            elif self.config.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    timeout=self.config.timeout,
                )
                content = response.content[0].text
            else:
                raise ValueError(f"Unknown provider: {self.config.provider}")

            return LLMResponse(content=content)

        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            raise

    @staticmethod
    def _default_tool_selection(target: str) -> List[str]:
        """Default tool selection when LLM unavailable"""
        # Standard reconnaissance flow
        return [
            "subfinder",      # subdomains first
            "dnsx",           # DNS resolution
            "httpx",          # HTTP probing
            "naabu",          # port scanning
            "nuclei",         # vulnerability detection
        ]

    @staticmethod
    def _default_analysis(results: Dict[str, Any]) -> Dict[str, Any]:
        """Default analysis when LLM unavailable"""
        return {
            "findings": ["Automated reconnaissance completed"],
            "gaps": ["Manual validation recommended"],
            "next_tools": [],
            "priority_targets": [],
            "confidence": 0.5,
            "summary": "Results collected - manual review recommended"
        }

    @staticmethod
    def _default_report(target: str, results: Dict[str, Any]) -> str:
        """Default report when LLM unavailable"""
        return f"""
# Reconnaissance Report: {target}

## Summary
Automated reconnaissance completed.

## Results
{json.dumps(results, indent=2, default=str)[:2000]}

## Recommendations
- Review findings manually
- Validate high-priority targets
- Plan follow-up assessments

*Report generated without LLM analysis - manual review recommended*
"""
