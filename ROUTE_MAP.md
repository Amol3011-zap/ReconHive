# ReconHive Route Map

**Frontend Routes**: 8 Implemented + 1 in Dashboard  
**Backend Routes**: 30 endpoints (with import errors)  
**Status**: ⚠️ Frontend and backend don't fully connect

---

## FRONTEND ROUTES (Next.js App Router)

### Primary Routes (8 Total)

```
/ (Dashboard)
├── Layout: MainLayout + Sidebar
├── Components: MetricCard, ActivityTimeline, Table, RiskChart
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/engagements
├── Layout: MainLayout
├── Components: Table
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/assets
├── Layout: MainLayout
├── Components: Table
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/scans
├── Layout: MainLayout
├── Components: Table
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/findings
├── Layout: MainLayout
├── Components: Table
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/evidence
├── Layout: MainLayout
├── Components: Table
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/reports
├── Layout: MainLayout
├── Components: Card list
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected

/settings
├── Layout: MainLayout
├── Components: Form fields
├── Data: Mock (hardcoded setState)
├── Status: ✅ WORKS (display only)
└── Backend: ⚠️ Not connected
```

### Secondary Routes (Defined but Not Implemented)

- `/activity` - Referenced in Dashboard, route doesn't exist
- `/plugins` - Referenced in requirements, not implemented
- `/schedules` - Referenced in requirements, not implemented

---

## BACKEND ROUTES (FastAPI)

### Health & Root (2 Endpoints)

```
GET /health
├── Status: ✅ Working
├── Response: {"status": "healthy", "version": "3.0.0"}
└── Auth: ❌ Not required

GET /
├── Status: ✅ Working
├── Response: {name, version, modules, endpoints info}
└── Auth: ❌ Not required
```

### API Routes (30 Planned Endpoints)

```
GET /api/v1/engagements
├── Status: ⚠️ Route defined (import error in app)
├── Implementation: /routes/api.py
├── Auth: ✅ Required (HTTPBearer)
└── Frontend: Not integrated

POST /api/v1/engagements
├── Status: ⚠️ Route defined (import error)
├── Implementation: /routes/api.py
├── Auth: ✅ Required
└── Frontend: Not integrated

GET /api/v1/assets
├── Status: ⚠️ Route defined (import error)
├── Implementation: /routes/api.py
├── Auth: ✅ Required
└── Frontend: Not integrated

[... 27 more endpoints defined but not testable due to import error ...]

GET /api/v1/plugins/{plugin_id}/configs
├── Status: ⚠️ Route defined (import error)
├── Implementation: /routes/plugin_configs.py
├── Auth: ✅ Required
└── Frontend: Not integrated

POST /api/v1/plugins/{plugin_id}/configs/{id}/validate
├── Status: ⚠️ Route defined (import error)
├── Implementation: /routes/plugin_configs.py
├── Auth: ✅ Required
└── Frontend: Not integrated
```

### Routes by Category

**Engagement Management (4 routes)**
- GET /api/v1/engagements
- POST /api/v1/engagements
- GET /api/v1/engagements/{id}
- PUT /api/v1/engagements/{id}

**Asset Management (4 routes)**
- GET /api/v1/assets
- POST /api/v1/assets
- GET /api/v1/assets/{id}
- PUT /api/v1/assets/{id}

**Target/Scope Management (4 routes)**
- GET /api/v1/targets
- POST /api/v1/targets
- GET /api/v1/targets/{id}
- PUT /api/v1/targets/{id}

**Scan Orchestration (4 routes)**
- GET /api/v1/scans
- POST /api/v1/scans
- GET /api/v1/scans/{id}
- PUT /api/v1/scans/{id}

**Job Execution (3 routes)**
- POST /api/v1/jobs
- GET /api/v1/jobs/{id}
- DELETE /api/v1/jobs/{id}

**Finding Management (4 routes)**
- GET /api/v1/findings
- POST /api/v1/findings
- GET /api/v1/findings/{id}
- PUT /api/v1/findings/{id}

**Evidence Collection (3 routes)**
- POST /api/v1/evidence
- GET /api/v1/evidence/{id}
- DELETE /api/v1/evidence/{id}

