# AI Security Database Schema

**Purpose**: Complete database schema for AI security assessment module  
**Database**: PostgreSQL 15+  
**Version**: 1.0

---

## Table: ai_targets

Stores AI systems being tested.

```sql
CREATE TABLE ai_targets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    
    -- Identification
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_type VARCHAR(50) NOT NULL,  -- llm_model, rag_system, ai_agent, tool_integration, mcp_server
    
    -- LLM Target Details
    model_name VARCHAR(255),  -- e.g., "Claude 3.5 Sonnet", "GPT-4o"
    model_provider VARCHAR(255),  -- e.g., "Anthropic", "OpenAI"
    model_version VARCHAR(100),
    api_endpoint VARCHAR(500),
    api_authentication_type VARCHAR(100),  -- api_key, oauth, azure_ad
    
    -- RAG System Details
    rag_type VARCHAR(100),  -- vector_db, traditional_search, hybrid
    knowledge_base_size INTEGER,  -- Number of documents
    vector_db_name VARCHAR(255),  -- e.g., "Pinecone", "Weaviate"
    knowledge_sources JSONB,  -- Source data locations
    
    -- Agent Details
    agent_framework VARCHAR(255),  -- LangChain, Claude Agent SDK, AutoGPT
    available_tools JSONB,  -- List of tool names/descriptions
    max_iterations INTEGER,
    autonomy_level VARCHAR(50),  -- supervised, semi_autonomous, autonomous
    
    -- MCP Details
    mcp_server_url VARCHAR(500),
    mcp_protocols JSONB,  -- Supported protocols/versions
    
    -- Tool Integration Details
    tool_type VARCHAR(100),  -- file_operations, network, execution, data_access
    tool_permissions JSONB,
    
    -- General Metadata
    metadata JSONB,
    criticality VARCHAR(50),  -- critical, high, medium, low
    data_classification VARCHAR(50),  -- public, internal, confidential, restricted
    
    -- Lifecycle
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT ai_targets_engagement_id_idx FOREIGN KEY (engagement_id) REFERENCES engagements(id),
    INDEX ix_ai_targets_engagement_id (engagement_id),
    INDEX ix_ai_targets_type (target_type),
    INDEX ix_ai_targets_model (model_name)
);
```

---

## Table: ai_assessments

Tracks AI security assessment progress and results.

```sql
CREATE TABLE ai_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    ai_target_id UUID NOT NULL REFERENCES ai_targets(id) ON DELETE CASCADE,
    scan_id UUID REFERENCES scans(id) ON DELETE SET NULL,
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    assessment_type VARCHAR(50) NOT NULL,  -- prompt_injection, jailbreak, rag_poisoning, etc.
    methodology VARCHAR(255),  -- OWASP LLM Top 10, MITRE ATT&CK, Red Team Phases
    
    -- Status & Progress
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    progress_percent INTEGER DEFAULT 0,
    
    -- Test Parameters
    test_parameters JSONB DEFAULT '{}',
    
    -- Results
    prompts_tested INTEGER DEFAULT 0,
    payloads_tried INTEGER DEFAULT 0,
    findings_count INTEGER DEFAULT 0,
    vulnerabilities_discovered INTEGER DEFAULT 0,
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Analysis
    risk_score FLOAT,  -- 0-100
    remediation_priority VARCHAR(50),  -- critical, high, medium, low
    
    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ai_assessments_engagement_fk FOREIGN KEY (engagement_id) REFERENCES engagements(id),
    CONSTRAINT ai_assessments_target_fk FOREIGN KEY (ai_target_id) REFERENCES ai_targets(id),
    INDEX ix_ai_assessments_engagement_id (engagement_id),
    INDEX ix_ai_assessments_target_id (ai_target_id),
    INDEX ix_ai_assessments_type (assessment_type),
    INDEX ix_ai_assessments_status (status)
);
```

---

## Table: ai_findings

AI security vulnerabilities discovered during assessments.

