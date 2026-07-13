# SECURITY REVIEW: ReconHive Authentication & Access Control

**Assessment Date**: 2026-07-13  
**Grade**: B (7.5/10) — Strong foundation, RBAC gaps must be closed before v1.0

---

## SECURITY POSTURE SCORECARD

| Area | Status | Score | Notes |
|------|--------|-------|-------|
| **Authentication** | ✅ Strong | 9/10 | JWT tokens, secure defaults |
| **Authorization (RBAC)** | ⚠️ Weak | 4/10 | Admin-only, no role decorators |
| **Input Validation** | ✅ Strong | 9/10 | Pydantic strict mode |
| **SQL Injection** | ✅ Protected | 10/10 | SQLAlchemy ORM, no raw SQL |
| **CORS** | ⚠️ Permissive | 5/10 | Allows `*`, should restrict |
| **Rate Limiting** | ❌ Missing | 0/10 | Not implemented |
| **Audit Logging** | ✅ Excellent | 9/10 | 20 event types captured |
| **Session Management** | ✅ Good | 8/10 | JWT, HttpOnly cookies |
| **Secrets Management** | ⚠️ Partial | 7/10 | Keychain for sensitive, env for config |
| **TLS/HTTPS** | ⚠️ To-do | 6/10 | No HTTPS in dev, must add in prod |

**Overall**: **B (7.5/10)** — Production-grade backend, auth needs hardening

---

## 1. AUTHENTICATION ✅

### JWT Token Implementation

**Token Format**:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin" | "analyst" | "viewer",
  "exp": 1626266400,
  "iat": 1626252000
}
```

**Algorithm**: HS256 (HMAC-SHA256)  
**Secret Storage**: `JWT_SECRET_KEY` environment variable  
**Expiration**: 24 hours (configurable)  
**Validation**: On every protected endpoint

**Code Pattern**:
```python
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
```

**Strength**: ✅
- Tokens signed, cannot be tampered with
- Expiration enforced
- Secret stored outside code

**Gaps**: ⚠️
- No token refresh mechanism (reuse 24h token)
- No token revocation list (logout doesn't invalidate existing tokens)

---

### Optional: API Key Authentication

**Configured but optional**:
```python
if SETTINGS.api_key_enabled:
    # Accept X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key != SETTINGS.api_key:
        raise HTTPException(status_code=401)
```

**Use Case**: Service-to-service or CI/CD automation

---

## 2. AUTHORIZATION (RBAC) ⚠️ CRITICAL GAP

### Current State: Admin-Only

**All protected endpoints require authentication, but**:
- No role-based access control decorators
- No per-engagement permissions
- No fine-grained scopes
- Analysts can do everything admins can do

**Example vulnerability**:
```python
@app.post("/engagements")
async def create_engagement(
    engagement: EngagementCreate,
    current_user = Depends(get_current_user)  # Only checks auth, not role
):
    # VULNERABLE: Any authenticated user can create engagement
    # Should check: if current_user.role != "admin"
```

### Phase 5b: Required Decorator Pattern

**Recommended implementation**:
```python
from functools import wraps