**Plugin Management (2 routes)**
- GET /api/v1/plugins
- PUT /api/v1/plugins/{id}

**Plugin Configuration - NEW (10 routes)**
- POST /api/v1/plugins/{plugin_id}/configs
- GET /api/v1/plugins/{plugin_id}/configs
- GET /api/v1/plugins/{plugin_id}/configs/default
- GET /api/v1/plugins/{plugin_id}/configs/{id}
- PUT /api/v1/plugins/{plugin_id}/configs/{id}
- POST /api/v1/plugins/{plugin_id}/configs/{id}/validate
- POST /api/v1/plugins/{plugin_id}/configs/{id}/activate
- POST /api/v1/plugins/{plugin_id}/configs/{id}/deactivate
- DELETE /api/v1/plugins/{plugin_id}/configs/{id}
- GET /api/v1/plugins/{plugin_id}/configs/{id}/history

---

## FRONTEND-BACKEND INTEGRATION

### Current State

| Frontend Route | Backend Route | Connected | Status |
|---|---|---|---|
| / (Dashboard) | Multiple | ❌ | Mock only |
| /engagements | GET /api/v1/engagements | ❌ | Mock only |
| /assets | GET /api/v1/assets | ❌ | Mock only |
| /scans | GET /api/v1/scans | ❌ | Mock only |
| /findings | GET /api/v1/findings | ❌ | Mock only |
| /evidence | GET /api/v1/evidence | ❌ | Mock only |
| /reports | Custom | ❌ | Mock only |
| /settings | Custom | ❌ | Mock only |

### Missing Integration Layer

**api.ts** exists but:
- ✅ Defines base URL and method structure
- ✅ Has mock fallback data
- ❌ Not actually called by any page
- ❌ No useEffect to fetch data
- ❌ No error handling
- ❌ No loading state management

---

## NAVIGATION STRUCTURE

### Sidebar Navigation (8 Items)

```
🔐 ReconHive
├── 📊 Dashboard (/
├── 📋 Engagements (/engagements)
├── 🖥️  Assets (/assets)
├── 🔍 Scans (/scans)
├── 🚨 Findings (/findings)
├── 📸 Evidence (/evidence)
├── 📄 Reports (/reports)
└── ⚙️  Settings (/settings)

Quick Actions
└── ➕ New Engagement [Non-functional button]
```

### Missing Sidebar Items (Not Implemented)

- 🔧 Plugins (/plugins)
- ⏱️  Schedules (/schedules)

### Internal Navigation

**Dashboard Links**:
- "View all activity →" → `/activity` (route doesn't exist)
- "View all findings →" → `/findings` ✅

**Engagements Links**:
- None (should have edit/detail links)

---

## ROUTE PROTECTION

### Current State
- ❌ No auth middleware on frontend routes
- ❌ No ProtectedRoute component
- ❌ All routes accessible without authentication
- ❌ localStorage.getItem('token') exists but unused

### What Should Be
- Protected routes should check auth token
- Redirect to login if token missing
- Token validation on route entry
- Logout should clear routes

---

## API CLIENT USAGE

### api.ts Methods

```typescript
api.get<T>(path)        // Defined but unused
api.post<T>(path, data) // Defined but unused
api.put<T>(path, data)  // Defined but unused
api.delete(path)        // Defined but unused
```

### Usage In Pages

- ❌ Dashboard: Not used (mock data)
- ❌ Engagements: Not used (mock data)
- ❌ Assets: Not used (mock data)
- ❌ Scans: Not used (mock data)
- ❌ Findings: Not used (mock data)
- ❌ Evidence: Not used (mock data)
- ❌ Reports: Not used (mock data)
- ❌ Settings: Not used (mock data)

---

## SUMMARY

**Frontend Routes**: 8 working (display only)  
**Backend Routes**: 30 defined (1 import error blocks all)  
**Connection**: 0% integrated  
**Navigation**: ✅ Works locally, ❌ doesn't fetch real data

**Route Readiness**:
- ✅ All navigation works
- ✅ All pages render
- ✅ All components display
- ❌ No data fetching
- ❌ No API integration
- ❌ No auth enforcement

---

**Prepared by**: Principal QA Engineer  
**Status**: Routes exist but not connected
