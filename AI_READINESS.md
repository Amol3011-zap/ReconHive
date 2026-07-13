# AI READINESS: ReconHive LLM Copilot Preparation

**Assessment Date**: 2026-07-13  
**Grade**: C+ (5/10) — Foundation built, AI features not yet implemented

---

## AI CAPABILITY MATRIX

| Feature | Status | Score | ETA | Notes |
|---------|--------|-------|-----|-------|
| **Vector Database** | ⏳ | 2/10 | Phase 5c | pgvector extension installed, not used |
| **Semantic Search** | ❌ | 0/10 | Phase 5c | No embeddings pipeline |
| **RAG System** | ❌ | 0/10 | Phase 6 | Planned post-v1.0 |
| **Report Generation** | ❌ | 0/10 | Phase 6 | LLM integration not started |
| **Natural Language Queries** | ❌ | 0/10 | Phase 6 | No NLP layer |
| **Finding Correlation** | ⏳ | 30/10 | Phase 5b | Deterministic rules, not AI |
| **Evidence Classification** | ❌ | 0/10 | Wave 2 | Auto-categorize tool output |
| **Risk Scoring** | ✅ | 60/10 | Phase 5 | Manual CVSS, automation ready |
| **Prompt Safety** | ❌ | 0/10 | Phase 6 | No guardrails |
| **Cost Tracking** | ❌ | 0/10 | Phase 6 | No token counting |

**Overall AI Readiness**: **C+ (5/10)** — Infrastructure ready, features deferred

---

## FOUNDATION (READY FOR AI FEATURES)

### 1. Vector Database: pgvector ✅ Configured

**Status**: Extension installed, not used

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Future table structure
CREATE TABLE evidence_embeddings (
  id UUID PRIMARY KEY,
  evidence_id UUID REFERENCES evidence(id),
  embedding vector(1536),  -- OpenAI ada-002 size
  created_at TIMESTAMP
);

CREATE INDEX ON evidence_embeddings USING IVFFLAT (embedding vector_cosine_ops);
```

**When to activate** (Phase 5c):
```python
# Service layer
class EvidenceEmbeddingService(BaseService):
    async def embed_evidence(self, evidence: Evidence):
        # Call OpenAI API for embedding
        embedding = await self.llm.embed(evidence.raw_data)
        # Store in pgvector
        await self.db.create(EvidenceEmbedding, {
            "evidence_id": evidence.id,
            "embedding": embedding
        })
```

---

### 2. Data Structure for LLM Consumption ✅ Ready

**Activity Timeline**: 20 events with full context

```python
EventLog {
  id, activity_type, entity_id, entity_type, user_id,
  description, metadata (JSON), created_at
}

# Example context for LLM:
{
  "engagement": "Example Corp",
  "scan": "nmap_full_network",
  "events": [
    {
      "timestamp": "2026-07-13T10:00:00Z",
      "action": "finding_created",
      "details": {
        "title": "SQL Injection in login form",
        "severity": "CRITICAL",
        "asset": "app.example.com",
        "evidence": "...raw_data..."
      }
    }
  ]
}
```

**Strength**: ✅ Audit trail designed for LLM context windows

---

### 3. Evidence Schema: Normalizer ✅ Ready

**Result Normalizer** converts tool output to standard format:

```python
# Internal normalizer schema
class NormalizedFinding(BaseModel):
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    cvss_score: Optional[float]
    cwe_id: Optional[str]
    attack_vector: str
    proof_of_concept: str
    remediation: str
    tool: str  # nmap, burp, metasploit
    raw_output: dict  # Original tool JSON
```

**Preparation for AI**:
- Normalized format makes evidence easier to analyze
- Raw output preserved for context
- Tool metadata enables tool-specific LLM prompts

---

## PLANNED AI FEATURES (Phase 5+)

### Phase 5c: Report Generation (2 weeks out)

**Scope**: Generate narrative findings reports from API

**Implementation**:
```python
# POST /findings/{id}/generate-report
async def generate_report(finding_id: UUID, llm_model: str = "gpt-4"):
    finding = await FindingService.read(finding_id)
    evidence_list = await EvidenceService.list(finding_id=finding_id)
    
    prompt = f"""
    Given this vulnerability finding, generate a professional 
    pentesting report section:
    
    Title: {finding.title}
    Severity: {finding.severity}
    Evidence:
    {json.dumps([e.raw_data for e in evidence_list], indent=2)}
    
    Generate:
    1. Executive summary (2-3 sentences)
    2. Technical details (1 paragraph)
    3. Remediation steps (bullet list)
    4. CVSS scoring rationale
    """
    
    report_section = await openai_client.complete(prompt, model=llm_model)
    return {
        "finding_id": finding_id,
        "report_section": report_section,
        "tokens_used": count_tokens(prompt + report_section),
        "model": llm_model
    }
