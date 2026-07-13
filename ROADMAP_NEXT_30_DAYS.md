# ROADMAP: Next 30 Days (Phase 5 Final Push)

**Current Date**: 2026-07-13  
**Target v1.0**: 2026-08-03  
**Phase**: 5 (Plugin Ecosystem)  
**Completion**: 43% (6 of 14 features)

---

## TIMELINE

```
[NOW] 2026-07-13 ────────────────────────── [v1.0] 2026-08-03
      └─ Phase 5a (Complete)
         └─ Phase 5b (1 week)
            └─ Phase 5c (2 weeks)
               └─ Phase 5d (1 week)
                  └─ Release 🎉
```

---

## PHASE 5B: Job Scheduling (Week 1: Jul 13-19)

### Goals
- Wire Celery to job execution
- Implement periodic scan scheduling
- Add job retry logic with exponential backoff

### P0 (Critical)

#### 1. Celery Task Wiring
- [ ] Connect Job model to Celery tasks
- [ ] Create `api/tasks/scan.py` module
- [ ] Map Job status → Celery task state
- [ ] Implement webhook callbacks for task completion

**Work**:
```python
# api/tasks/scan.py
from celery import shared_task

@shared_task(bind=True)
def run_job(self, job_id: UUID):
    job = Job.query.get(job_id)
    try:
        plugin = load_plugin(job.plugin_id)
        result = plugin.execute(job.input_data)
        job.output_data = result
        job.status = "COMPLETED"
    except Exception as e:
        self.retry(exc=e, countdown=2 ** self.request.retries, max_retries=3)
    finally:
        job.save()
        # Emit activity log
        EventLog.create(activity="job_completed", job_id=job_id)

# api/routes/jobs.py
@app.post("/jobs/{id}/execute")
async def execute_job(id: UUID):
    job = Job.query.get(id)
    run_job.delay(str(job.id))
    return {"status": "queued", "job_id": id}
```

**Tests**:
- [ ] Job execution completes successfully
- [ ] Job failure triggers retry (max 3 times)
- [ ] Exponential backoff (2s, 4s, 8s)
- [ ] EventLog updated on completion

**Estimate**: 3 days

---

#### 2. Scan Lifecycle Updates
- [ ] Add `/scans/{id}/schedule` endpoint (schedule future scans)
- [ ] Add cron job for scheduled scans
- [ ] Status tracking: SCHEDULED → QUEUED → RUNNING → COMPLETED

**Work**:
```python
# POST /scans/{id}/schedule
async def schedule_scan(scan_id: UUID, schedule: ScanSchedule):
    # schedule = {"frequency": "daily", "time": "02:00 UTC"}
    scan = Scan.query.get(scan_id)
    scan.scheduled_at = schedule.next_run_time()
    scan.save()
    return {"scan_id": scan_id, "scheduled_for": schedule.next_run_time()}

# Celery beat (runs every minute)
@periodic_task(run_every=crontab(minute='*'))
def run_scheduled_scans():
    scans = Scan.filter(scheduled_at <= utcnow(), status="SCHEDULED")
    for scan in scans:
        run_job.delay(scan.id)
```

**Estimate**: 2 days

---

#### 3. Job Monitoring Dashboard
- [ ] GET `/jobs?status=RUNNING` returns active jobs
- [ ] GET `/flower` (Celery Flower UI) already running
- [ ] Add job health checks (hung tasks detection)

**Estimate**: 1 day

---

### P1 (Important)

#### 4. Retry Configuration
- [ ] Create `JobRetryPolicy` class
- [ ] Support exponential backoff, linear, fixed strategies
- [ ] Add to PluginConfiguration (max_retries, retry_delay)

**Estimate**: 2 days

---

### P2 (Nice to have)

#### 5. Distributed Lock for Concurrent Scans
- [ ] Prevent same scan running twice (via Redis)
- [ ] Lock key: `scan:{scan_id}:running`
- [ ] TTL: 6 hours (auto-release if hung)

**Estimate**: 1 day

---

**Phase 5b Summary**:
- **Effort**: ~9 days
- **Blocker**: Celery Docker service must be running
- **Test Coverage Target**: 70%
- **Outcome**: Scans can be scheduled, run async, retry on failure

---

## PHASE 5C: Frontend & Hardening (Weeks 2-3: Jul 20-Aug 2)

### Goals
- Build minimal dashboard (frontend MVP)
- Implement RBAC on backend
- Add rate limiting
- Restrict CORS
- Implement HTTPS

