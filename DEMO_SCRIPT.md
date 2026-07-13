# ReconHive Demo Script

**Total Duration**: 15-20 minutes  
**Format**: Live walkthrough + Q&A  
**Audience**: Technical hiring panel (engineers, architects, security team)

---

## OPENING STATEMENT (1 minute)

> "ReconHive is an enterprise security assessment platform designed to orchestrate, manage, and report on security engagements at scale. Think of it as Jira for pentesters—but built for collaboration, automation, and compliance."

**Key Points**:
- Centralized engagement management
- Automated plugin-based scanning
- Real-time findings dashboard
- Compliance-ready audit trail
- AI copilot for insights

---

## SECTION 1: DASHBOARD WALKTHROUGH (4 minutes)

**Start**: http://localhost:3000

### 1.1 Executive Overview (1 min)

Say:
> "This is the executive dashboard. It's designed so leadership and pentesters can understand the security posture at a glance."

**Show**:
- KPI cards: "We're tracking 12 active engagements, 4,231 assets, 7 running scans"
- Trend indicators: "Assets up 12% from last month, scans up 40%"

**Talking Point**: This is the real-time status view. Every metric updates as scans complete and findings are discovered.

### 1.2 Recent Activity Timeline (1 min)

Say:
> "Every action in ReconHive is logged for compliance. Here you can see..."

**Show**:
- Engagement created 3 minutes ago
- Scan completed 15 minutes ago
- Evidence uploaded
- Finding marked as high severity

**Talking Point**: "This activity log is immutable and tied to user identity. Required for SOC 2 and PCI-DSS compliance."

### 1.3 Scan Monitoring (1 min)

Say:
> "Scans are real-time. You can see which plugins are running, on which targets, and the progress."

**Show**:
- Nuclei scan at 79% (web app)
- Subdomain discovery at 45%
- Nmap full scan at 30%
- Completed scans below

**Talking Point**: "Each scan runs in parallel via Celery task queue. We can orchestrate 100s of concurrent jobs."

### 1.4 Risk Overview (1 min)

Say:
> "The risk matrix shows severity distribution. This helps prioritize remediation."

**Show**:
- Red bar (9 Critical)
- Orange bar (27 High)
- Yellow bar (48 Medium)
- Rest blue/gray

**Talking Point**: "CRITICAL findings get flagged immediately. The dashboard is real-time; you'd see new findings pop up as scans complete."

---

## SECTION 2: ENGAGEMENT WORKFLOW (4 minutes)

### 2.1 Navigating to Engagements (0.5 min)

**Click**: Sidebar → Engagements

Say:
> "This is the engagement hub. Each row is a security assessment with its own scope, scans, and findings."

**Show**:
- Acme Corp Internal Test (Active)
- Beta Finance Security Audit (Active)
- DataCorp Web App Assessment (Completed)

### 2.2 Engagement Details (1 min)

Say:
> "Let's walk through the full workflow. When we create an engagement, we define the client, objectives, scope, and timeline."

**Talking Point**: 
- "The engagement is the root entity. Everything else—assets, scans, findings—rolls up to it."
- "You can have multiple engagements in parallel."

### 2.3 Scope Management (1 min)

**Conceptually describe**:
> "Inside each engagement, you define scope: which domains, IPs, CIDR ranges are in-scope, which are exclusions. This prevents out-of-scope scanning and keeps you compliant."

**Talking Point**:
- "Scope is enforced at the plugin level. A scan can't run against out-of-scope targets."
- "You can import scope from CSV or define manually."

### 2.4 Assets & Targets (1.5 min)

**Click**: Sidebar → Assets

Say:
> "Once you've defined scope, ReconHive catalogs all discovered assets. Servers, databases, web apps, cloud infrastructure—all tagged and indexed."

**Show**:
- app.acme.com (Web App, Critical)
- api.acme.com (API, Critical)
- mail.acme.com (Mail Server, High)
- db.internal (Database, High)

**Talking Point**:
- "Assets are the target inventory. Each asset can have multiple findings linked to it."
- "Criticality helps prioritize remediation."