```

**Dependencies**:
- OpenAI API key
- Token counting library
- Cost tracking (optional)

**Cost**: ~$0.02 per report (GPT-4)

---

### Phase 5d: Finding Correlation (AI)

**Current**: Deterministic rule-based (Phase 5b)

**Future**: LLM-assisted correlation

```python
# POST /findings/correlate
async def correlate_findings(engagement_id: UUID):
    findings = await FindingService.list(engagement_id=engagement_id)
    
    prompt = f"""
    Analyze these security findings and identify correlations:
    
    Findings:
    {json.dumps([f.dict() for f in findings], indent=2)}
    
    For each correlated group, return:
    {{
      "group_name": "root cause category",
      "findings": [list of finding IDs],
      "root_cause": "likely cause",
      "exploitation_chain": "how these can be chained",
      "remediation_priority": "which to fix first"
    }}
    """
    
    correlated = await openai_client.complete(prompt, model="gpt-4")
    return correlated
```

---

### Phase 6: Natural Language Queries (Post-v1.0)

**Vision**: Ask questions about engagement findings

```python
# POST /engagements/{id}/ask
async def natural_language_query(engagement_id: UUID, query: str):
    # e.g., "What are the critical vulnerabilities in the web app?"
    
    # 1. Retrieve context from engagement
    engagement = await EngagementService.read(engagement_id)
    findings = await FindingService.list(engagement_id=engagement_id)
    
    # 2. Semantic search for relevant findings
    query_embedding = await llm.embed(query)
    relevant_findings = await semantic_search(
        embedding=query_embedding,
        limit=5
    )
    
    # 3. Generate answer from context
    prompt = f"""
    Question: {query}
    
    Relevant findings from {engagement.name}:
    {json.dumps([f.dict() for f in relevant_findings], indent=2)}
    
    Answer the question directly with findings-based evidence.
    """
    
    answer = await openai_client.complete(prompt, model="gpt-3.5-turbo")
    return {"query": query, "answer": answer}
```

---

### Phase 6: Evidence Auto-Classification (Post-v1.0)

**Current**: Manual classification by analyst

**Future**: LLM reads raw tool output, suggests finding type

```python
# POST /evidence/{id}/classify
async def classify_evidence(evidence_id: UUID):
    evidence = await EvidenceService.read(evidence_id)
    
    prompt = f"""
    Analyze this raw security tool output and classify it.
    
    Tool: {evidence.tool_name}
    Output:
    {json.dumps(evidence.raw_data, indent=2)}
    
    Return:
    {{
      "finding_type": "vulnerability type",
      "severity": "CRITICAL/HIGH/MEDIUM/LOW/INFO",
      "affected_asset": "what was tested",
      "suggested_title": "findings title",
      "suggested_description": "technical details",
      "cwe_ids": [list],
      "cvss_preliminary": 0.0-10.0
    }}
    """
    
    classification = await openai_client.complete(prompt, model="gpt-4")
    return classification