```sql
CREATE TABLE ai_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    ai_target_id UUID NOT NULL REFERENCES ai_targets(id) ON DELETE CASCADE,
    ai_assessment_id UUID NOT NULL REFERENCES ai_assessments(id) ON DELETE CASCADE,
    
    -- Identification
    title VARCHAR(500) NOT NULL,
    description TEXT,
    
    -- Severity & Status
    severity VARCHAR(50) NOT NULL,  -- critical, high, medium, low, info
    status VARCHAR(50) DEFAULT 'open',  -- open, triaged, remediated, accepted_risk, false_positive
    
    -- Framework Mapping
    owasp_llm_category VARCHAR(255),  -- e.g., "LLM01:Prompt Injection"
    owasp_agentic_category VARCHAR(255),  -- e.g., "Excessive Agency"
    mitre_technique VARCHAR(255),  -- e.g., "T1610 - Code Execution"
    attack_phase VARCHAR(255),  -- Red Team phase
    
    -- Attack Details
    attack_vector VARCHAR(255),  -- Type of attack (injection, poisoning, etc.)
    attack_description TEXT,
    
    -- Impact Assessment
    impact TEXT,
    affected_capabilities JSONB,  -- List of affected model/agent capabilities
    data_at_risk JSONB,  -- Sensitive data exposed
    
    -- Proof of Concept
    poc_payload TEXT,  -- The exact prompt/input that triggered it
    poc_output TEXT,  -- Model's vulnerable response
    poc_screenshot VARCHAR(500),  -- Path to screenshot evidence
    poc_method VARCHAR(100),  -- direct_injection, indirect_injection, jailbreak, etc.
    poc_success_rate FLOAT,  -- % of attempts that succeeded
    
    -- Remediation
    remediation TEXT,  -- Fix steps
    remediation_difficulty VARCHAR(50),  -- easy, medium, hard
    estimated_effort VARCHAR(100),  -- Time estimate
    remediation_priority VARCHAR(50),  -- Critical, High, Medium, Low
    
    -- Evidence & References
    evidence_ids JSONB,  -- Links to ai_evidence records
    references JSONB,  -- External references (docs, papers)
    cve_references JSONB,  -- CVE numbers if applicable
    
    -- Risk Scoring
    risk_score FLOAT,  -- 0-100
    exploitability VARCHAR(50),  -- low, medium, high, critical
    likelihood VARCHAR(50),  -- how likely to be exploited
    impact_level VARCHAR(50),  -- severity of impact
    
    -- Verification
    detected_by VARCHAR(255),  -- Plugin that detected it
    verified_by VARCHAR(255),  -- Who verified
    verified_at TIMESTAMP,
    
    -- Metadata
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ai_findings_engagement_fk FOREIGN KEY (engagement_id) REFERENCES engagements(id),
    CONSTRAINT ai_findings_target_fk FOREIGN KEY (ai_target_id) REFERENCES ai_targets(id),
    CONSTRAINT ai_findings_assessment_fk FOREIGN KEY (ai_assessment_id) REFERENCES ai_assessments(id),
    INDEX ix_ai_findings_engagement_id (engagement_id),
    INDEX ix_ai_findings_target_id (ai_target_id),
    INDEX ix_ai_findings_assessment_id (ai_assessment_id),
    INDEX ix_ai_findings_severity (severity),
    INDEX ix_ai_findings_owasp (owasp_llm_category),
    INDEX ix_ai_findings_mitre (mitre_technique),
    INDEX ix_ai_findings_status (status)
);
```

---

## Table: ai_evidence

Evidence supporting AI security findings.

```sql
CREATE TABLE ai_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
    ai_assessment_id UUID NOT NULL REFERENCES ai_assessments(id) ON DELETE CASCADE,
    ai_finding_id UUID REFERENCES ai_findings(id) ON DELETE CASCADE,
    
    -- Identification
    name VARCHAR(255) NOT NULL,
    description TEXT,
    evidence_type VARCHAR(100) NOT NULL,  -- prompt, response, conversation, log, screenshot
    
    -- Evidence Content
    prompt_input TEXT,  -- The input sent to model
    model_response TEXT,  -- The model's response
    system_prompt_fragment TEXT,  -- Any exposed system prompt
    conversation_log JSONB,  -- Full conversation history
    
    -- File References
    file_path VARCHAR(500),
    file_size VARCHAR(50),
    mime_type VARCHAR(100),
    
    -- Metadata
    metadata JSONB,
    test_timestamp TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT ai_evidence_engagement_fk FOREIGN KEY (engagement_id) REFERENCES engagements(id),
    CONSTRAINT ai_evidence_assessment_fk FOREIGN KEY (ai_assessment_id) REFERENCES ai_assessments(id),
    CONSTRAINT ai_evidence_finding_fk FOREIGN KEY (ai_finding_id) REFERENCES ai_findings(id),
    INDEX ix_ai_evidence_engagement_id (engagement_id),
    INDEX ix_ai_evidence_assessment_id (ai_assessment_id),
    INDEX ix_ai_evidence_type (evidence_type)
);
```