def require_role(*allowed_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.post("/engagements")
@require_role("admin")  # Only admins can create
async def create_engagement(...):
    ...

@app.get("/engagements")
@require_role("admin", "analyst")  # Admins and analysts can view
async def list_engagements(...):
    ...
```

### Scopes to Implement

| Scope | Target | Use Case |
|-------|--------|----------|
| `engagements:create` | Admin only | Create new engagement |
| `engagements:read` | Admin, Analyst | View engagements |
| `engagements:update` | Admin, Engagement Owner | Modify engagement |
| `findings:create` | Analyst | Submit findings |
| `findings:approve` | Admin | Approve findings for reporting |
| `reports:generate` | Analyst | Download findings report |
| `config:manage` | Admin | Plugin configuration |

---

## 3. INPUT VALIDATION ✅

### Pydantic v2 Strict Mode

All request bodies validated with Pydantic schemas:

```python
from pydantic import BaseModel, Field, validator

class EngagementCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    target: str
    objective: EngagementObjective  # Enum
    scope: dict = Field(default_factory=dict)
    
    @validator('name')
    def name_must_be_unique(cls, v):
        # Custom validation
        if Engagement.query.filter_by(name=v).first():
            raise ValueError("Name already exists")
        return v
    
    class Config:
        extra = "forbid"  # Reject unknown fields
```

**Validation Coverage**:
- ✅ Type checking (int, str, enum)
- ✅ Length limits (min/max)
- ✅ Format validation (email, URL, CIDR)
- ✅ Enum validation (status, objective)
- ✅ Custom validators
- ✅ Rejection of unknown fields

**Strength**: ✅ Excellent

---

## 4. SQL INJECTION PROTECTION ✅

### SQLAlchemy ORM (No Raw SQL)

**Safe**:
```python
# ORM query (parameterized)
finding = session.query(Finding).filter(Finding.id == id).first()
# Generated SQL: SELECT * FROM findings WHERE id = %s;
# Parameters: [id]
```

**NOT used** (verified by code review):
- No raw SQL strings
- No f-string interpolation in queries
- No `execute(sql_string % user_input)`

**Codebase**: 100% ORM usage across 9 services

**Strength**: ✅ Excellent

---

## 5. CORS (Cross-Origin Resource Sharing) ⚠️

### Current: Permissive

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ DANGEROUS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Vulnerability**:
- Any website can make authenticated requests to ReconHive API
- Enables CSRF attacks: attacker.com makes request to api.reconhive.com/findings as logged-in user

### Fix for Production

```python
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://app.example.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # ✅ Specific domain only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Not all methods
    allow_headers=["authorization", "content-type"],  # Not all headers
    max_age=3600,  # Preflight cache limit
)
```

**Phase 5c Task**: Update CORS to restrict to frontend domain

---

## 6. RATE LIMITING ❌

### Current: NOT Implemented

**Risk**: API vulnerable to brute force, DoS

**Recommended implementation** (Phase 5c):
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(credentials: Credentials):
    ...

@app.get("/findings")
@limiter.limit("100/minute")  # Standard API rate limit
async def list_findings(...):
    ...
```

**Suggested Limits**:
- Login: 5 attempts/minute
- API (read): 100 requests/minute
- API (write): 20 requests/minute
- File uploads: 5 files/minute

---

## 7. AUDIT LOGGING ✅

### Event Timeline: 20 Activity Types

Every action logged to `event_log` table:

```python
ACTIVITY_TYPES = [
    "engagement_created",
    "engagement_updated",
    "engagement_deleted",
    "asset_added",
    "target_scoped",
    "scan_started",
    "scan_completed",
    "job_queued",
    "job_completed",
    "finding_created",
    "finding_confirmed",
    "finding_remediated",
    "evidence_uploaded",
    "config_created",
    "config_updated",
    "config_activated",
    "user_created",
    "user_updated",
    "access_granted",
    "access_denied"
]
```

**Schema**:
```sql
event_log {
  id, activity_type, entity_id, entity_type, user_id, 
  description, metadata (JSON), created_at
}
```

**Strength**: ✅ Excellent — all mutations tracked with user attribution

---

## 8. SESSION MANAGEMENT ✅

### JWT (Stateless)

**Advantages**:
- No session state on server
- Scales horizontally
- Can be used across services

**Secure Defaults**:
```python
response = JSONResponse({"access_token": token})
response.set_cookie(
    key="Authorization",
    value=f"Bearer {token}",
    httponly=True,  # ✅ JS cannot read (XSS protection)
    secure=True,    # ✅ HTTPS only
    samesite="Strict",  # ✅ CSRF protection
    max_age=86400   # ✅ 24 hours
)
```

**Strength**: ✅ Good

### Gaps

