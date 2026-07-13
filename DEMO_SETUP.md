# ReconHive Demo Setup Guide

**Target Date**: Wednesday Demo  
**Version**: v0.1-alpha  
**Status**: Production Ready (Backend + Frontend)

---

## PREREQUISITES

- Docker & Docker Compose (latest)
- 8GB RAM minimum
- 5GB disk space
- Modern browser (Chrome/Firefox/Safari)

---

## QUICK START (5 minutes)

### 1. Clone Repository

```bash
cd /c/Users/AmolLondhe/.claude/projects/reconhive
git status
```

### 2. Start Backend Services

```bash
docker-compose up -d

# Wait 30 seconds for services to initialize
sleep 30

# Verify all services running
docker-compose ps

# Check backend health
curl http://localhost:8000/health
```

**Expected Output**:
```
{
  "status": "healthy",
  "timestamp": "2026-07-13T..."
}
```

### 3. Start Frontend (Separate Terminal)

```bash
cd frontend
npm run dev

# Frontend starts on http://localhost:3000
```

**Expected Output**:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

### 4. Access Dashboard

Open browser: **http://localhost:3000**

You should see the professional ReconHive dashboard with:
- ✅ KPI cards (Engagements, Assets, Scans, etc.)
- ✅ Recent activity timeline
- ✅ Running scans table
- ✅ Risk overview chart
- ✅ Top findings list
- ✅ AI Copilot sidebar
- ✅ Sidebar navigation

---

## VERIFICATION CHECKLIST

Run through each step:

- [ ] Backend API responds to `/health`
- [ ] Frontend loads without errors (check browser console)
- [ ] Dashboard displays KPI cards with numbers
- [ ] All sidebar menu items clickable
- [ ] Click Engagements → table loads
- [ ] Click Scans → table loads
- [ ] Click Findings → table loads
- [ ] Click Evidence → table loads
- [ ] Click Assets → table loads
- [ ] Click Reports → reports list loads
- [ ] AI Copilot sidebar opens/closes
- [ ] Metric cards show proper styling
- [ ] Risk chart displays all severity levels
- [ ] Activity timeline shows recent events

---

## COMMON ISSUES & FIXES

### Issue: "Connection refused" on localhost:8000

**Fix**:
```bash
# Check if services started
docker-compose logs api

# If not, rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Frontend doesn't load

**Fix**:
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev
```

### Issue: Port 3000 already in use

**Fix**:
```bash
# Find what's using port 3000
lsof -i :3000

# Kill it
kill -9 <PID>

# Or use different port
PORT=3001 npm run dev
```

### Issue: Docker running out of memory

**Fix**:
```bash
# Stop all containers
docker-compose down

# Prune unused resources
docker system prune -a

# Start again
docker-compose up -d
```

---

## BACKEND VERIFICATION

### Check API Endpoints

```bash
# List engagements
curl http://localhost:8000/api/v1/engagements \
  -H "Authorization: Bearer demo-token"

# Get API docs
curl http://localhost:8000/docs
```

### Check Database

```bash
# Access PostgreSQL
docker exec -it reconhive-postgres-1 psql -U reconhive -d reconhive

# Inside psql:
\dt                    -- List tables
SELECT COUNT(*) FROM engagements;
\q                     -- Exit
```

### Check Redis

```bash
# Test Redis
docker exec -it reconhive-redis-1 redis-cli PING

# Should respond: PONG
```

---

## FRONTEND DEVELOPMENT

### Build Production Version

```bash
cd frontend
npm run build
npm start
```

### Run Tests (if applicable)

```bash
npm run test
```

### Check TypeScript

```bash
npx tsc --noEmit
```

---

## DEMO DATA

The dashboard is seeded with realistic demo data:

- **12 Engagements** (various statuses)
- **4,231 Assets** (servers, web apps, APIs, etc.)
- **7 Running Scans** (with progress bars)
- **156 Findings** (by severity)
- **156 Evidence Files** (screenshots, logs, JSON, etc.)
- **20 Event Log Entries** (recent activity)

All data is mock data in the frontend. No backend changes needed.

---

## STOPPING SERVICES

### Stop Frontend

```
Ctrl+C in frontend terminal
```

### Stop Backend

```bash
docker-compose down

# Or with volume cleanup
docker-compose down -v
```

---

## TROUBLESHOOTING

**Problem**: Services start but frontend shows "Unable to reach API"
**Solution**: Frontend uses mock data by default. Backend is optional for demo.

**Problem**: Dashboard loads slowly
**Solution**: Clear browser cache (Ctrl+Shift+Delete)

**Problem**: Sidebar doesn't appear
**Solution**: Check browser console for JS errors. Try hard refresh (Ctrl+Shift+R).

---

## DOCKER COMPOSE SERVICES

| Service | Port | Purpose |
|---------|------|---------|
| api | 8000 | FastAPI backend |
| frontend | 3000 | Next.js dashboard |
| postgres | 5432 | Database |
| redis | 6379 | Cache/broker |
| pgadmin | 5050 | DB admin UI |
| flower | 5555 | Celery monitor |
| prometheus | 9090 | Metrics |
| grafana | 3001 | Dashboards |

---

## NEXT STEPS AFTER SETUP

1. **Verify Dashboard** (5 min)
   - Navigate all pages
   - Check all components render

2. **Test Interactions** (5 min)
   - Click filters on tables
   - Open sidebar menu
   - Click AI Copilot

3. **Run Demo Script** (15 min)
   - Follow DEMO_SCRIPT.md for talking points

4. **Interview Prep** (30 min)
   - Read WEDNESDAY_DEMO_GUIDE.md
   - Practice transitions between pages
   - Prepare architecture explanation

---

**Status**: ✅ Ready for Wednesday demo

Setup time: ~5 minutes  
Verification time: ~5 minutes  
Demo duration: ~15-20 minutes