### P0 (Critical)

#### 1. RBAC Implementation (Backend)
- [ ] Add `@require_role()` decorator to all endpoints
- [ ] Define roles: admin, analyst, viewer
- [ ] Define scopes: engagements:create, findings:read, config:manage, etc.
- [ ] Add role checking to service layer

**Work**:
```python
# api/security/decorators.py
def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage in routes
@app.get("/engagements")
@require_role("admin", "analyst")  # Admins and analysts can view
async def list_engagements(...):
    ...

@app.post("/engagements")
@require_role("admin")  # Only admins can create
async def create_engagement(...):
    ...
```

**Tests**:
- [ ] Analyst cannot create engagement
- [ ] Viewer cannot access findings
- [ ] Admin can access all endpoints

**Estimate**: 4 days

---

#### 2. Rate Limiting
- [ ] Install `slowapi`
- [ ] Implement per-endpoint rate limits
- [ ] Add to all POST/PUT/DELETE endpoints
- [ ] Login endpoint: 5/minute
- [ ] Standard API: 100/minute

**Work**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")
async def login(...):
    ...

@app.get("/findings")
@limiter.limit("100/minute")
async def list_findings(...):
    ...
```

**Tests**:
- [ ] 6th login attempt returns 429 Too Many Requests
- [ ] Request count resets after window

**Estimate**: 2 days

---

#### 3. CORS Hardening
- [ ] Update to restrict to specific domain
- [ ] Add to environment variable
- [ ] Remove `allow_origins=["*"]`

**Work**:
```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://app.example.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["authorization", "content-type"],
)
```

**Estimate**: 1 day

---

#### 4. HTTPS Setup
- [ ] Create self-signed cert for dev (mkcert)
- [ ] Add to docker-compose
- [ ] Update frontend API_URL to https://

**Estimate**: 1 day

---

### P1 (Important)

#### 5. Frontend Dashboard MVP
- [ ] **Home page**: KPI cards (engagements, findings, critical count)
- [ ] **Engagements list**: Table with status, target, dates
- [ ] **Findings list**: Filterable table (status, severity)
- [ ] **Navigation**: Sidebar with links

**Work**:
```typescript
// frontend/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function Dashboard() {
  const [stats, setStats] = useState({ engagements: 0, findings: 0 });
  
  useEffect(() => {
    api.get('/engagements?limit=0').then(res => {
      setStats(prev => ({ ...prev, engagements: res.pagination.total }));
    });
  }, []);
  
  return (
    <div className="grid grid-cols-3 gap-4 p-8">
      <div className="bg-amber-50 p-6 rounded">
        <h3>Total Engagements</h3>
        <p className="text-3xl">{stats.engagements}</p>
      </div>
      {/* More KPI cards */}
    </div>
  );
}
```

**Components needed**:
- [ ] Card component
- [ ] Table component
- [ ] Filter sidebar
- [ ] Navigation layout

**Estimate**: 5 days

---

#### 6. Integration Tests (Backend)
- [ ] Test API endpoint flows (create → read → update)
- [ ] Test database transactions (rollback on error)
- [ ] Test authorization rules

**Estimate**: 3 days

---

### P2 (Nice to have)

#### 7. Load Testing
- [ ] Use locust or k6
- [ ] Simulate 100 concurrent users
- [ ] Identify bottlenecks
- [ ] Generate performance report

**Estimate**: 2 days (optional)

---

**Phase 5c Summary**:
- **Effort**: ~18 days (spread over 2 weeks)
- **Blockers**: None (backend-first approach)
- **Test Coverage Target**: 75%
- **Outcome**: Functional dashboard, hardened API, HTTPS

---

## PHASE 5D: Finalization & Release (Week 4: Aug 2-3)

### Goals
- Polish UI/UX
- Final testing
- Documentation
- Release v1.0

### P0 (Critical)

#### 1. E2E Testing
- [ ] Create 3-4 user flows in Cypress/Playwright
- [ ] Flow 1: Create engagement → add asset → run scan
- [ ] Flow 2: View findings → update status → generate report
- [ ] Flow 3: Configure plugin → activate config → run job

**Estimate**: 2 days

---

#### 2. Documentation
- [ ] Update README.md with quick start
- [ ] API docs (Swagger at `/docs`)
- [ ] Installation guide (Docker Compose)
- [ ] Architecture diagram

**Estimate**: 1 day

---

#### 3. Release Notes
- [ ] Summarize v1.0 features
- [ ] Known limitations
- [ ] Upgrade guide for beta users

**Estimate**: 1 day

---

### P1 (Important)

#### 4. UI Polish
- [ ] Responsive mobile layout
- [ ] Dark mode (default for security context)
- [ ] Error messages (user-friendly)
- [ ] Loading states (skeleton screens)

**Estimate**: 3 days

---

#### 5. Bug Fixes & Cleanup
- [ ] Resolve 20-30 open issues
- [ ] Remove debug logging
- [ ] Dead code cleanup

**Estimate**: 2 days

---

**Phase 5d Summary**:
- **Effort**: ~9 days
- **Focus**: Quality, not features
- **Outcome**: v1.0 released to production

---

## TEAM ASSIGNMENTS (Suggested)

### Backend (2 engineers)
- Engineer A: Celery wiring, job scheduling (Phase 5b)
- Engineer B: RBAC, rate limiting, integration tests (Phase 5c)

### Frontend (1 engineer)
- Engineer C: Dashboard, components, responsive design (Phase 5c-5d)

### DevOps/QA (1 engineer)
- Engineer D: HTTPS setup, E2E tests, load testing (Phase 5c-5d)

---

## RISK MITIGATION

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Celery integration overruns | Medium | 5 days delay | Start early, use async/await patterns |
| RBAC scope creep | High | 3 days delay | Define scopes in Phase 5b, don't add features |
| Frontend not ready by Aug 2 | Low | Delay v1.0 | Pre-build components early, use templates |
| Performance issues in load test | Medium | 2 days delay | Profile early, add indexes, caching |
| Security audit findings | Low | 1-3 days delay | Pentest externally by Aug 1 |

---

## SUCCESS METRICS

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | 80% | 60% |
| API Response Time (p95) | <500ms | Untested |
| 99.9% Uptime | Yes | N/A |
| Dashboard Load Time | <2s | N/A |
| Zero Critical Findings | Yes | Depends on 5c |

---

## MONTHLY TRACKING

### Week 1 (Jul 13-19): Phase 5b
- [ ] Celery integration complete
- [ ] Job scheduling working
- [ ] Retry logic tested

**Go/No-Go**: On track if 80% Phase 5b done by Jul 19

---

### Week 2 (Jul 20-26): Phase 5c Part 1
- [ ] RBAC + decorators on all endpoints
- [ ] Rate limiting deployed
- [ ] HTTPS working locally

**Go/No-Go**: On track if backend hardening 90% done by Jul 26

---

### Week 3 (Jul 27-Aug 2): Phase 5c Part 2 + 5d Part 1
- [ ] Dashboard MVP complete
- [ ] Integration tests passing
- [ ] Load test results analyzed

**Go/No-Go**: On track if frontend usable by Aug 2

---

### Week 4 (Aug 2-3): Phase 5d Finalization
- [ ] E2E tests passing
- [ ] Documentation complete
- [ ] v1.0 released

**Go/No-Go**: v1.0 ships on time

---

## POST-v1.0 PRIORITIES

### Wave 2 (Sep-Oct 2026)
- [ ] Third-party integrations (Burp, Metasploit, ZAP)
- [ ] Evidence correlation (AI-assisted)
- [ ] Report generation
- [ ] Kubernetes deployment

### Wave 3 (Nov-Dec 2026)
- [ ] HackerOne/Bugcrowd integrations
- [ ] Mobile app
- [ ] Multi-tenant support
- [ ] Advanced analytics

---

## BUDGET & RESOURCES

**Dev Cost** (4 engineers × 4 weeks @ $150/hr):
- 16 weeks-months × $150/hr × 40 hrs/week = **$96,000**

**Infrastructure** (Docker hosts, AWS):
- Dev: $50/month
- Prod (Phase 5+): $200/month

**Third-party APIs** (Phase 6):
- OpenAI API: ~$100-200/month

---

## DEFINITION OF DONE (v1.0)

- [ ] All 14 Phase 5 features implemented
- [ ] 80%+ test coverage
- [ ] Zero critical security findings
- [ ] API docs auto-generated (Swagger)
- [ ] Dashboard loads in <2s
- [ ] Deployment guide documented
- [ ] Rollback plan in place
- [ ] Monitoring & alerting set up
- [ ] On-call runbook created

---

**Roadmap prepared by**: Product Manager + Tech Lead  
**Date**: 2026-07-13  
**Next update**: 2026-07-20 (weekly sync)