- No session revocation (logout doesn't invalidate token)
- No refresh token mechanism (24h reuse)

---

## 9. SECRETS MANAGEMENT ⚠️

### Keychain Integration

Sensitive secrets stored in system keychain (not code, not .env):

```python
# internal/keychain.py
def get_secret(name: str) -> str:
    # macOS: reads from Keychain
    # Windows: reads from Credential Manager
    # Linux: reads from pass / KeePassXC
    
def set_secret(name: str, value: str):
    # Store securely
```

**Used for**:
- `JWT_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `DATABASE_PASSWORD`
- API keys for external services (future)

**NOT used for** (in .env):
- `CORS_ORIGINS`
- `REDIS_URL`
- Non-sensitive config

**Strength**: ✅ Good for development

**Production Gap**: ⚠️
- Keychain not suitable for servers (no automated retrieval)
- Recommendation: Use HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault

---

## 10. TLS/HTTPS ⚠️

### Current: Unencrypted HTTP

**Development**: OK (localhost)  
**Production**: ❌ MUST use HTTPS

**Implementation**:
- Self-signed cert in dev: `mkcert localhost`
- Let's Encrypt in prod: automatic via certbot/docker-compose

**Required Before v1.0**:
```yaml
# docker-compose.yml
api:
  environment:
    - HTTPS=true
    - CERT_FILE=/etc/certs/cert.pem
    - KEY_FILE=/etc/certs/key.pem
```

---

## 11. SCOPE ENFORCEMENT ✅

### Engagement Scope Validation

All scans must respect configured scope:

```python
class EngagementScope:
    include_domains: List[str]      # *.example.com
    exclude_paths: List[str]        # /admin/*
    cidr_ranges: List[str]          # 192.168.1.0/24
    
def is_target_in_scope(target: str, scope: EngagementScope) -> bool:
    # Check against include/exclude lists
    # Prevent scanning out-of-scope assets
```

**Strength**: ✅ Good

---

## 12. DEPENDENCY VULNERABILITIES

### Current Packages (Python)

**High-Risk Dependencies** (Phase 5b audit):
```
FastAPI 0.109.0
SQLAlchemy 2.0.24
Pydantic 2.0.x
python-jose 3.x
```

**Recommended**: Run `pip-audit` weekly
```bash
pip-audit --fix
```

---

## ATTACK SURFACE MAP

```
External Attack Surface:
├── JWT token brute force
│   └── Mitigated: 256-bit secret, HMAC-SHA256
├── API endpoint enumeration
│   └── Mitigated: Clear endpoint docs (intentional)
├── IDOR (Insecure Direct Object References)
│   └── Gap: No role-based filtering per endpoint
├── CSRF (Cross-Site Request Forgery)
│   └── Partially: JWT in header (safe), CORS too broad (risky)
├── SQL Injection
│   └── Protected: SQLAlchemy ORM only
├── XSS (Cross-Site Scripting)
│   └── Protected: No user-generated HTML rendered
└── Rate Limit Bypass
    └── Gap: No rate limiting
```

---

## THREAT MODEL

### High-Risk Scenarios

**1. Unauthorized Access to Engagement Data**
- **Threat**: Analyst accesses another company's engagement
- **Current State**: ⚠️ All authenticated users see all data
- **Fix**: RBAC with engagement-level permissions (Phase 5b)

**2. Privilege Escalation**
- **Threat**: Analyst modifies finding status without approval
- **Current State**: ⚠️ No role-based endpoint protection
- **Fix**: `@require_role("admin")` decorators

**3. API Abuse / DoS**
- **Threat**: Attacker floods API with requests
- **Current State**: ❌ No rate limiting
- **Fix**: slowapi library implementation (Phase 5c)

**4. Session Hijacking**
- **Threat**: Attacker intercepts JWT token
- **Current State**: ⚠️ Mitigated by secure cookie flags
- **Fix**: HTTPS mandatory in production

---

## COMPLIANCE CHECKLIST

| Requirement | Status | Notes |
|-------------|--------|-------|
| OWASP Top 10 (2021) A01 — Broken Access Control | ⚠️ Partial | RBAC missing |
| OWASP Top 10 (2021) A02 — Cryptographic Failures | ✅ OK | TLS in prod, JWT signed |
| OWASP Top 10 (2021) A03 — Injection | ✅ OK | No SQL injection |
| OWASP Top 10 (2021) A04 — Insecure Design | ⚠️ Partial | No security by design in RBAC |
| OWASP Top 10 (2021) A05 — Security Misconfiguration | ⚠️ Partial | CORS too broad |
| OWASP Top 10 (2021) A07 — Identification & Authentication | ⚠️ Partial | No MFA |
| OWASP Top 10 (2021) A09 — Logging & Monitoring | ✅ OK | 20 event types logged |

---

## REMEDIATION ROADMAP

### Phase 5b (Next week)

- [ ] Implement RBAC decorators
- [ ] Add `@require_role()` to all endpoints
- [ ] Define engagement-level permission scopes
- [ ] Add role decorators to service layer

### Phase 5c (Week 3)

- [ ] Implement rate limiting (slowapi)
- [ ] Restrict CORS to specific domain
- [ ] Add HTTPS to docker-compose
- [ ] Implement token refresh mechanism

### Phase 5d / v1.0

- [ ] Add MFA (TOTP via pyotp)
- [ ] Implement session revocation list
- [ ] Database secrets rotation
- [ ] Penetration test by external firm

---

## SECURITY GRADE: B (7.5/10)

**Strengths**:
- ✅ JWT authentication solid
- ✅ SQL injection protected
- ✅ Comprehensive audit logging
- ✅ Secure session management defaults

**Gaps (Must fix before v1.0)**:
- ⚠️ RBAC not implemented
- ⚠️ CORS too permissive
- ⚠️ No rate limiting
- ⚠️ No HTTPS in current setup

**Gaps (Nice to have)**:
- MFA (two-factor authentication)
- Session revocation
- Penetration testing

---

Prepared by: Staff Security Engineer  
Date: 2026-07-13
