# ReconHive - Quick Start Guide

**Date:** 2026-07-18  
**Status:** ✅ RUNNING

---

## 🚀 Access Points

### Frontend Dashboard
**URL:** http://localhost:3000

**Note:** Frontend may be starting. If port 3000 is unavailable, use:
- Alternative Frontend: Use API directly via http://localhost:8000/docs

### API Server (FastAPI)
**URL:** http://localhost:8000
**Interactive Docs:** http://localhost:8000/docs
**ReDoc Docs:** http://localhost:8000/redoc

### Database Administration
**PgAdmin:** http://localhost:5050
- Email: admin@reconhive.local
- Password: admin

**Adminer:** http://localhost:8080
- System: PostgreSQL
- Server: postgres
- User: reconhive_user
- Password: secure_password_change_me
- Database: reconhive

### Redis Cache
**URL:** localhost:6379
- Used for task queue and caching

### Monitoring & Metrics
**Prometheus:** http://localhost:9090
**Mail Sandbox:** http://localhost:8025 (MailPit)

---

## 📋 Testing URLs

### Add Testing URLs to ReconHive

**Via API:**

```bash
# 1. Start a reconnaissance scan
curl -X POST http://localhost:8000/api/v1/recon/start \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "engagement_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Response:
# {
#   "scan_id": "550e8400-e29b-41d4-a716-446655440001",
#   "target": "example.com",
#   "status": "queued",
#   "phases": 11
# }
```

**Via Dashboard:**

1. Open http://localhost:3000
2. Navigate to **New Scan** or **Engagements**
3. Click **Create Engagement**
4. Enter target domain (e.g., `example.com`)
5. Select **Start Reconnaissance**

---

## 🔍 Proof Validation Endpoints

### Validate SQL Injection

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/sql_injection \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/search",
    "parameter": "q",
    "method": "GET"
  }'
```

**Response:**
```json
{
  "vulnerability_type": "sql_injection",
  "affected_url": "https://example.com/search",
  "affected_parameter": "q",
  "status": "confirmed",
  "is_valid": true,
  "confidence_score": 0.95,
  "severity": "high",
  "owasp_category": "A03: Injection",
  "payload_used": "' OR '1'='1"
}
```

### Validate XSS

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/comment",
    "parameter": "text",
    "xss_type": "reflected"
  }'
```

### Validate SSRF

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/ssrf \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/proxy",
    "parameter": "url"
  }'
```

### Get Available Payloads

```bash
# List all payload categories
curl http://localhost:8000/api/v1/validation/payloads

# Get SQL injection payloads
curl "http://localhost:8000/api/v1/validation/payloads/sql_injection"

# Get MySQL-specific payloads
curl "http://localhost:8000/api/v1/validation/payloads/sql_injection?subcategory=mysql"

# Get XSS reflected payloads
curl "http://localhost:8000/api/v1/validation/payloads/xss?subcategory=reflected"

# Get SSRF payloads
curl "http://localhost:8000/api/v1/validation/payloads/ssrf"
```

---

## 📊 Reconnaissance Workflow

### Step 1: Start Scan
```bash
curl -X POST http://localhost:8000/api/v1/recon/start \
  -d '{"target": "example.com"}'
```

### Step 2: Execute Workflow
```bash
curl -X POST http://localhost:8000/api/v1/recon/execute/{scan_id}
```

### Step 3: Get Status
```bash
curl http://localhost:8000/api/v1/recon/status/{scan_id}
```

### Step 4: Validate Findings
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/{vuln_type} \
  -d '{
    "target_url": "https://example.com",
    "parameter": "id"
  }'
```

### Step 5: Get Report
```bash
curl http://localhost:8000/api/v1/recon/results/{scan_id}
```

---

## 🛠️ Available Tools & Features

