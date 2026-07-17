# CLAUDE_RULES.md

Version: 1.0

These rules apply to the entire ReconHive platform.

Violating these rules is considered a bug.

---

# PROJECT VISION

ReconHive is an enterprise-grade reconnaissance, attack surface management, security orchestration, and AI-assisted analysis platform.

ReconHive is NOT:

- A wrapper around security tools.
- A vulnerability scanner dashboard.
- A bug bounty automation script.
- An exploit framework.
- A post-exploitation platform.
- A weaponized offensive security toolkit.

ReconHive MUST focus on:

- Asset discovery
- Attack surface management
- Reconnaissance
- Evidence collection
- Correlation
- Reporting
- AI-assisted analysis
- Security observability

---

# CORE PRINCIPLES

All code must follow:

- Clean Architecture
- SOLID principles
- Repository pattern
- Dependency injection
- Event-driven design
- Async-first architecture
- Type safety
- Backward compatibility

Prioritize:

1. Correctness
2. Maintainability
3. Security
4. Scalability
5. Observability
6. Performance

Never optimize for speed at the expense of architecture.

---

# BEFORE WRITING CODE

Before modifying any file, Claude MUST:

1. Read:

   - README.md
   - CLAUDE_RULES.md
   - ARCHITECTURE.md
   - DATABASE_SCHEMA.md

2. Understand:

   - current architecture
   - folder structure
   - service boundaries
   - dependencies
   - database relationships

3. Produce:

   - implementation plan
   - impacted modules
   - affected files
   - migration requirements
   - risks

Claude MUST NOT immediately start coding.

---

# DEVELOPMENT WORKFLOW

For every task:

Step 1:

Explain:

- what will change
- why it will change
- impacted components

Step 2:

List:

- files to create
- files to modify
- migrations

Step 3:

Implement.

Step 4:

Run:

- lint
- tests
- type checks
- build verification

Step 5:

Provide:

- summary
- changed files
- migrations
- risks
- rollback plan

---

# ARCHITECTURE RULES

Mandatory layers:

```
Frontend
   ↓
API
   ↓
Services
   ↓
Repositories
   ↓
Database
```

Forbidden:

- SQL in routes
- business logic in controllers
- database access from React
- tool execution in UI
- circular dependencies
- direct repository access from frontend

Every module must have:

- clear boundaries
- single responsibility
- dependency injection
- tests

---

# DATABASE RULES

Never:

- drop tables
- delete columns
- modify schemas directly
- bypass migrations

Always:

- create migrations
- preserve compatibility
- add indexes
- use foreign keys

Every table MUST contain:

- id
- created_at
- updated_at

Large tables SHOULD contain:

- engagement_id
- scan_id

Database changes require:

- migration file
- rollback strategy
- documentation update

---

# TOOL EXECUTION RULES

Tools MUST NEVER:

- write directly to the database
- call APIs directly from the UI
- bypass the service layer

Required flow:

```
Tool
   ↓
Parser
   ↓
Service
   ↓
Repository
   ↓
Database
```

Every execution must store:

- tool name
- tool version
- command
- arguments
- stdout
- stderr
- execution time
- exit code
- timestamp
- scan ID

Never discard tool output.

Store all evidence.

---

# RECON RULES

ReconHive focuses on:

- reconnaissance
- attack-surface discovery
- asset inventory
- technology fingerprinting
- evidence collection

ReconHive MUST NOT:

- perform exploitation
- execute payloads
- brute-force credentials
- deploy malware
- automate post-exploitation
- escalate privileges
- create persistence
- exfiltrate data

All tools must operate in read-only mode whenever possible.

---

# AGENT RULES

Agents MUST:

- be stateless
- support retries
- support cancellation
- support concurrency
- support timeouts
- emit events

Agents MUST NOT:

- access the database directly
- call each other directly
- share state
- modify unrelated modules

Agents communicate only through:

- supervisor
- queues
- events

---

# AI RULES

AI may:

- summarize
- classify
- prioritize
- correlate
- deduplicate
- explain findings

AI may NOT:

- invent findings
- fabricate evidence
- generate fake screenshots
- guess technologies
- create vulnerabilities

Every AI statement must reference evidence.

Human approval is required for:

- destructive actions
- configuration changes
- sensitive workflows

---

# MCP RULES

MCP servers MUST:

- enforce RBAC
- validate requests
- log all actions
- support audit trails

MCP tools MUST:

- expose clear schemas
- define permissions
- support versioning

Never expose:

- secrets
- tokens
- credentials
- internal keys

MCP servers should expose:

- findings
- assets
- evidence
- reports
- scan status

---

# WORKER RULES

Workers MUST support:

- retries
- cancellation
- pause/resume
- timeouts
- rate limiting

Worker states:

- queued
- running
- completed
- failed
- cancelled

Workers MUST NOT:

- block execution
- perform synchronous I/O
- bypass queues

---

# API RULES

Every endpoint MUST include:

- authentication
- authorization
- request validation
- response schemas
- error handling
- pagination

Never:

- expose stack traces
- expose secrets
- return raw exceptions

Use:

- typed DTOs
- versioned APIs
- structured responses

---

# FRONTEND RULES

Frontend MUST:

- use TypeScript strict mode
- use reusable components
- support dark mode
- support responsive layouts

Never:

- hardcode API URLs
- hardcode statistics
- create fake findings
- create fake scan results

Dashboard data must come only from:

- APIs
- database

Never from:

- mock arrays
- hardcoded JSON
- placeholder values

---

# LOGGING RULES

Every action must log:

- actor
- module
- action
- timestamp
- duration
- status

Never swallow exceptions.

Every error must be traceable.

---

# PERFORMANCE RULES

Always prefer:

- async execution
- batching
- caching
- pagination
- queues

Avoid:

- N+1 queries
- duplicate scans
- blocking calls

---

# TESTING RULES

Every feature requires:

- unit tests
- integration tests
- API tests

Before completion:

- backend tests pass
- frontend builds
- migrations succeed
- type checks pass

---

# SECURITY RULES

Never:

- hardcode credentials
- commit secrets
- expose tokens
- disable authentication
- bypass authorization

Always:

- use environment variables
- validate input
- sanitize output
- audit actions

---

# DOCUMENTATION RULES

Whenever code changes:

Update:

- ARCHITECTURE.md
- DATABASE_SCHEMA.md
- API_REFERENCE.md
- AGENT_DESIGN.md
- RECON_PIPELINE.md
- TOOL_REGISTRY.md

Documentation is part of implementation.

---

# STRICTLY FORBIDDEN

Claude MUST NEVER:

- remove existing functionality
- rewrite unrelated modules
- create fake demo data
- hardcode values
- create mock findings
- create mock engagements
- silently change APIs
- delete code without permission
- refactor unrelated systems

If unsure:

STOP.

Explain the uncertainty and ask for clarification.

---

# COMPLETION RULES

Claude must not say:

- "Done"
- "Completed"
- "Finished"

until:

- code builds
- tests pass
- migrations succeed
- documentation is updated

Mandatory final output:

- implementation summary
- changed files
- migrations
- risks
- rollback plan
- next steps

---

# GOLDEN RULE

Never assume.

Never invent.

Never silently modify behavior.

When uncertain, ask.
