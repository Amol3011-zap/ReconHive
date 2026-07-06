# ReconHive Architecture

## Overview

ReconHive is an enterprise-grade Security Assessment Management Platform built on Clean Architecture principles, emphasizing separation of concerns, testability, and maintainability.

## Architecture Layers

### 1. Presentation Layer (Frontend)
- **Technology**: Next.js 15, React, TypeScript, TailwindCSS
- **Location**: `frontend/`
- **Responsibility**: User interface, forms, real-time updates via WebSocket

### 2. API Layer (FastAPI Routes)
- **Location**: `backend/app/routes/api.py`
- **Responsibility**: HTTP request handling, request validation, response formatting
- **Security**: JWT authentication (via `app/security.py`)
- **Middleware**: RequestIdMiddleware, CORSMiddleware
- **Pattern**: Each route depends on exactly one service

### 3. Service Layer (Business Logic)
- **Location**: `backend/app/services/`
- **Files**: 
  - `base.py` - Abstract BaseService class
  - `engagement_service.py` - Engagement CRUD + summary
  - `asset_service.py` - Asset inventory management
  - `target_service.py` - Target/scope management
  - `scan_service.py` - Scan orchestration
  - `job_service.py` - Individual job execution
  - `plugin_service.py` - Plugin lifecycle
  - `evidence_service.py` - Evidence collection
  - `finding_service.py` - Finding management

**Responsibility**: Business logic, validation, orchestration
**Pattern**: All services inherit from `BaseService` providing CRUD methods

### 4. Repository Layer (Database Abstraction)
- **Location**: `backend/app/db/session.py`
- **Responsibility**: Database session management, transaction control
- **Pattern**: Services receive `Session` via `get_db()` dependency

### 5. Data Layer (Models & Migrations)
- **Models**: `backend/app/models/` - SQLAlchemy ORM models
- **Migrations**: `backend/alembic/versions/` - Database schema versioning

## Database Schema

### Core Entities

```
Engagement (Root)
├── Assets (14 types)
├── Targets (scope items)
├── Scans (assessment runs)
│   ├── Jobs (plugin executions)
│   ├── Evidence (collected data)
│   └── Findings (vulnerabilities)
└── Reports (deliverables)
```

### Key Relationships

| Parent | Child | Cascade | Purpose |
|--------|-------|---------|---------|
| Engagement | Asset | Delete | Scope cleanup |
| Engagement | Target | Delete | Scope cleanup |
| Engagement | Scan | Delete | Assessment cleanup |
| Scan | Job | Delete | Job cleanup |
| Scan | Evidence | Delete | Evidence cleanup |
| Scan | Finding | Delete | Finding cleanup |
| Job | Evidence | Set Null | Evidence preserved |
| Asset | Finding | Set Null | Finding preserved |

### Indexes (Performance)
- `idx_engagements_status` - Engagement list filtering
- `idx_assets_engagement` - Asset lookups
- `idx_scans_status` - Scan status queries
- `idx_findings_severity` - Finding filtering
- `idx_jobs_priority` - Job queue ordering

## Advanced Features (Phase 4)

### Plugin SDK (`backend/app/plugins/`)
- **BasePlugin**: Abstract interface all plugins implement
- **PluginType**: 5 types (Scanner, Normalizer, Reporter, Enricher, Analyzer)
- **PluginManager**: Lifecycle management (load, execute, health check)
- **Pattern**: Plugins isolated from core; zero core dependencies on plugins

### Event Bus (`backend/app/events/bus.py`)
- **EventType**: 12+ event types covering lifecycle
- **EventBus**: Global pub/sub with history
- **Pattern**: Services emit events on CRUD operations
- **Use**: Real-time dashboards, workflows, audit trail

### AI Copilot (`backend/app/ai/copilot.py`)
- **Summarize**: Evidence-based finding summaries (no invention)
- **Map to MITRE**: CWE → ATT&CK mappings
- **Suggest Remediation**: Pattern-based recommendations
- **Detect Duplicates**: Finding deduplication
- **Validate**: Ensures evidence exists

### WebSocket Support (`backend/app/realtime/websocket.py`)
- **ConnectionManager**: User subscription tracking
- **Broadcast**: Real-time event distribution
- **Pattern**: Event bus publishes → WebSocket broadcasts

## Code Organization

