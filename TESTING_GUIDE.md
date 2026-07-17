# ReconHive - Complete Testing & Validation Guide

**Date:** 2026-07-18  
**Status:** ✅ ALL SERVICES RUNNING  
**Version:** 3.0.0 (Phase 4.5 Complete)

---

## 🚀 SERVICE ENDPOINTS - READY TO USE

### **PRIMARY DASHBOARD & API**

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **API Server** | http://localhost:8000 | ✅ Running | Main REST API |
| **API Documentation** | http://localhost:8000/docs | ✅ Active | Interactive Swagger UI |
| **ReDoc Docs** | http://localhost:8000/redoc | ✅ Active | Alternative API docs |
| **Health Check** | http://localhost:8000/health | ✅ Healthy | Service status |

### **DATABASE MANAGEMENT**

| Service | URL | Status | Credentials |
|---------|-----|--------|-------------|
| **PgAdmin** | http://localhost:5050 | ✅ Running | admin@reconhive.local / admin |
| **Adminer** | http://localhost:8080 | ✅ Running | PostgreSQL / reconhive_user |
| **Direct DB** | postgres:5432 | ✅ Healthy | reconhive_user / secure_password_change_me |

### **INFRASTRUCTURE**

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **Redis Cache** | localhost:6379 | ✅ Running | Task queue & caching |
| **Prometheus** | http://localhost:9090 | ✅ Running | Metrics & monitoring |
| **MailPit** | http://localhost:8025 | ✅ Running | Email sandbox |

---

## 🎯 HOW TO ADD & TEST URLs

### **METHOD 1: Via API (Recommended)**

#### Start a Reconnaissance Scan

```bash
curl -X POST http://localhost:8000/api/v1/recon/start \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "engagement_id": "550e8400-e29b-41d4-a716-446655440000",
    "scan_name": "Example.com Assessment"
  }'
```

**Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440001",
  "target": "example.com",
  "status": "queued",
  "phases": 11,
  "message": "Reconnaissance workflow queued"
}
```

#### Execute the Reconnaissance Workflow

```bash
curl -X POST http://localhost:8000/api/v1/recon/execute/550e8400-e29b-41d4-a716-446655440001
```

#### Check Scan Status

```bash
curl http://localhost:8000/api/v1/recon/status/550e8400-e29b-41d4-a716-446655440001
```

#### Get Scan Results

```bash
curl http://localhost:8000/api/v1/recon/results/550e8400-e29b-41d4-a716-446655440001
```

---

### **METHOD 2: Via Interactive API Docs**

1. Open **http://localhost:8000/docs**
2. Look for **"recon"** endpoints section
3. Click **"Try it out"** on `/api/v1/recon/start`
4. Enter target domain (e.g., `example.com`)
5. Click **"Execute"**
6. Save the `scan_id` from response
7. Use `scan_id` to check status and results

---

## 🔍 PROOF VALIDATION ENGINE - TEST VULNERABILITIES

### **SQL Injection Validation**

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/sql_injection \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/search",
    "parameter": "q",
    "method": "GET"
  }'
```

**Tests:**
- ✅ Error-based SQLi (SQL error messages)
- ✅ Boolean-based blind SQLi (response differences)
- ✅ Time-based blind SQLi (SLEEP payloads)
- ✅ Union-based SQLi (column enumeration)

---

### **XSS Validation**

**Reflected XSS:**
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/comment",
    "parameter": "text",
    "xss_type": "reflected"
  }'
```

**Stored XSS:**
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/post",
    "parameter": "body",
    "xss_type": "stored"
  }'
```

**DOM XSS:**
```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/search",
    "parameter": "query",
    "xss_type": "dom"
  }'
```

---

### **SSRF Validation**

```bash
curl -X POST http://localhost:8000/api/v1/validation/validate/ssrf \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/proxy",
    "parameter": "url"
  }'
```

**Tests:**
- ✅ Localhost/127.0.0.1 access
- ✅ Cloud metadata endpoints (AWS, GCP, Azure)
- ✅ Internal service detection (Redis, MongoDB, MySQL)
- ✅ Response timing analysis

---

## 📚 PAYLOAD LIBRARY ACCESS

### **Get All Payload Categories**

```bash
curl http://localhost:8000/api/v1/validation/payloads
```

**Response:**
```json
{
  "categories": {
    "sql_injection": 33,
    "xss": 22,
    "ssrf": 19,
    "command_injection": 19,
    "ssti": 16,
    ...
  },
  "total_payloads": 183
}
```

