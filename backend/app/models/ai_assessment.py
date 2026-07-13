from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum, Index, Integer, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid
from app.db.base import Base

class AITargetType(PyEnum):
    LLM_MODEL = "llm_model"
    RAG_SYSTEM = "rag_system"
    AI_AGENT = "ai_agent"
    PROMPT_INJECTION_VECTOR = "prompt_injection_vector"
    TOOL_INTEGRATION = "tool_integration"
    MCP_SERVER = "mcp_server"

class AIAssessmentType(PyEnum):
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    SYSTEM_PROMPT_LEAKAGE = "system_prompt_leakage"
    RAG_POISONING = "rag_poisoning"
    TOOL_MISUSE = "tool_misuse"
    MCP_EXPLOITATION = "mcp_exploitation"
    AGENT_CAPABILITY = "agent_capability"
    MEMORY_EXPLOITATION = "memory_exploitation"
    DATA_EXFILTRATION = "data_exfiltration"
    EXCESSIVE_AGENCY = "excessive_agency"
    MODEL_THEFT = "model_theft"

class AISeverity(PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AITarget(Base):
    __tablename__ = "ai_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    target_type = Column(Enum(AITargetType), nullable=False, index=True)

    # AI Target Details
    model_name = Column(String(255))  # e.g., "Claude 3.5 Sonnet"
    model_provider = Column(String(255))  # e.g., "Anthropic"
    api_endpoint = Column(String(500))

    # RAG System Details
    rag_type = Column(String(100))  # e.g., "vector_db", "traditional_search"
    knowledge_base_size = Column(Integer)  # Number of documents

    # Agent Details
    agent_framework = Column(String(255))  # e.g., "Claude Agent SDK", "LangChain"
    available_tools = Column(JSONB, default=[])
    max_iterations = Column(Integer)

    # MCP Details
    mcp_server_url = Column(String(500))
    mcp_protocols = Column(JSONB, default=[])

    custom_metadata = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="ai_targets")
    ai_assessments = relationship("AIAssessment", back_populates="ai_target", cascade="all, delete-orphan")
    ai_findings = relationship("AIFinding", back_populates="ai_target")

    __table_args__ = (
        Index("ix_ai_targets_engagement_id", "engagement_id"),
        Index("ix_ai_targets_type", "target_type"),
        Index("ix_ai_targets_model", "model_name"),
    )

class AIAssessment(Base):
    __tablename__ = "ai_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_target_id = Column(UUID(as_uuid=True), ForeignKey("ai_targets.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="SET NULL"), index=True)

    name = Column(String(255), nullable=False)
    assessment_type = Column(Enum(AIAssessmentType), nullable=False, index=True)
    description = Column(Text)

    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed
    progress_percent = Column(Integer, default=0)

    # Test parameters
    test_parameters = Column(JSONB, default={})
    prompts_tested = Column(Integer, default=0)
    payloads_tried = Column(Integer, default=0)

    # Results
    findings_count = Column(Integer, default=0)
    vulnerabilities_discovered = Column(Integer, default=0)

    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Analysis
    risk_score = Column(Float)  # 0-100
    remediation_priority = Column(String(50))

    methodology = Column(String(255))  # e.g., "OWASP LLM Top 10", "ATT&CK"

    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="ai_assessments")
    ai_target = relationship("AITarget", back_populates="ai_assessments")
    scan = relationship("Scan")
    ai_findings = relationship("AIFinding", back_populates="ai_assessment", cascade="all, delete-orphan")
    prompt_tests = relationship("PromptTest", back_populates="ai_assessment", cascade="all, delete-orphan")
    rag_tests = relationship("RAGTest", back_populates="ai_assessment", cascade="all, delete-orphan")
    tool_tests = relationship("ToolTest", back_populates="ai_assessment", cascade="all, delete-orphan")
    ai_evidence = relationship("AIEvidence", back_populates="ai_assessment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_ai_assessments_engagement_id", "engagement_id"),
        Index("ix_ai_assessments_target_id", "ai_target_id"),
        Index("ix_ai_assessments_type", "assessment_type"),
        Index("ix_ai_assessments_status", "status"),
    )