```
backend/
├── app/
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic (8 services)
│   ├── routes/              # FastAPI routes
│   ├── schemas/             # Pydantic request/response models
│   ├── db/                  # Database session
│   ├── plugins/             # Plugin SDK (base.py, manager.py)
│   ├── events/              # Event bus (bus.py)
│   ├── ai/                  # AI Copilot (copilot.py)
│   ├── realtime/            # WebSocket (websocket.py)
│   ├── utils/
│   │   ├── responses.py     # Response envelopes
│   │   ├── logger.py        # Structured logging
│   │   └── middleware.py    # Request ID tracking
│   ├── security.py          # JWT authentication
│   ├── config.py            # Environment configuration
│   └── main.py              # FastAPI app
├── tests/                   # Unit and integration tests
├── alembic/
│   └── versions/            # Database migrations
└── requirements.txt         # Dependencies
```

## Request Flow Example: Create Engagement

```
1. HTTP POST /api/v1/engagements
   └── FastAPI Route (api.py:18)
       ├── Validates request via Pydantic schema
       ├── Verifies JWT token (security.py)
       └── Calls service method

2. Service Layer (engagement_service.py:15)
   ├── Validates business logic
   ├── Creates model instance
   └── Persists to database

3. Response Layer (responses.py)
   ├── Wraps result in APIResponse
   └── Returns to client

4. Event Bus (bus.py)
   └── Emits ENGAGEMENT_CREATED event
       └── WebSocket broadcasts to connected clients
```

## SOLID Principles Implementation

| Principle | Implementation |
|-----------|-----------------|
| **S**ingle Responsibility | Each service handles one entity type |
| **O**pen/Closed | BaseService extensible; plugins extend not modify core |
| **L**iskov Substitution | All plugins substitute BasePlugin correctly |
| **I**nterface Segregation | Interfaces separated (Service, Repository, Plugin) |
| **D**ependency Inversion | Services depend on abstractions (Session, BasePlugin) |

## Security Architecture

### Authentication
- JWT tokens with expiration
- Token issued at login (to be implemented)
- All endpoints require valid token (via `Depends(verify_token)`)

### Authorization
- User context available in all requests
- RBAC decorators for admin endpoints
- Request logging includes user ID

### Data Protection
- Database credentials via environment variables
- CORS restricted to specific origins
- SQL parameterization prevents injection

## Performance Considerations

### Query Optimization
- Strategic indexes on foreign keys and frequently filtered columns
- Eager loading for relationships (joinedload/selectinload)
- Pagination for list operations (limit 50 default)
- N+1 query prevention in services

### Caching (Phase 5+)
- Response caching for GET endpoints
- Plugin health check caching
- Event history pruning

### Scalability
- Stateless API design
- Event bus separable from core (can connect to Redis)
- Plugin execution independent of API

## Deployment Architecture

### Docker
- Base image: `python:3.11-slim`
- Multi-stage build
- Service runs on port 8000

### Database
- PostgreSQL 14+
- pgvector extension (semantic search, Phase 5+)
- Migration management via Alembic

### Environment Configuration
- `.env` file for local development
- Environment variables for production
- Settings class validates required vars

## Phase 5: Assessment Engine

Phase 5 extends the architecture with:

1. **Plugin Registry**: Central plugin catalog
2. **Plugin Loader**: Dynamic plugin discovery
3. **Execution Queue**: Job scheduling and distribution
4. **Result Normalization**: Standardize plugin outputs
5. **Evidence Correlation**: Link evidence to findings
6. **Metrics Collection**: Track assessment progress
7. **Activity Timeline**: Audit trail of all operations

## Key Design Patterns

| Pattern | Usage | Files |
|---------|-------|-------|
| Repository | DB abstraction | `db/session.py` |
| Dependency Injection | Service instantiation | `routes/api.py` |
| Abstract Base Class | Plugin interface | `plugins/base.py` |
| Pub/Sub | Event distribution | `events/bus.py` |
| Middleware | Cross-cutting concerns | `main.py`, `middleware.py` |
| Service Locator | Plugin management | `plugins/manager.py` |

## Testing Strategy

### Unit Tests
- Service business logic
- Schema validation
- Error handling

### Integration Tests
- API endpoint flows
- Database transactions
- Event bus operations

### E2E Tests (Phase 5+)
- Complete assessment workflows
- Plugin execution
- Report generation

---

**Last Updated**: 2026-07-07  
**Version**: 4.0.0  
**Status**: Production Ready (with noted security improvements needed)