---

## SECTION 3: SCANNING & JOB ORCHESTRATION (3 minutes)

### 3.1 Scan Management (1 min)

**Click**: Sidebar → Scans

Say:
> "This is the scan queue. Scans run asynchronously via Celery. We queue jobs, workers pick them up, and results stream back to the database."

**Show**:
- Running scans with progress bars
- Worker assignment (which worker is running which scan)
- Duration tracking

**Talking Point**: "Plugins are modular. We've got Nuclei, Burp, Nmap, testssl, Metasploit—each is a plugin that can be configured independently."

### 3.2 Plugin Architecture (1 min)

**Conceptually explain**:
> "Every scan is a plugin execution. Plugins are discoverable, configurable, and can be versioned. A plugin has a schema, input data, output normalizer, and retry logic."

**Talking Point**:
- "We can add new tools by writing a plugin adapter."
- "Results are normalized to a common schema—no matter which tool."

### 3.3 Job Execution Queue (1 min)

Say:
> "Under the hood, each scan spawns multiple jobs. A Nuclei scan might be 50 concurrent jobs. Celery manages the queue, retries on failure, and tracks progress."

**Talking Point**: "This is why you can scale horizontally. Add more workers, they pick up jobs from Redis, process them, and return results."

---

## SECTION 4: FINDINGS & EVIDENCE (3 minutes)

### 4.1 Findings Dashboard (1 min)

**Click**: Sidebar → Findings

Say:
> "Here's the core output: findings. Each is a vulnerability with severity, CVSS, affected asset, and status."

**Show**:
- Exposed Admin Panel (CRITICAL, 9.1)
- SQL Injection (CRITICAL, 8.9)
- Missing SPF (HIGH, 7.5)
- Weak TLS (HIGH, 7.2)

**Talking Point**:
- "Findings flow from plugin output. The Result Normalizer converts tool-specific formats into this common schema."
- "Status tracking: OPEN → CONFIRMED → REMEDIATED or FALSE_POSITIVE."

### 4.2 Evidence & Proof (1 min)

**Click**: Sidebar → Evidence

Say:
> "Evidence is the proof. Screenshots, HTTP responses, logs, anything that substantiates a finding."

**Show**:
- screenshot_20250713_1422.png
- http_response_sql_injection.json
- dns_enumeration_results.txt
- nmap_scan_results.xml

**Talking Point**: "Every piece of evidence is timestamped, linked to findings, and immutable. Auditors love this for compliance."

### 4.3 Impact & Remediation (1 min)

Say:
> "Beyond just reporting the issue, ReconHive tracks remediation. Each finding has a description, impact assessment, and recommended fix."

**Talking Point**: "Teams use this to prioritize. 'We have 156 findings. Which 10 do we fix first?' The severity and CVSS scores answer that."

---

## SECTION 5: REPORTING (2 minutes)

### 5.1 Report Generation (1 min)

**Click**: Sidebar → Reports

Say:
> "Once you've found, classified, and remediated, you generate a report. ReconHive produces professional penetration test reports in PDF or Markdown."

**Show**:
- Acme Corp - Q3 Pentest Report
- DataCorp - Final Assessment Report

**Talking Point**: 
- "Reports include: Executive Summary, Scope, Findings, Evidence, Remediation Steps."
- "Fully customizable sections."

### 5.2 Export & Distribution (1 min)

Say:
> "You can export as PDF (formatted for print) or Markdown (for version control / collaboration). Reports are timestamped and include metadata."

**Talking Point**: "This is the deliverable. Client-facing, audit-ready, signed and dated."

---

## SECTION 6: AI COPILOT (1 minute)

Say:
> "ReconHive includes an AI Copilot—this is a preview feature for v1.0."

**Click**: AI Copilot button (bottom right)

**Show**:
- Sidebar opens with chat interface
- Type: "Summarize engagement"
- AI responds with high-level overview

**Talking Point**:
- "The copilot answers questions about findings, assets, and risks."
- "Future phases: auto-correlate findings, generate remediation playbooks, predict risk trends."