class AIFinding(Base):
    __tablename__ = "ai_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_target_id = Column(UUID(as_uuid=True), ForeignKey("ai_targets.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_assessment_id = Column(UUID(as_uuid=True), ForeignKey("ai_assessments.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(Enum(AISeverity), nullable=False, index=True)
    status = Column(String(50), default="open", nullable=False, index=True)

    # Framework Mapping
    owasp_llm_category = Column(String(255), index=True)  # e.g., "LLM01:Prompt Injection"
    owasp_agentic_category = Column(String(255), index=True)  # e.g., "Excessive Agency"
    mitre_technique = Column(String(255), index=True)  # e.g., "T1610 - Code Execution"
    attack_phase = Column(String(255), index=True)  # e.g., "Initial Access", "Privilege Escalation"

    # Technical Details
    attack_vector = Column(String(255))  # e.g., "Direct Prompt Injection"
    attack_description = Column(Text)

    # Impact Assessment
    impact = Column(Text)
    affected_capabilities = Column(JSONB, default=[])
    data_at_risk = Column(JSONB, default=[])

    # Proof of Concept
    poc_payload = Column(Text)  # The actual prompt/input that triggered the vulnerability
    poc_output = Column(Text)  # The model's response showing the vulnerability
    poc_screenshot = Column(String(500))  # Path to evidence screenshot

    # Remediation
    remediation = Column(Text)
    remediation_difficulty = Column(String(50))  # easy, medium, hard
    estimated_effort = Column(String(100))

    # Evidence
    evidence_ids = Column(JSON)
    references = Column(JSON)
    cve_references = Column(JSON)

    # Risk Scoring
    risk_score = Column(Float)  # 0-100
    exploitability = Column(String(50))  # low, medium, high, critical

    detected_by = Column(String(255))
    verified_by = Column(String(255))
    verified_at = Column(DateTime)

    created_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement")
    ai_target = relationship("AITarget", back_populates="ai_findings")
    ai_assessment = relationship("AIAssessment", back_populates="ai_findings")
    ai_evidence = relationship("AIEvidence", back_populates="ai_finding")

    __table_args__ = (
        Index("ix_ai_findings_engagement_id", "engagement_id"),
        Index("ix_ai_findings_target_id", "ai_target_id"),
        Index("ix_ai_findings_assessment_id", "ai_assessment_id"),
        Index("ix_ai_findings_severity", "severity"),
        Index("ix_ai_findings_owasp", "owasp_llm_category"),
        Index("ix_ai_findings_mitre", "mitre_technique"),
    )

class AIEvidence(Base):
    __tablename__ = "ai_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    engagement_id = Column(UUID(as_uuid=True), ForeignKey("engagements.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_assessment_id = Column(UUID(as_uuid=True), ForeignKey("ai_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    ai_finding_id = Column(UUID(as_uuid=True), ForeignKey("ai_findings.id", ondelete="CASCADE"), index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)
    evidence_type = Column(String(100), nullable=False, index=True)  # prompt, response, log, screenshot, conversation

    # Evidence Data
    prompt_input = Column(Text)  # The input that triggered the finding
    model_response = Column(Text)  # The model's response
    system_prompt_fragment = Column(Text)  # Any exposed system prompt

    conversation_log = Column(JSONB)  # Full conversation history
    custom_metadata = Column(JSONB)

    # File References
    file_path = Column(String(500))
    file_size = Column(String(50))
    mime_type = Column(String(100))

    # Timestamps
    test_timestamp = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement")
    ai_assessment = relationship("AIAssessment", back_populates="ai_evidence")
    ai_finding = relationship("AIFinding", back_populates="ai_evidence")

    __table_args__ = (
        Index("ix_ai_evidence_engagement_id", "engagement_id"),
        Index("ix_ai_evidence_assessment_id", "ai_assessment_id"),
        Index("ix_ai_evidence_type", "evidence_type"),
    )

class PromptTest(Base):
    __tablename__ = "prompt_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_assessment_id = Column(UUID(as_uuid=True), ForeignKey("ai_assessments.id", ondelete="CASCADE"), nullable=False, index=True)

    test_name = Column(String(255), nullable=False)
    test_category = Column(String(100))  # jailbreak, injection, extraction, evasion

    # Prompt Details
    prompt_template = Column(Text, nullable=False)
    prompt_parameters = Column(JSONB, default={})

    # Execution
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    result = Column(Text)
    success = Column(Boolean, default=False)

    # Analysis
    injection_detected = Column(Boolean, default=False)
    jailbreak_successful = Column(Boolean, default=False)
    system_prompt_leaked = Column(Boolean, default=False)

    risk_level = Column(String(50))  # low, medium, high, critical

    executed_at = Column(DateTime)
    execution_time_ms = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ai_assessment = relationship("AIAssessment", back_populates="prompt_tests")

    __table_args__ = (
        Index("ix_prompt_tests_assessment_id", "ai_assessment_id"),
        Index("ix_prompt_tests_category", "test_category"),
    )

class RAGTest(Base):
    __tablename__ = "rag_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_assessment_id = Column(UUID(as_uuid=True), ForeignKey("ai_assessments.id", ondelete="CASCADE"), nullable=False, index=True)

    test_name = Column(String(255), nullable=False)
    test_type = Column(String(100))  # poisoning, extraction, inference, privacy

    # Test Parameters
    query = Column(Text, nullable=False)
    expected_knowledge_base_data = Column(Text)
    sensitive_data_present = Column(Boolean, default=False)

    # Results
    retrieved_documents = Column(JSONB, default=[])
    model_response = Column(Text)

    # Analysis
    knowledge_base_leak = Column(Boolean, default=False)
    sensitive_data_exposed = Column(Boolean, default=False)
    poisoning_successful = Column(Boolean, default=False)

    risk_level = Column(String(50))

    executed_at = Column(DateTime)
    execution_time_ms = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ai_assessment = relationship("AIAssessment", back_populates="rag_tests")

    __table_args__ = (
        Index("ix_rag_tests_assessment_id", "ai_assessment_id"),
        Index("ix_rag_tests_type", "test_type"),
    )

class ToolTest(Base):
    __tablename__ = "tool_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_assessment_id = Column(UUID(as_uuid=True), ForeignKey("ai_assessments.id", ondelete="CASCADE"), nullable=False, index=True)

    test_name = Column(String(255), nullable=False)
    tool_name = Column(String(255), nullable=False, index=True)
    tool_type = Column(String(100))  # file_operations, network, execution, credential

    # Test Details
    tool_specification = Column(JSONB)  # Tool schema/definition
    attempted_misuse = Column(Text)  # Description of misuse attempt

    # Execution
    status = Column(String(50), default="pending")
    result = Column(Text)

    # Analysis
    tool_misuse_detected = Column(Boolean, default=False)
    excessive_agency_found = Column(Boolean, default=False)
    unintended_execution = Column(Boolean, default=False)
    security_boundary_crossed = Column(Boolean, default=False)

    risk_level = Column(String(50))

    executed_at = Column(DateTime)
    execution_time_ms = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ai_assessment = relationship("AIAssessment", back_populates="tool_tests")

    __table_args__ = (
        Index("ix_tool_tests_assessment_id", "ai_assessment_id"),
        Index("ix_tool_tests_tool_name", "tool_name"),
        Index("ix_tool_tests_type", "tool_type"),
    )