### Reconnaissance Phases (11 Total)
1. Asset Discovery (subdomains)
2. URL Collection (historical)
3. DNS Analysis (resolution)
4. Web Discovery (alive hosts)
5. Technology Detection (fingerprinting)
6. JavaScript Analysis (endpoints)
7. API Discovery (documentation)
8. Parameter Discovery (hidden)
9. Content Discovery (directories)
10. Network Discovery (ports)
11. Validation (vulnerabilities)

### Validators (3 Implemented)
- ✅ SQL Injection
- ✅ Cross-Site Scripting (XSS)
- ✅ Server-Side Request Forgery (SSRF)

**Planned:** BOLA/IDOR, XXE, SSTI, LFI/RFI, Open Redirect, File Upload, API Auth, Crypto Failures

### Payload Library
- **Total Payloads:** 183+
- **Categories:** 15+
- **SQL Databases:** 5 (MySQL, PostgreSQL, MSSQL, Oracle, SQLite)
- **Template Engines:** 5 (Jinja2, Twig, ERB, FreeMarker, Velocity)
- **Cloud Providers:** 4 (AWS, GCP, Azure, DigitalOcean)

---

## 🔒 Authorization & Safety

All validations are **non-exploitative**:
- ✅ Tests vulnerability existence
- ✅ Captures evidence (requests, responses)
- ✅ No data exfiltration
- ✅ No privilege escalation
- ✅ No system modification
- ✅ Read-only proof-of-concept

---

## 📈 Monitoring & Debugging

### Check API Health
```bash
curl http://localhost:8000/health
```

### View API Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Monitor Database
```bash
# Via PgAdmin: http://localhost:5050
# Via Adminer: http://localhost:8080
```

### Check Metrics
```bash
curl http://localhost:9090/api/v1/targets
```

### View Logs
```bash
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f frontend
```

---

## 🧪 Example Test Targets

**OWASP WebGoat:**
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/sql_injection \
  -d '{
    "target_url": "http://your-webgoat-instance/WebGoat",
    "parameter": "id"
  }'
```

**DVWA (Damn Vulnerable Web App):**
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -d '{
    "target_url": "http://your-dvwa-instance/vulnerabilities/xss_r/",
    "parameter": "name",
    "xss_type": "reflected"
  }'
```

**Juice Shop:**
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/ssrf \
  -d '{
    "target_url": "http://your-juice-shop:3000/api/proxy",
    "parameter": "url"
  }'
```

---

## 🚨 Troubleshooting

### Port 3000 Already in Use
```bash
# Use API directly via http://localhost:8000/docs
# Or kill the process using port 3000
lsof -i :3000
kill -9 <PID>
```

### Database Connection Error
```bash
# Restart database
docker-compose restart postgres
```

### API Unhealthy
```bash
# Check logs
docker-compose logs api

# Rebuild container
docker-compose build --no-cache api
docker-compose up -d api
```

### Frontend Not Starting
```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📚 Documentation

- **CLAUDE_RULES.md** - Development governance
- **VALIDATION_ENGINE_SUMMARY.md** - Proof validation engine details
- **SECURITY_SKILLS_MANIFEST.md** - Security assessment skills
- **PHASE_COMPLETION_SUMMARY.md** - Build completion status

---

## ✅ Quick Checklist

- [ ] API running at http://localhost:8000
- [ ] Database connected (PgAdmin at http://localhost:5050)
- [ ] Redis cache active (localhost:6379)
- [ ] Validation engine ready
- [ ] Payload library loaded (183+ payloads)
- [ ] Example test executed

---

## 🔗 Key Endpoints Summary

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | ReconHive Dashboard |
| **API** | http://localhost:8000 | REST API Server |
| **API Docs** | http://localhost:8000/docs | Interactive Documentation |
| **Database Admin** | http://localhost:5050 | PgAdmin |
| **Database Browser** | http://localhost:8080 | Adminer |
| **Monitoring** | http://localhost:9090 | Prometheus Metrics |
| **Mail Sandbox** | http://localhost:8025 | MailPit |

---

**Ready to test!** 🚀

Start with a test URL and monitor progress via the API or dashboard.