### **Get SQL Injection Payloads**

```bash
# All databases
curl http://localhost:8000/api/v1/validation/payloads/sql_injection

# MySQL-specific
curl "http://localhost:8000/api/v1/validation/payloads/sql_injection?subcategory=mysql"

# PostgreSQL-specific
curl "http://localhost:8000/api/v1/validation/payloads/sql_injection?subcategory=postgresql"

# MSSQL-specific
curl "http://localhost:8000/api/v1/validation/payloads/sql_injection?subcategory=mssql"
```

### **Get XSS Payloads**

```bash
# Reflected XSS
curl "http://localhost:8000/api/v1/validation/payloads/xss?subcategory=reflected"

# Stored XSS
curl "http://localhost:8000/api/v1/validation/payloads/xss?subcategory=stored"

# DOM XSS
curl "http://localhost:8000/api/v1/validation/payloads/xss?subcategory=dom"

# Polyglot XSS
curl "http://localhost:8000/api/v1/validation/payloads/xss?subcategory=polyglot"
```

### **Get SSRF Payloads**

```bash
# Localhost payloads
curl "http://localhost:8000/api/v1/validation/payloads/ssrf?subcategory=localhost"

# Cloud metadata
curl "http://localhost:8000/api/v1/validation/payloads/ssrf?subcategory=cloud_metadata"

# Internal services
curl "http://localhost:8000/api/v1/validation/payloads/ssrf?subcategory=internal_services"

# Bypass techniques
curl "http://localhost:8000/api/v1/validation/payloads/ssrf?subcategory=bypass"
```

### **Get Other Payloads**

```bash
# Command Injection
curl http://localhost:8000/api/v1/validation/payloads/command_injection

# SSTI
curl http://localhost:8000/api/v1/validation/payloads/ssti

# Path Traversal
curl http://localhost:8000/api/v1/validation/payloads/path_traversal

# XXE
curl http://localhost:8000/api/v1/validation/payloads/xxe

# LDAP Injection
curl http://localhost:8000/api/v1/validation/payloads/ldap_injection

# Open Redirect
curl http://localhost:8000/api/v1/validation/payloads/open_redirect
```

---

## 📊 VALIDATION RESULTS

### **Understanding Validation Responses**

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
  "payload_used": "' OR '1'='1",
  "reproduction_steps": [
    "1. Send GET /search?q=' OR '1'='1",
    "2. Observe SQL error message in response",
    "3. Confirm injection point"
  ],
  "evidence": [
    {
      "type": "response",
      "description": "SQL error message indicating injection point"
    }
  ],
  "remediation": "Use parameterized queries or prepared statements",
  "validated_at": "2026-07-18T00:00:00",
  "validated_by": "analyzer"
}
```

**Key Fields:**
- **status**: `detected`, `needs_review`, `reproduced`, `confirmed`, `client_verified`
- **confidence_score**: 0.0-1.0 (higher = more certain)
- **is_valid**: `true` if vulnerability confirmed
- **severity**: `critical`, `high`, `medium`, `low`, `informational`
- **owasp_category**: Mapped to OWASP Top 10 2025

---

## 🧪 EXAMPLE TEST SCENARIOS

### **Test 1: SQLi on Web Application**

```bash
# 1. Validate SQL injection
curl -X POST http://localhost:8000/api/v1/validation/validate/sql_injection \
  -d '{
    "target_url": "https://vulnerable-app.local/users",
    "parameter": "id",
    "method": "GET"
  }'

# 2. Get MySQL payloads
curl "http://localhost:8000/api/v1/validation/payloads/sql_injection?subcategory=mysql"

# 3. View results
# Check confidence_score and is_valid fields
```

### **Test 2: XSS in User Input**

```bash
# 1. Validate reflected XSS
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -d '{
    "target_url": "https://vulnerable-app.local/search",
    "parameter": "q",
    "xss_type": "reflected"
  }'

# 2. Get XSS payloads
curl "http://localhost:8000/api/v1/validation/payloads/xss?subcategory=reflected"

# 3. Analyze vulnerability
```

### **Test 3: SSRF in URL Parameter**

```bash
# 1. Validate SSRF
curl -X POST http://localhost:8000/api/v1/validation/validate/ssrf \
  -d '{
    "target_url": "https://vulnerable-app.local/fetch",
    "parameter": "url"
  }'

