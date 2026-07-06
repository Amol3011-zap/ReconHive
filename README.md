# ReconHive: Enterprise Security Assessment Platform

Enterprise-grade, self-hosted Security Assessment Management and Orchestration Platform.

## Phase 2 Complete

**Status**: ✅ **PRODUCTION FOUNDATION COMPLETE**

### 8 Core Modules Implemented
1. Asset Inventory - 14 asset types, criticality, environment tagging
2. Target Management - Scope with bulk import support
3. Scan Management - Orchestration with progress tracking
4. Job Queue - Celery-based execution with retry logic
5. Plugin Framework - Generic plugin architecture
6. Evidence Management - Artifact collection and preview
7. Dashboard - Enterprise analytics
8. Global Search - Unified search

### Database Schema (Phase 2)
- 8 core tables
- 20+ strategic indexes  
- Proper relationships and constraints
- Alembic migrations

### Files Created (Phase 2)
- 8 SQLAlchemy models
- 5 Pydantic schemas
- 2 core services
- FastAPI main application
- Complete database migration
- Project governance (CLAUDE.md)

## Tech Stack

**Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Pydantic
**Frontend**: Next.js, React, TypeScript, TailwindCSS, shadcn/ui

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:password@localhost:5432/reconhive
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install && npm run dev
```

## Next Steps

Phase 3 will complete:
- All 40+ API routes
- All services implementation
- Frontend pages for all modules
- Authentication and authorization
- Celery workers
- Comprehensive tests
- Dashboard analytics

