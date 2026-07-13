# AI Agent Capabilities Map

## Supervisor Agent

**Purpose:** Route user requests to specialized agents

**Input Keywords:**
- Asset, scan, technology, service, attack surface → Recon Agent
- Finding, severity, CVSS, vulnerability, remediation → Findings Agent
- Summary, executive, technical, report, overview → Reports Agent
- OWASP LLM, MITRE ATT&CK, prompt injection, RAG, AI security → AI Security Agent

**Routing Logic:** Keyword matching (Phase 1) → LLM-based routing (Phase 2+)

---

## Recon Agent

**Capabilities:**
- Summarize asset inventory by type
- Analyze scan results and completion status
- Identify technologies discovered
- Map attack surface and entry points
- Estimate reconnaissance completeness

**Data Sources:**
- Engagements table
- Assets table
- Scans table
- Technology stack fields

**Output Example:**
```
## Reconnaissance Summary

**Assets:** 45 total
- Web Applications: 12
- Servers: 8
- Network Infrastructure: 25

**Scans Completed:** 23
- Web Scans: 8
- Network Scans: 15

**Attack Surface:** MEDIUM
```

---

## Findings Agent

**Capabilities:**
- Summarize findings by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Explain CVSS scores and impact
- Generate remediation recommendations
- Map findings to MITRE ATT&CK tactics
- Identify root cause patterns

**Data Sources:**
- Findings table
- Evidence table
- Assets table

**Output Example:**
```
## Findings Summary

**Critical Findings:** 3
- SQL Injection in API endpoint
- Hardcoded credentials
- Cross-site scripting in form fields

**Remediation Priority:**
1. Patch critical findings immediately
2. Address high findings within 30 days
3. Medium findings within 90 days
```

---

## Reports Agent

**Capabilities:**
- Generate executive summaries (C-level)
- Create technical summaries (engineering)
- Produce remediation roadmaps
- Format for different stakeholders
- Estimate remediation timelines

**Output Options:**
- Executive: High-level risk, timeline, recommendations
- Technical: Detailed findings, CVSS, tool output
- Remediation: Priority matrix, effort estimates

---

## AI Security Agent

**Capabilities:**
- Map findings to OWASP LLM Top 10 (LLM01-LLM10)
- Identify MITRE ATT&CK AI tactics/techniques
- Assess Red Team attack phases
- Evaluate prompt injection risk
- Analyze RAG system vulnerabilities
- Detect tool misuse patterns
- Identify excessive agency issues

**Frameworks:**
- OWASP LLM Top 10: LLM01 → LLM10
- MITRE ATT&CK AI: Reconnaissance, Initial Access, Execution, etc.
- Red Team Phases: Recon → Weaponization → Delivery → Exploitation → C2 → Actions → Exfiltration

**Output Example:**
```
## AI Security Mapping

**OWASP LLM Findings:**
- LLM01 (Prompt Injection): FOUND
- LLM06 (Sensitive Info Disclosure): NOT FOUND

**MITRE ATT&CK:**
- Initial Access: Direct Prompt Injection
- Execution: Instruction Override

**Risk Level:** HIGH
```

---

## Phase 1 Status

| Agent | Status | Integration | LLM | Database |
|-------|--------|-------------|-----|----------|
| Supervisor | ✅ Ready | API | Mock | N/A |
| Recon | ✅ Stub | API | Mock | Future |
| Findings | ✅ Stub | API | Mock | Future |
| Reports | ✅ Stub | API | Mock | Future |
| AI Security | ✅ Stub | API | Mock | Future |

**Mock Data:** All agents return hardcoded responses (0 assets, 0 findings, etc.)

**Production Ready:** Phase 2 (LLM integration + real DB)
