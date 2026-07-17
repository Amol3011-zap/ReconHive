# ReconHive - Command Reference Card

**Status:** ✅ PRODUCTION LIVE  
**Date:** 2026-07-18

---

## 🎯 MAIN ENTRY POINTS

### **Dashboard (Web UI)**
```
http://127.0.0.1:3000
```
- Create engagements
- Add target URLs
- Monitor scans
- View findings
- Generate reports

### **API Documentation**
```
http://127.0.0.1:8000/docs
```
- Interactive endpoint testing
- Schema reference
- Live examples
- Request/response samples

### **Database Admin**
```
http://127.0.0.1:5050
```
- Username: admin@reconhive.local
- Password: admin

---

## 🔍 QUICK API COMMANDS

### **Start Reconnaissance Scan**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/recon/start \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "engagement_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### **Check Scan Status**
```bash
curl http://127.0.0.1:8000/api/v1/recon/status/{scan_id}
```

### **Get Scan Results**
```bash
curl http://127.0.0.1:8000/api/v1/recon/results/{scan_id}
```

### **Validate SQL Injection**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/validation/validate/sql_injection \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/search",
    "parameter": "q"
  }'
```

### **Validate XSS**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/validation/validate/xss \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/comment",
    "parameter": "text",
    "xss_type": "reflected"
  }'
```

### **Validate SSRF**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/validation/validate/ssrf \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/proxy",
    "parameter": "url"
  }'
```

### **Get Payloads**
```bash
# All payloads
curl http://127.0.0.1:8000/api/v1/validation/payloads

# SQL injection payloads
curl http://127.0.0.1:8000/api/v1/validation/payloads/sql_injection

# XSS payloads (reflected)
curl "http://127.0.0.1:8000/api/v1/validation/payloads/xss?subcategory=reflected"

# SSRF payloads
curl http://127.0.0.1:8000/api/v1/validation/payloads/ssrf
```

### **Get Validation Statistics**
```bash
curl http://127.0.0.1:8000/api/v1/validation/stats
```

### **Get Validation History**
```bash
curl "http://127.0.0.1:8000/api/v1/validation/history?limit=100"
```

---

## 🐳 DOCKER COMMANDS

### **Check All Services**
```bash
docker-compose ps
```

### **View API Logs**
```bash
docker-compose logs -f api
```

### **View Frontend Logs**
```bash
docker-compose logs -f frontend
```

### **View Database Logs**
```bash
docker-compose logs -f postgres
```

### **Restart All Services**
```bash
docker-compose restart
```

### **Restart Specific Service**
```bash
docker-compose restart api
docker-compose restart frontend
docker-compose restart postgres
```

### **Stop All Services**
```bash
docker-compose down
```

### **Start All Services**
```bash
docker-compose up -d
```

### **Rebuild Images**
```bash
docker-compose build --no-cache
```

---

## 💾 DATABASE COMMANDS

### **Access PostgreSQL Directly**
```bash
psql -h 127.0.0.1 -U reconhive_user -d reconhive
```

### **List All Tables**
```
\dt
```

### **View Scan Results**
```sql
SELECT * FROM scans ORDER BY created_at DESC LIMIT 10;
```

### **View Findings**
```sql
SELECT * FROM findings ORDER BY created_at DESC LIMIT 20;
```

### **View Tool Runs**
```sql
SELECT * FROM tool_runs ORDER BY created_at DESC LIMIT 10;
```

---

## 🔗 SERVICE CONNECTIONS

### **Redis CLI**
```bash
redis-cli -h 127.0.0.1 -p 6379
```

### **Check Celery Tasks**
```bash
celery -A app.workers.celery_app inspect active
```

### **View Queue Stats**
```bash
celery -A app.workers.celery_app inspect stats
```

---

## 📊 MONITORING ENDPOINTS

### **API Health Check**
```bash
curl http://127.0.0.1:8000/health
```

### **Prometheus Metrics**
```
http://127.0.0.1:9090
```

### **Available Agents**
```bash
curl http://127.0.0.1:8000/api/v1/recon/list-agents
```

### **Available Validators**
```bash
curl http://127.0.0.1:8000/api/v1/validation/validators
```

---

## 📝 WORKFLOW EXAMPLE

### **Complete Client Scan Workflow**

```bash
# 1. Start scan
SCAN_ID=$(curl -s -X POST http://127.0.0.1:8000/api/v1/recon/start \
  -d '{"target":"example.com"}' | jq -r '.scan_id')

echo "Scan started: $SCAN_ID"

# 2. Check status
curl http://127.0.0.1:8000/api/v1/recon/status/$SCAN_ID

# 3. Get results (after completion)
curl http://127.0.0.1:8000/api/v1/recon/results/$SCAN_ID | jq .

# 4. Validate findings
curl -X POST http://127.0.0.1:8000/api/v1/validation/validate/sql_injection \
  -d '{"target_url":"https://example.com","parameter":"id"}'

# 5. Check stats
curl http://127.0.0.1:8000/api/v1/validation/stats
```

---

## 🎯 DASHBOARD WORKFLOW

**For GUI-based scanning:**

1. Open http://127.0.0.1:3000
2. Click "New Engagement"
3. Enter client info
4. Add target domain
5. Click "Start Reconnaissance"
6. Monitor progress (real-time)
7. Review findings
8. Click "Generate Report"
9. Download/share report

---

## 🔐 AUTHENTICATION

Currently running in development mode without authentication.

For production deployment, configure:
- JWT authentication in `.env`
- Database credentials
- SSL/TLS certificates
- API key management

---

## 📚 DOCUMENTATION

| Guide | Purpose |
|-------|---------|
| CLIENT_SCANNING_GUIDE.md | How to scan client websites |
| TESTING_GUIDE.md | Technical API usage |
| QUICK_START.md | Getting started |
| VALIDATION_ENGINE_SUMMARY.md | Validator details |
| CLAUDE_RULES.md | Development governance |

---

## ⚡ QUICK REFERENCE TABLE

| Task | Command/URL |
|------|-------------|
| Open Dashboard | http://127.0.0.1:3000 |
| View API Docs | http://127.0.0.1:8000/docs |
| Database Admin | http://127.0.0.1:5050 |
| Start Scan | POST /api/v1/recon/start |
| Check Status | GET /api/v1/recon/status/{id} |
| Validate SQLi | POST /api/v1/validation/validate/sql_injection |
| Get Payloads | GET /api/v1/validation/payloads |
| Docker Logs | docker-compose logs -f {service} |
| Health Check | curl http://127.0.0.1:8000/health |

---

## 🚀 GETTING STARTED NOW

```bash
# 1. Open dashboard
# http://127.0.0.1:3000

# 2. Create engagement and add domain

# 3. Start scan

# 4. Monitor progress

# 5. Review findings

# 6. Generate report
```

---

**All systems operational. Ready for client engagements!** ✅

