# Wednesday AI Integration Demo Guide

## Demo Objectives

Show that ReconHive has a working AI orchestration layer with:
1. ✅ API endpoints operational
2. ✅ Agent routing working
3. ✅ Mock responses realistic
4. ✅ Clean architecture maintained
5. ✅ Production-ready skeleton for Phase 2

## Prerequisites

```bash
# 1. Frontend running
http://127.0.0.1:3000

# 2. Backend running
http://localhost:8000

# 3. Check AI status
curl http://localhost:8000/api/v1/ai/status
```

## Demo Flow (10 minutes)

### 1. Agent Routing Demo

**Recon Query:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the attack surface?"}'
```
Routes to: **Recon Agent**

**Findings Query:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the highest-risk findings?"}'
```
Routes to: **Findings Agent**

**Report Query:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate executive summary"}'
```
Routes to: **Reports Agent**

**AI Security Query:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Map findings to OWASP LLM"}'
```
Routes to: **AI Security Agent**

### 2. Architecture Overview

**Component Stack:**
- Frontend: React 18 AI Copilot widget
- API: FastAPI /api/v1/ai/* endpoints
- Supervisor: Routes to specialized agents
- Agents: Recon, Findings, Reports, AI Security
- Database: PostgreSQL + AI conversation tables
- Security: Read-only, no execution, human-approved

### 3. Key Highlights

**Phase 1 Status:**
- ✅ Supervisor agent operational
- ✅ 4 agent stubs ready
- ✅ API endpoints live
- ✅ Database schema created
- ✅ Mock responses working

**Security Model:**
- ✅ No autonomous actions
- ✅ Read-only access
- ✅ No shell execution
- ✅ Human approval required

### 4. Phase 2 Roadmap

- 🔜 OpenAI/Anthropic LLM integration
- 🔜 Real database query responses
- 🔜 Conversation persistence
- 🔜 Vector search with pgvector
- 🔜 Audit logging

## Success Metrics

✅ All endpoints responding
✅ Routing logic works correctly
✅ Mock responses realistic
✅ Clean separation of concerns
✅ Security model enforced
