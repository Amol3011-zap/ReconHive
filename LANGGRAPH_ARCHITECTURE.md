# LangGraph Architecture for ReconHive

## Overview

ReconHive integrates LangChain + LangGraph as an AI Orchestration Layer on top of the existing architecture.

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React 18)                    │
│           (AI Copilot Widget - Phase 1)                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI (8000)                         │
│   /api/v1/ai/{chat,summarize,status,conversations}     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│          ReconHive Service Layer                         │
│    (Asset, Scan, Finding, Evidence Services)            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│      AI Orchestration Layer (LangGraph)                  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │         Supervisor Agent                          │ │
│  │  Routes requests to specialized agents            │ │
│  └───────────┬──────────────────────────────────────┘ │
│              │                                         │
│   ┌──────────┼──────────────────────┬─────────────┐  │
│   ▼          ▼                       ▼             ▼   │
│ ┌────┐  ┌────────┐  ┌────────┐  ┌──────────┐      │
│ │Recon   Findings │ Reports │ AI Security      │
│ │Agent    Agent  │  Agent  │  Agent           │
│ └────┘  └────────┘  └────────┘  └──────────┘      │
│                                                    │
│  └────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐    ┌─────▼──────┐   ┌──────▼────┐
   │PostgreSQL│    │  Redis     │   │ pgvector  │
   │          │    │ (cache)    │   │ (embed)   │
   └──────────┘    └────────────┘   └───────────┘
```

## Key Components

### Supervisor Agent
- Routes user requests to appropriate agents
- Uses keyword matching (Phase 1) → LLM routing (Phase 2+)
- Returns routing decision with reasoning

### Specialized Agents
1. **Recon Agent**: Asset/scan summarization
2. **Findings Agent**: Finding analysis and remediation
3. **Reports Agent**: Executive/technical summaries
4. **AI Security Agent**: Framework mapping (OWASP LLM, MITRE ATT&CK)

### Database Tables

| Table | Purpose |
|-------|---------|
| `ai_conversations` | Chat session tracking |
| `ai_messages` | Message history |
| `ai_summaries` | Generated summaries |
| `ai_feedback` | User feedback on responses |

## Phase 1 (Current)

**✅ Implemented:**
- Supervisor agent with keyword routing
- 4 specialized agent stubs
- API endpoints (/ai/chat, /ai/summarize, /ai/status)
- Database schema
- Mock data responses

**⏳ Mocked (Phase 2+):**
- LLM integration (OpenAI/Anthropic)
- Real database queries
- Vector search with pgvector
- Conversation persistence
- Feedback learning

## Phase 2+ Roadmap

| Phase | Focus | Timeline |
|-------|-------|----------|
| 2 | LLM integration, real DB queries | August |
| 3 | Vector search, RAG, fine-tuning | September |
| 4 | Autonomous analysis, tool integration | October |
| 5 | Multi-agent orchestration, learning | November |

## Security Model

**MANDATORY:**
- No autonomous exploitation
- Human approval required for actions
- All requests logged and audited
- No shell access or command execution
- Tool allowlist enforcement
- Rate limiting on API

**Currently Enforced:**
- Read-only mode for all agents
- No database mutations
- No external calls
- Bearer token validation (Demo-only in Phase 1)