# 2. Get SSRF payloads
curl "http://localhost:8000/api/v1/validation/payloads/ssrf"

# 3. Check for metadata access or internal service detection
```

### **Test 4: Batch Validation**

```bash
# Validate multiple findings at once
curl -X POST http://localhost:8000/api/v1/validation/validate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "findings": [
      {
        "vulnerability_type": "sql_injection",
        "target_url": "https://app.local/search",
        "parameter": "q"
      },
      {
        "vulnerability_type": "xss",
        "target_url": "https://app.local/comment",
        "parameter": "text"
      },
      {
        "vulnerability_type": "ssrf",
        "target_url": "https://app.local/proxy",
        "parameter": "url"
      }
    ]
  }'
```

---

## 📈 MONITORING & TRACKING

### **Get Validation History**

```bash
# Last 100 validations
curl "http://localhost:8000/api/v1/validation/history?limit=100"

# Pagination
curl "http://localhost:8000/api/v1/validation/history?limit=50&offset=100"
```

### **Get Validation Statistics**

```bash
curl http://localhost:8000/api/v1/validation/stats
```

**Response:**
```json
{
  "total_validations": 45,
  "confirmed": 38,
  "accuracy": 84.4,
  "by_type": {
    "sql_injection": 15,
    "xss": 20,
    "ssrf": 10
  },
  "by_severity": {
    "critical": 5,
    "high": 18,
    "medium": 15,
    "low": 7
  }
}
```

---

## 🔐 SAFETY & AUTHORIZATION

**All validators operate in NON-EXPLOITATIVE mode:**

✅ **SAFE OPERATIONS:**
- Test vulnerability existence
- Capture evidence (responses, headers, timing)
- Generate confidence scores
- Document reproduction steps
- Provide remediation guidance

❌ **NEVER:**
- Extract data from databases
- Execute malicious code
- Modify application data
- Escalate privileges
- Create persistence
- Exfiltrate credentials

**Authorization Required:**
- Written authorization for all testing
- Scoped engagement boundaries
- Safe harbor confirmation
- Audit logging enabled
- Results tracked for compliance

---

## 📲 QUICK COMMAND REFERENCE

```bash
# Health check
curl http://localhost:8000/health

# View available agents
curl http://localhost:8000/api/v1/recon/list-agents

# Start scan
curl -X POST http://localhost:8000/api/v1/recon/start -d '{"target":"example.com"}'

# Get payloads
curl http://localhost:8000/api/v1/validation/payloads

# Validate SQLi
curl -X POST http://localhost:8000/api/v1/validation/validate/sql_injection \
  -d '{"target_url":"https://example.com","parameter":"id"}'

# Validate XSS
curl -X POST http://localhost:8000/api/v1/validation/validate/xss \
  -d '{"target_url":"https://example.com","parameter":"q","xss_type":"reflected"}'

# Validate SSRF
curl -X POST http://localhost:8000/api/v1/validation/validate/ssrf \
  -d '{"target_url":"https://example.com","parameter":"url"}'

# Get stats
curl http://localhost:8000/api/v1/validation/stats

# Get history
curl http://localhost:8000/api/v1/validation/history
```

---

## 🎯 NEXT STEPS

1. **Choose Target URL** (e.g., example.com or vulnerable test app)
2. **Pick Testing Method:**
   - Via API: Use curl commands above
   - Via Dashboard: Open http://localhost:8000/docs
   - Via PgAdmin: Monitor database changes at http://localhost:5050
3. **Select Validators:**
   - SQL Injection (3 variants tested)
   - XSS (3 types tested)
   - SSRF (4 categories tested)
4. **Review Results:**
   - Check confidence scores
   - Read reproduction steps
   - Review remediation guidance
5. **Track Progress:**
   - Use `/validation/stats` for metrics
   - Use `/validation/history` for audit trail

---

## 📞 SUPPORT URLS

| Resource | URL |
|----------|-----|
| API Health | http://localhost:8000/health |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc Docs | http://localhost:8000/redoc |
| Database Admin | http://localhost:5050 |
| Database Browser | http://localhost:8080 |
| Metrics | http://localhost:9090 |
| Email Sandbox | http://localhost:8025 |

---

**Status:** ✅ **ALL SYSTEMS OPERATIONAL**

ReconHive is ready for authorized security testing. Use the URLs above to add your test targets and validate vulnerabilities.