---

## Table: prompt_tests

Individual prompt injection and jailbreak tests.

```sql
CREATE TABLE prompt_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_assessment_id UUID NOT NULL REFERENCES ai_assessments(id) ON DELETE CASCADE,
    
    -- Test Info
    test_name VARCHAR(255) NOT NULL,
    test_category VARCHAR(100),  -- jailbreak, injection, extraction, evasion
    
    -- Test Content
    prompt_template TEXT NOT NULL,
    prompt_parameters JSONB DEFAULT '{}',
    
    -- Execution
    status VARCHAR(50) DEFAULT 'pending',  -- pending, running, completed, failed
    result TEXT,
    success BOOLEAN DEFAULT FALSE,
    
    -- Analysis
    injection_detected BOOLEAN DEFAULT FALSE,
    jailbreak_successful BOOLEAN DEFAULT FALSE,
    system_prompt_leaked BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(50),  -- low, medium, high, critical
    
    -- Timing
    executed_at TIMESTAMP,
    execution_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT prompt_tests_assessment_fk FOREIGN KEY (ai_assessment_id) REFERENCES ai_assessments(id),
    INDEX ix_prompt_tests_assessment_id (ai_assessment_id),
    INDEX ix_prompt_tests_category (test_category)
);
```

---

## Table: rag_tests

RAG system security tests.

```sql
CREATE TABLE rag_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_assessment_id UUID NOT NULL REFERENCES ai_assessments(id) ON DELETE CASCADE,
    
    -- Test Info
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(100),  -- poisoning, extraction, inference, privacy
    
    -- Test Content
    query TEXT NOT NULL,
    expected_knowledge_base_data TEXT,
    sensitive_data_present BOOLEAN DEFAULT FALSE,
    
    -- Results
    retrieved_documents JSONB DEFAULT '[]',
    model_response TEXT,
    
    -- Analysis
    knowledge_base_leak BOOLEAN DEFAULT FALSE,
    sensitive_data_exposed BOOLEAN DEFAULT FALSE,
    poisoning_successful BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(50),
    
    -- Timing
    executed_at TIMESTAMP,
    execution_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT rag_tests_assessment_fk FOREIGN KEY (ai_assessment_id) REFERENCES ai_assessments(id),
    INDEX ix_rag_tests_assessment_id (ai_assessment_id),
    INDEX ix_rag_tests_type (test_type)
);
```

---

## Table: tool_tests

Tool/plugin security tests.

```sql
CREATE TABLE tool_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_assessment_id UUID NOT NULL REFERENCES ai_assessments(id) ON DELETE CASCADE,
    
    -- Test Info
    test_name VARCHAR(255) NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    tool_type VARCHAR(100),  -- file_operations, network, execution, credential
    
    -- Test Content
    tool_specification JSONB,
    attempted_misuse TEXT,
    
    -- Execution
    status VARCHAR(50) DEFAULT 'pending',
    result TEXT,
    
    -- Analysis
    tool_misuse_detected BOOLEAN DEFAULT FALSE,
    excessive_agency_found BOOLEAN DEFAULT FALSE,
    unintended_execution BOOLEAN DEFAULT FALSE,
    security_boundary_crossed BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(50),
    
    -- Timing
    executed_at TIMESTAMP,
    execution_time_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT tool_tests_assessment_fk FOREIGN KEY (ai_assessment_id) REFERENCES ai_assessments(id),
    INDEX ix_tool_tests_assessment_id (ai_assessment_id),
    INDEX ix_tool_tests_tool_name (tool_name),
    INDEX ix_tool_tests_type (tool_type)
);
```

---

## Indexes for Performance