```

---

## INFRASTRUCTURE FOR AI

### LLM Integration Points

```python
# api/llm/openai.py
from openai import AsyncOpenAI

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4"  # or gpt-3.5-turbo for cost
    
    async def complete(self, prompt: str, model: str = None) -> str:
        response = await self.client.chat.completions.create(
            model=model or self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Balanced creativity/consistency
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    async def embed(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        response = await self.client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
```

### Cost Tracking

```python
# api/llm/cost_tracker.py
class CostTracker:
    COSTS = {
        "gpt-4": {"input": 0.03/1000, "output": 0.06/1000},
        "gpt-3.5-turbo": {"input": 0.0005/1000, "output": 0.0015/1000},
        "text-embedding-3-small": {"tokens": 0.02/1000}
    }
    
    async def track_completion(self, model: str, 
                               input_tokens: int, 
                               output_tokens: int):
        input_cost = input_tokens * self.COSTS[model]["input"]
        output_cost = output_tokens * self.COSTS[model]["output"]
        total = input_cost + output_cost
        
        # Log to audit trail
        await EventLog.create({
            "activity_type": "llm_api_call",
            "metadata": {
                "model": model,
                "tokens": input_tokens + output_tokens,
                "cost_usd": total
            }
        })
        return total
```

---

## PROMPT ENGINEERING PATTERNS

### Safety Guardrails (Phase 6)

```python
class PromptGuard:
    FORBIDDEN_PATTERNS = [
        "delete", "drop", "truncate",  # SQL
        "rm -rf", "sudo", "chmod",      # Shell
        "exec", "eval",                  # Code execution
    ]
    
    def is_safe_prompt(self, prompt: str) -> bool:
        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern.lower() in prompt.lower():
                return False
        return True
    
    async def sanitize_llm_output(self, response: str) -> str:
        # Prevent LLM from returning dangerous commands
        for pattern in self.FORBIDDEN_PATTERNS:
            response = response.replace(pattern, "[REDACTED]")
        return response
```

### Tool-Specific Prompts

```python
TOOL_PROMPTS = {
    "nmap": """
        This is output from nmap network scanning tool.
        Extract:
        - Open ports
        - Services
        - Potential vulnerabilities
        - Recommendations
    """,
    "burp": """
        This is output from Burp Suite web application scanner.
        Identify:
        - Web vulnerabilities (SQLi, XSS, etc.)
        - Authentication flaws
        - Configuration issues
    """,
    "metasploit": """
        This is output from Metasploit exploitation framework.
        Document:
        - Successful exploits
        - Post-exploitation access
        - Proof of concept
        - Impact assessment
    """
}
```

---

## KNOWLEDGE GRAPH (Future)

**Vision** (Wave 2): Build searchable knowledge base from findings

```python
# Future table structure
CREATE TABLE knowledge_graph (
  id UUID PRIMARY KEY,
  source_type TEXT,  -- "vulnerability", "remediation", "cve", "technique"
  source_id UUID,    -- Link to finding/CVE/technique
  related_entities JSONB,  -- {"cve": ["CVE-2021-1234"], ...}
  relationships JSONB,     -- {"exploitable_via": "SQLi", ...}
);

# Example query
SELECT * FROM knowledge_graph 
WHERE relationships->>'root_cause' = 'insecure_config'
LIMIT 10;
```

---

## TESTING AI FEATURES

### Unit Tests (Phase 5c+)

```python
@pytest.mark.asyncio
async def test_report_generation_includes_remediation():
    finding = await FindingFactory.create()
    report = await generate_report(finding.id)
    
    assert "remediation" in report.lower()
    assert "cvss" in report.lower()

@pytest.mark.asyncio
async def test_cost_tracking_records_api_calls():
    cost = await track_cost(model="gpt-4", tokens_in=100, tokens_out=50)
    
    log = await EventLog.filter(activity_type="llm_api_call").first()
    assert log is not None
    assert log.metadata["cost_usd"] > 0
```

### Integration Tests (Phase 6)

- [ ] Test with real OpenAI API (gated behind feature flag)
- [ ] Validate LLM output against schema
- [ ] Monitor cost accuracy

### Cost Controls

```python
# api/settings.py
class Settings(BaseSettings):
    llm_enabled: bool = False  # Gate behind flag
    llm_monthly_budget_usd: float = 100.0
    llm_model: str = "gpt-3.5-turbo"  # Cheaper by default
    llm_max_tokens_per_call: int = 1500
```

---

## ROADMAP

| Timeline | Feature | Effort | Cost |
|----------|---------|--------|------|
| Phase 5c | Report generation | 2 weeks | $0.01-0.05/report |
| Phase 5d | Finding correlation (AI) | 1 week | $0.02-0.10/engagement |
| Phase 6 (v1.0+) | Natural language queries | 3 weeks | $0.01-0.20/query |
| Phase 6+ | Evidence auto-classification | 2 weeks | $0.001-0.01/evidence |
| Wave 2 | Knowledge graph | 4 weeks | N/A (internal) |

---

## COST ESTIMATION

**Assumptions**:
- 1 engagement per day
- 20 findings per engagement
- 10 evidence items per finding
- 50 users

**Monthly Cost** (Phase 5c-5d):

| Feature | Calls/month | Cost/call | Total |
|---------|-------------|-----------|-------|
| Report generation | 600 (30 engagements × 20) | $0.02 | $12 |
| Finding correlation | 30 | $0.10 | $3 |
| **Phase 5 Total** | | | **$15/month** |

**Phase 6 (v1.0+)**:

| Feature | Calls/month | Cost/call | Total |
|---------|-------------|-----------|-------|
| NL queries | 500 (10/user/month) | $0.02 | $10 |
| Auto-classification | 6,000 | $0.005 | $30 |
| **Phase 6 Total** | | | **$40/month** |

**Overall**: Minimal cost (<$100/month at scale), high value

---

## RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM hallucination | False findings reported | Manual validation in v1.0, confidence scores in Phase 6 |
| API rate limits | Feature unavailable | Queue system with exponential backoff |
| Cost overruns | Budget exceeded | Monthly budget gates, model downgrade fallback |
| Data leakage | Sensitive data sent to OpenAI | Strip PII before sending, use Azure OpenAI if compliance needed |
| Prompt injection | LLM exploited | Input sanitization, prompt guards |

---

## COMPLIANCE & PRIVACY

**GDPR**: If processing EU user data, ensure:
- [ ] Data Processing Agreement with OpenAI
- [ ] Data residency compliance
- [ ] Audit trail of LLM API calls

**SOC 2**: Document:
- [ ] LLM input validation
- [ ] Cost controls and approval workflows
- [ ] Incident response for API compromise

---

**AI Readiness Grade: C+ (5/10)**

**Ready**: Vector database, data structure, evidence normalizer  
**In Progress**: Infrastructure and cost tracking  
**Not Started**: LLM features (Phase 5c+)

---

Prepared by: AI/ML Lead  
Date: 2026-07-13
