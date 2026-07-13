# API Data Diagnostic

**Purpose**: Verify the dashboard is getting REAL data from the database, not cached/fake values

---

## Check 1: API Health

```bash
curl -H "Authorization: Bearer demo-token" \
  http://localhost:8000/health
```

Expected:
```json
{"status": "healthy", "version": "3.0.0", "phase": 3}
```

---

## Check 2: Dashboard Stats API

```bash
curl -H "Authorization: Bearer demo-token" \
  http://localhost:8000/api/v1/dashboard/stats
```

This should return ACTUAL counts from database:
- `engagements.total` - count from engagements table
- `assets.total` - count from assets table
- `scans.running` - count of running scans
- `findings.total` - count from findings table
- `findings.critical` - count of critical findings
- `evidence.total` - count from evidence table

If all zeros → Database is empty OR API is failing silently

---

## Check 3: Dashboard Full Data API

```bash
curl -H "Authorization: Bearer demo-token" \
  http://localhost:8000/api/v1/dashboard/full
```

This should return:
```json
{
  "success": true,
  "data": {
    "findings_by_severity": { "CRITICAL": 0, "HIGH": 0, ... },
    "top_findings": [],
    "asset_summary": {},
    "evidence_summary": {},
    "scans_overview": []
  }
}
```

---

## Check 4: Direct Database Query

```bash
psql -U postgres -d reconhive -c "
SELECT 
  (SELECT COUNT(*) FROM engagements) as engagements,
  (SELECT COUNT(*) FROM assets) as assets,
  (SELECT COUNT(*) FROM scans WHERE status = 'running') as running_scans,
  (SELECT COUNT(*) FROM findings) as findings,
  (SELECT COUNT(*) FROM findings WHERE severity = 'critical') as critical_findings,
  (SELECT COUNT(*) FROM evidence) as evidence_files;
"
```

---

## What's Probably Happening

### Scenario 1: Database is Empty
- All API queries return 0
- Dashboard shows: 0 engagements, 0 assets, 0 scans, 0 findings
- ✅ This is CORRECT - shows real state

### Scenario 2: API is Failing Silently
- Frontend catches error, shows error banner
- Dashboard shows: 0 across all metrics
- ✅ This is CORRECT - shows real state (API down)

### Scenario 3: Old Cache Still Active
- API works but returns 0s
- Frontend shows the values from before (12, 4.2K, 7, etc.)
- ❌ This is WRONG - browser cache or hardcoded fallback

---

## The Fix Applied

1. ✅ Removed hardcoded engagement ID
2. ✅ Changed API call to NOT filter by engagement (get all data)
3. ✅ Removed initial state with fake numbers
4. ✅ Added error banner if API fails
5. ✅ Console logging to debug

---

## Testing the Fix

### Step 1: Clear Browser Cache
```
Ctrl+Shift+Delete → Clear all data
```

### Step 2: Verify Backend is Running
```bash
docker-compose ps
# Should show api container as UP
```

### Step 3: Refresh Dashboard
```
http://127.0.0.1:3000
```

### Expected Result
- If database is empty: All metrics show 0
- If API fails: Error banner shows explaining why
- If database has data: Real numbers displayed

---

## If Still Showing Fake Numbers

1. Check browser console (F12 → Console tab)
   - Should see API calls logged
   - Should see data returned (or errors)

2. Check if API is actually returning data
   - Run `curl` commands above

3. Check if database has any data
   - Run direct PostgreSQL query

4. Check if error banner appears
   - If yes: API is failing, not a data issue
   - If no: API is working, but database is empty (which is correct!)

---

## Rule: Dashboard Must Never Lie

- If database has 0 scans → show 0
- If API is down → show error message
- If database has 156 findings → show 156
- Never show cached/old/fake numbers

**Current state after fix**: All metrics pull from `stats` state which starts at 0 and only updates from API. No hardcoded fallback values.
