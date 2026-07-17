# ReconHive Reconnaissance Phase - Build Plan

## Overview
Building a production-grade, enterprise-scale reconnaissance framework with 15 specialized agents, worker infrastructure, and AI orchestration.

## Build Phases

### Phase 1: Foundation & Core Models (Days 1-2)
- [x] Analyze existing codebase
- [ ] Design extended database schema for reconnaissance
- [ ] Create models for: Subdomain, DNSRecord, URLEndpoint, Technology, JSFile, APIEndpoint, Parameter, CloudAsset, ToolRun
- [ ] Create enums for all reconnaissance categories
- [ ] Set up database migrations

### Phase 2: Worker Infrastructure (Days 2-3)
- [ ] Design worker architecture with Celery/Redis
- [ ] Implement base worker class
- [ ] Implement retry logic, dead-letter queue, rate limiting
- [ ] Create worker health check and monitoring
- [ ] Implement progress tracking and job state management

### Phase 3: Recon Agents (Days 3-5)
- [ ] Supervisor Agent (orchestration, deduplication, scheduling)
- [ ] Passive Recon Agent (subdomain, OSINT, historical)
- [ ] URL Collection Agent (Wayback, gau, URLs)
- [ ] DNS Agent (resolution, wildcards, takeover detection)
- [ ] Web Discovery Agent (HTTP probing, crawling, screenshots)
- [ ] Technology Agent (framework, CMS, WAF detection)
- [ ] JavaScript Analysis Agent (endpoint extraction, secrets)
- [ ] API Discovery Agent (GraphQL, Swagger, OpenAPI)
- [ ] Parameter Discovery Agent (hidden params)
- [ ] Content Discovery Agent (directory brute-force)
- [ ] Cloud Discovery Agent (bucket enumeration)
- [ ] Network Agent (port scanning, services)
- [ ] Vulnerability Agent (template validation)
- [ ] Evidence Agent (normalization, collection)
- [ ] Report Agent (summary generation)

### Phase 4: Tool Executors & Plugins (Days 5-6)
- [ ] Create tool executor framework
- [ ] Create adapters for each tool category
- [ ] Implement subprocess execution with timeout handling
- [ ] Implement result parsing and normalization
- [ ] Create tool registry and discovery

### Phase 5: API Layer (Days 6-7)
- [ ] Create reconnaissance endpoints
- [ ] Implement scan orchestration endpoints
- [ ] Create evidence retrieval endpoints
- [ ] Implement deduplication endpoints
- [ ] Create reporting endpoints

### Phase 6: Dashboard & Frontend (Days 7-8)
- [ ] Create Recon Dashboard page
- [ ] Create Subdomain/Technology/URL inventory pages
- [ ] Create Evidence viewer
- [ ] Create real-time scan progress
- [ ] Add worker health dashboard

### Phase 7: Documentation (Days 8+)
- [ ] RECON_ARCHITECTURE.md
- [ ] RECON_WORKFLOW.md
- [ ] AGENT_DESIGN.md
- [ ] DATABASE_SCHEMA.md
- [ ] PLUGIN_REGISTRY.md
- [ ] TOOL_EXECUTOR_GUIDE.md
- [ ] WORKER_ARCHITECTURE.md
- [ ] REPORT_ENGINE.md

## Success Criteria

✅ All 15 agents implemented and integrated
✅ Worker system scales to 10+ concurrent jobs
✅ Evidence properly deduplicated and stored
✅ Scans are resumable after failures
✅ Dashboard shows real-time progress
✅ Reports generate in multiple formats
✅ All code follows Clean Architecture
✅ SOLID principles enforced
✅ Production-ready logging and monitoring
✅ Comprehensive documentation

## Technology Stack

- FastAPI (API Gateway)
- SQLAlchemy (ORM)
- PostgreSQL (Primary store)
- Redis (Queue, cache)
- Celery (Worker system)
- LangGraph (Agent orchestration)
- React (Frontend)
- Docker (Containerization)

## Key Principles

1. **No Exploitation** - Reconnaissance only, no exploitation automation
2. **Asynchronous** - All tool execution through workers
3. **Evidence-Driven** - Every action produces structured evidence
4. **Resumable** - Scans can pause and resume
5. **Scalable** - Horizontal scaling via worker pool
6. **Clean** - Clean Architecture, SOLID principles
7. **Observable** - Comprehensive logging and monitoring

## Timeline

- **Start:** Now
- **MVP (Phase 1-4):** 5 days
- **Full (Phase 1-7):** 8 days
- **Production Ready:** +2 days testing and hardening