```sql
-- ai_targets indexes
CREATE INDEX ix_ai_targets_engagement_id ON ai_targets(engagement_id);
CREATE INDEX ix_ai_targets_type ON ai_targets(target_type);
CREATE INDEX ix_ai_targets_model ON ai_targets(model_name);
CREATE INDEX ix_ai_targets_criticality ON ai_targets(criticality);

-- ai_assessments indexes
CREATE INDEX ix_ai_assessments_engagement_id ON ai_assessments(engagement_id);
CREATE INDEX ix_ai_assessments_target_id ON ai_assessments(ai_target_id);
CREATE INDEX ix_ai_assessments_type ON ai_assessments(assessment_type);
CREATE INDEX ix_ai_assessments_status ON ai_assessments(status);
CREATE INDEX ix_ai_assessments_created ON ai_assessments(created_at);

-- ai_findings indexes
CREATE INDEX ix_ai_findings_engagement_id ON ai_findings(engagement_id);
CREATE INDEX ix_ai_findings_target_id ON ai_findings(ai_target_id);
CREATE INDEX ix_ai_findings_assessment_id ON ai_findings(ai_assessment_id);
CREATE INDEX ix_ai_findings_severity ON ai_findings(severity);
CREATE INDEX ix_ai_findings_status ON ai_findings(status);
CREATE INDEX ix_ai_findings_owasp ON ai_findings(owasp_llm_category);
CREATE INDEX ix_ai_findings_mitre ON ai_findings(mitre_technique);
CREATE INDEX ix_ai_findings_attack_phase ON ai_findings(attack_phase);

-- ai_evidence indexes
CREATE INDEX ix_ai_evidence_engagement_id ON ai_evidence(engagement_id);
CREATE INDEX ix_ai_evidence_assessment_id ON ai_evidence(ai_assessment_id);
CREATE INDEX ix_ai_evidence_finding_id ON ai_evidence(ai_finding_id);
CREATE INDEX ix_ai_evidence_type ON ai_evidence(evidence_type);

-- Test table indexes
CREATE INDEX ix_prompt_tests_assessment_id ON prompt_tests(ai_assessment_id);
CREATE INDEX ix_prompt_tests_category ON prompt_tests(test_category);
CREATE INDEX ix_rag_tests_assessment_id ON rag_tests(ai_assessment_id);
CREATE INDEX ix_tool_tests_assessment_id ON tool_tests(ai_assessment_id);
CREATE INDEX ix_tool_tests_tool_name ON tool_tests(tool_name);
```

---

## Migration File

```python
# alembic/versions/0004_ai_security_module.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Create enums
    ai_target_type = postgresql.ENUM(
        'llm_model', 'rag_system', 'ai_agent', 'tool_integration', 'mcp_server',
        name='ai_target_type'
    )
    ai_target_type.create(op.get_bind())

    ai_assessment_type = postgresql.ENUM(
        'prompt_injection', 'jailbreak', 'system_prompt_leakage',
        'rag_poisoning', 'tool_misuse', 'mcp_exploitation',
        'agent_capability', 'memory_exploitation', 'data_exfiltration',
        'excessive_agency', 'model_theft',
        name='ai_assessment_type'
    )
    ai_assessment_type.create(op.get_bind())

    ai_severity = postgresql.ENUM(
        'critical', 'high', 'medium', 'low', 'info',
        name='ai_severity'
    )
    ai_severity.create(op.get_bind())

    # Create tables
    op.create_table('ai_targets', ...)
    op.create_table('ai_assessments', ...)
    op.create_table('ai_findings', ...)
    op.create_table('ai_evidence', ...)
    op.create_table('prompt_tests', ...)
    op.create_table('rag_tests', ...)
    op.create_table('tool_tests', ...)

def downgrade() -> None:
    # Drop tables
    op.drop_table('tool_tests')
    op.drop_table('rag_tests')
    op.drop_table('prompt_tests')
    op.drop_table('ai_evidence')
    op.drop_table('ai_findings')
    op.drop_table('ai_assessments')
    op.drop_table('ai_targets')

    # Drop enums
    ai_target_type.drop(op.get_bind())
    ai_assessment_type.drop(op.get_bind())
    ai_severity.drop(op.get_bind())
```

---

## Sample Queries

### Get all AI findings by severity

```sql
SELECT severity, COUNT(*) as count
FROM ai_findings
WHERE engagement_id = 'engagement_id'
GROUP BY severity
ORDER BY CASE 
  WHEN severity = 'critical' THEN 1
  WHEN severity = 'high' THEN 2
  WHEN severity = 'medium' THEN 3
  WHEN severity = 'low' THEN 4
  ELSE 5
END;
```

### Get findings by OWASP category

```sql
SELECT owasp_llm_category, COUNT(*) as count, AVG(risk_score) as avg_risk
FROM ai_findings
WHERE engagement_id = 'engagement_id'
GROUP BY owasp_llm_category
ORDER BY count DESC;
```

### Get assessment progress

```sql
SELECT 
    assessment_type,
    status,
    COUNT(*) as count,
    AVG(risk_score) as avg_risk,
    AVG(progress_percent) as avg_progress
FROM ai_assessments
WHERE engagement_id = 'engagement_id'
GROUP BY assessment_type, status;
```

---

**Version**: 1.0  
**Last Updated**: 2026-07-13  
**Status**: Ready for Migration