---

## SECTION 7: ARCHITECTURE & SCALABILITY (2-3 minutes)

**Conceptually explain** (or show diagram if available):

> "ReconHive is built on clean architecture. Layered design: API layer, service layer, repository layer, domain models."

**Key Points**:
- **FastAPI** backend (30 endpoints, RESTful)
- **PostgreSQL** database (normalized schema, 11 core tables)
- **Celery** task queue (plugin job execution)
- **Redis** broker (inter-service communication)
- **Next.js** frontend (React 18, TypeScript)

**Scalability**:
- **Horizontal**: Add more Celery workers to handle concurrent scans
- **Vertical**: PostgreSQL connection pooling, Redis caching
- **Cloud-native**: Containerized, Kubernetes-ready

**Security**:
- JWT authentication
- Activity logging (20 event types)
- RBAC (admin, analyst, viewer roles)
- Audit trail for compliance
- Scope enforcement (can't scan out of scope)

---

## SECTION 8: LIVE DEMO INTERACTIONS (2-3 minutes)

### Optional: Show Real-Time Updates

If time allows:
- Refresh dashboard and note updated scan progress
- Show real-time finding count updates
- Demonstrate sidebar navigation responsiveness

### Optional: Show API Documentation

**Navigate to**: http://localhost:8000/docs

Say:
> "This is the auto-generated Swagger documentation. Every endpoint is documented, with request/response schemas, authentication, error codes."

---

## CLOSING REMARKS (1 minute)

> "ReconHive is production-ready for the backend. The frontend is in active development for Phase 5. We're targeting v1.0 in August with:
> - RBAC enforcement
> - Rate limiting
> - Frontend completion
> - Kubernetes deployment
> - Integrations with HackerOne, Bugcrowd, Jira, Slack
>
> The architecture is designed to scale. We can orchestrate 1000s of concurrent scans, manage 100s of engagements, and report findings in real-time.
>
> Questions?"

---

## COMMON QUESTIONS & ANSWERS

**Q**: "How many scans can you run in parallel?"
**A**: "Theoretically unlimited. Each worker can run multiple Celery jobs. We've tested with 100s of concurrent jobs. Load test results coming in Phase 5c."

**Q**: "What about false positives?"
**A**: "Each finding has a status field. Analysts mark FALSE_POSITIVE, which flags it in the audit trail. Useful for tuning plugin configs over time."

**Q**: "Can you integrate with existing SIEM tools?"
**A**: "Planned for Wave 2. We'll support webhooks and API integrations with Splunk, Datadog, and other platforms."

**Q**: "How is authentication handled?"
**A**: "JWT tokens. Stateless, scalable. Optional API key auth for service-to-service calls."

**Q**: "What about multi-tenancy?"
**A**: "Planned post-v1.0. Currently single-tenant per deployment. Can spin up multiple instances for multiple orgs."

**Q**: "Is there a mobile app?"
**A**: "Planned for Wave 3. Currently web-only (responsive design)."

---

## TIMING BREAKDOWN

| Section | Time |
|---------|------|
| Opening | 1 min |
| Dashboard | 4 min |
| Workflow | 4 min |
| Scanning | 3 min |
| Findings | 3 min |
| Reports | 2 min |
| AI Copilot | 1 min |
| Architecture | 2-3 min |
| Live Interactions | 2-3 min |
| Closing | 1 min |
| **TOTAL** | **15-20 min** |

**Buffer**: 5 minutes for live interactions / questions

---

## PRE-DEMO CHECKLIST

- [ ] Backend running (docker-compose up -d)
- [ ] Frontend running (npm run dev)
- [ ] Dashboard loads without errors
- [ ] All pages accessible via sidebar
- [ ] Sidebar navigation smooth
- [ ] Tables display data
- [ ] Charts render correctly
- [ ] AI Copilot opens/closes
- [ ] Browser zoom at 100%
- [ ] Network connection stable
- [ ] Backup: Have SCREENSHOT_CHECKLIST.md ready if demo crashes

---

**Good luck! You've got this.** 🚀
