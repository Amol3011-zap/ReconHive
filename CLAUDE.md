# ReconHive: Enterprise Security Assessment Platform

## Vision
Build the Operating System for Professional Security Assessments.

## Mission
Create an enterprise-grade, self-hosted Security Assessment Management and Orchestration Platform that orchestrates approved security tools, centralizes evidence, correlates findings, and provides professional reporting.

## Core Principles
- **Production Quality**: Every line of code must be production-ready
- **No Exploitation**: This platform orchestrates approved tools, never implements offensive exploitation
- **Modularity**: Every component must remain independent and extensible
- **Enterprise Grade**: Compare with Burp Enterprise, Acunetix, Tenable
- **Self-Hosted**: Deployable on-premise with full control
- **Security First**: No hardcoded secrets, proper auth/authz throughout

## Architecture

### Clean Architecture
```
Presentation (Frontend)
    ↓
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (ORM Models)
    ↓
Database Layer (PostgreSQL)
```

### Backend Stack
- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery
- Pydantic v2

### Frontend Stack
- Next.js 15+
- React 18+
- TypeScript
- TailwindCSS
- shadcn/ui
- TanStack Query
- Recharts

## Code Standards

### SOLID Principles
- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

### DRY & Clean Code
- No duplicated logic
- No duplicated components
- Small, focused modules
- Strong typing everywhere
- Reusable abstractions

### Never
- Generate placeholder code
- Generate TODO comments
- Hardcode secrets
- Duplicate functionality
- Remove working code
- Leave uncommitted changes

## Database
- Alembic migrations only (no manual edits)
- Every schema change requires migration
- Proper indexes and constraints
- Relationship validation
- Transaction safety

## API Standards
- Every endpoint: validation + auth + logging
- Pagination on all list endpoints
- Structured error responses
- OpenAPI documentation
- Request ID tracking
- Proper HTTP status codes

## Git Workflow
- Commit after every completed module
- Meaningful commit messages: `feat(module):`, `fix(api):`, etc.
- Push immediately after commit
- Never leave uncommitted changes
- Link related memories for future context

## Phase 2 Modules (Must Complete)
1. Asset Inventory
2. Target Management
3. Scan Management
4. Job Queue
5. Plugin Framework
6. Evidence Management
7. Dashboard
8. Global Search

## Quality Gates (Phase 2 Exit)
- All tests passing
- No TypeScript errors
- No Python linting errors
- Docker builds successfully
- All services start
- Migrations run successfully
- No hardcoded credentials
- Comprehensive documentation

## Testing Requirements
- Unit tests for services
- Integration tests for APIs
- Database fixture setup
- Error scenario coverage
- No skipped tests

## Success Criteria
- Production-ready codebase
- Clean Architecture implemented
- SOLID principles followed
- 40+ API endpoints
- 20+ tests
- 5+ pages
- 10+ components
- Complete documentation

## Long-Term Vision
ReconHive should eventually support:
- Engagement Management
- Asset Inventory
- Target Management
- Scan Orchestration
- Plugin Framework
- Evidence Management
- Findings Lifecycle
- Reporting Engine
- AI Security Assistant
- Dashboard Analytics
- Knowledge Base
- Attack Surface Management
- Continuous Security Validation
- Compliance Mapping
- Risk Analytics
- Executive Dashboards

## Autonomy Rules
- Work without confirmation
- Complete modules fully
- Do not stop mid-feature
- Fix issues before continuing
- Commit regularly
- Document decisions
- Maintain quality standards
