# API Changes - Workflow Endpoints

**Version**: v0.1-alpha  
**Base URL**: `http://localhost:8000/api/v1`  
**Authentication**: Bearer token (demo: `Bearer demo-token`)

---

## Summary

Added 8 new API endpoints to enable complete scan workflow:
- Scan execution (start, progress, details)
- Worker management (list, register, heartbeat)
- Dashboard statistics and activity

All endpoints return standardized JSON responses with status, data, and error fields.

---

## New Endpoints

### 1. Start Scan

**Endpoint**: `POST /scans/{scan_id}/start`

**Purpose**: Initialize a queued scan and assign a worker

**Parameters**:
```
Path:
  scan_id (UUID) - Scan identifier

Headers:
  Authorization: Bearer {token}
```

**Request** (No body):
```bash
curl -X POST http://localhost:8000/api/v1/scans/550e8400-e29b-41d4-a716-446655440000/start \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "worker_id": "550e8400-e29b-41d4-a716-446655440001"
  },
  "error": null
}
```

**Status Codes**:
- `200` - Scan started successfully
- `400` - Invalid scan ID or scan not in QUEUED state
- `401` - Unauthorized
- `404` - Scan not found

**Side Effects**:
- Sets `scans.status = 'running'`
- Sets `scans.started_at = NOW()`
- Assigns available worker
- Creates first job record
- Updates worker metrics

---

### 2. Update Scan Progress

**Endpoint**: `POST /scans/{scan_id}/progress`

**Purpose**: Advance scan to next stage (simulate progress)

**Parameters**:
```
Path:
  scan_id (UUID) - Scan identifier

Headers:
  Authorization: Bearer {token}
```

**Request** (No body):
```bash
curl -X POST http://localhost:8000/api/v1/scans/550e8400-e29b-41d4-a716-446655440000/progress \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "progress": 45,
    "stage": "Scanning"
  },
  "error": null
}
```

**Progress Stages**:
```
0-25%     → "Initialize"      (validation, setup)
25-50%    → "Scanning"        (active scanning)
50-75%    → "Scanning"        (continued scanning)
75-100%   → "Reporting"       (result aggregation)
100%      → "Completed"       (generate findings & evidence)
```

**Status Codes**:
- `200` - Progress updated
- `400` - Invalid scan state
- `401` - Unauthorized
- `404` - Scan not found

**Side Effects**:
- Increments `scans.progress_percent`
- Updates `scans.current_stage`
- Appends to `jobs.logs`
- On 100%: Generates findings and evidence

---

### 3. Get Scan Details

**Endpoint**: `GET /scans/{scan_id}/details`

**Purpose**: Fetch complete scan information including jobs, findings, evidence

**Parameters**:
```
Path:
  scan_id (UUID) - Scan identifier

Headers:
  Authorization: Bearer {token}
```

**Request**:
```bash
curl -X GET http://localhost:8000/api/v1/scans/550e8400-e29b-41d4-a716-446655440000/details \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "scan": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Nuclei - Web Scan",
      "status": "running",
      "progress": 79,
      "stage": "Scanning",
      "started_at": "2026-07-13T15:22:00Z",
      "worker_id": "550e8400-e29b-41d4-a716-446655440001",
      "duration_seconds": 300
    },
    "jobs": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "plugin": "Nuclei",
        "status": "running",
        "progress": 79,
        "logs": [
          "[15:22] Scan started",
          "[15:25] Loaded 500 templates",
          "[15:35] Found 12 vulnerabilities"
        ]
      }
    ],
    "findings": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "title": "Exposed Admin Panel",
        "severity": "high",
        "cvss": 7.5
      }
    ],
    "evidence": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "name": "HTTP Response Headers",
        "type": "http_response"
      }
    ]
  },
  "error": null
}
```

**Status Codes**:
- `200` - Details retrieved
- `401` - Unauthorized
- `404` - Scan not found

---

### 4. Create Worker

**Endpoint**: `POST /workers`

**Purpose**: Register a new worker node

**Parameters**:
```
Query:
  name (string, required) - Worker name (e.g., "recon-worker-1")
  worker_type (string, optional) - Type (reconnaissance, vulnerability_assessment, etc.)
  
Headers:
  Authorization: Bearer {token}
```

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/workers?name=recon-worker-3&worker_type=reconnaissance" \
  -H "Authorization: Bearer demo-token"
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440005",
    "name": "recon-worker-3",
    "type": "reconnaissance",
    "status": "online"
  },
  "error": null
}
```

**Status Codes**:
- `201` - Worker created
- `400` - Invalid parameters or duplicate name
- `401` - Unauthorized

---

### 5. List Workers

**Endpoint**: `GET /workers`

**Purpose**: Fetch all registered workers with metrics

**Parameters**:
```
Query:
  skip (integer, optional, default=0) - Pagination offset
  limit (integer, optional, default=50) - Pagination limit
  
Headers:
  Authorization: Bearer {token}
```

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/workers?skip=0&limit=10" \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "recon-worker-1",
      "type": "reconnaissance",
      "status": "online",
      "cpu_usage": 45.2,
      "memory_usage": 2.1,
      "active_jobs": 3,
      "queue_depth": 5,
      "completed_jobs": 142,
      "failed_jobs": 2,
      "is_enabled": true
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "nuclei-worker",
      "type": "vulnerability_assessment",
      "status": "online",
      "cpu_usage": 68.7,
      "memory_usage": 3.4,
      "active_jobs": 5,
      "queue_depth": 8,
      "completed_jobs": 87,
      "failed_jobs": 1,
      "is_enabled": true
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 10
}
```

**Status Codes**:
- `200` - Workers listed
- `401` - Unauthorized

---

### 6. Worker Heartbeat

**Endpoint**: `POST /workers/{worker_id}/heartbeat`

**Purpose**: Update worker keep-alive and status

**Parameters**:
```
Path:
  worker_id (UUID) - Worker identifier

Headers:
  Authorization: Bearer {token}
```

**Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/workers/550e8400-e29b-41d4-a716-446655440001/heartbeat" \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "online",
    "last_heartbeat": "2026-07-13T15:30:00Z"
  },
  "error": null
}
```

**Status Codes**:
- `200` - Heartbeat recorded
- `401` - Unauthorized
- `404` - Worker not found

**Side Effects**:
- Updates `workers.last_heartbeat = NOW()`
- If offline, sets `workers.status = 'online'`

---

### 7. Dashboard Statistics

**Endpoint**: `GET /dashboard/stats`

**Purpose**: Get aggregated metrics for dashboard

**Parameters**:
```
Query:
  engagement_id (UUID, optional) - Filter to specific engagement
  
Headers:
  Authorization: Bearer {token}
```

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/stats?engagement_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "engagements": {
      "total": 12,
      "active": 8
    },
    "assets": {
      "total": 4231
    },
    "scans": {
      "running": 3,
      "completed": 47
    },
    "findings": {
      "total": 156,
      "critical": 9,
      "high": 34
    },
    "evidence": {
      "total": 256
    },
    "workers": {
      "online": 4,
      "total": 5
    }
  },
  "error": null
}
```

**Status Codes**:
- `200` - Stats retrieved
- `401` - Unauthorized

---

### 8. Activity Timeline

**Endpoint**: `GET /dashboard/activity`

**Purpose**: Get recent activity for timeline display

**Parameters**:
```
Query:
  engagement_id (UUID, optional) - Filter to specific engagement
  limit (integer, optional, default=20) - Max activities to return
  
Headers:
  Authorization: Bearer {token}
```

**Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/activity?limit=10" \
  -H "Authorization: Bearer demo-token"
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "type": "scan_created",
        "title": "Scan created: Nuclei - Web Scan",
        "timestamp": "2026-07-13T15:25:00Z",
        "icon": "🔍"
      },
      {
        "type": "finding_created",
        "title": "Finding: Exposed Admin Panel (high)",
        "timestamp": "2026-07-13T15:22:30Z",
        "icon": "🚨"
      }
    ]
  },
  "error": null
}
```

**Status Codes**:
- `200` - Activities retrieved
- `401` - Unauthorized

---

## Response Format

All responses follow standard format:

```json
{
  "success": boolean,
  "data": any,
  "error": string | null,
  "timestamp": "ISO-8601 timestamp"
}
```

### Success Response
```json
{
  "success": true,
  "data": { /* payload */ },
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": null,
  "error": "Human-readable error message"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid token |
| 404 | Not Found - Resource doesn't exist |
| 500 | Server Error - Internal error |

---

## Request/Response Examples

### Complete Workflow Example

**1. List workers**
```bash
curl -X GET http://localhost:8000/api/v1/workers \
  -H "Authorization: Bearer demo-token"
```

**2. Get scan details**
```bash
curl -X GET http://localhost:8000/api/v1/scans/scan-id-here/details \
  -H "Authorization: Bearer demo-token"
```

**3. Start scan**
```bash
curl -X POST http://localhost:8000/api/v1/scans/scan-id-here/start \
  -H "Authorization: Bearer demo-token"
```

**4. Update progress (repeat multiple times)**
```bash
curl -X POST http://localhost:8000/api/v1/scans/scan-id-here/progress \
  -H "Authorization: Bearer demo-token"
```

**5. Get updated details with findings**
```bash
curl -X GET http://localhost:8000/api/v1/scans/scan-id-here/details \
  -H "Authorization: Bearer demo-token"
```

---

## Implementation Details

### Scan State Machine

```
QUEUED
  ↓ (POST /start)
RUNNING (0-25%)
  ↓ (POST /progress)
RUNNING (25-50%)
  ↓ (POST /progress)
RUNNING (50-75%)
  ↓ (POST /progress)
RUNNING (75-100%)
  ↓ (POST /progress with 100%)
COMPLETED (generate findings & evidence)
```

### Worker Assignment Algorithm

1. Query all online workers
2. Filter by plugin compatibility
3. Sort by `active_jobs` (ascending)
4. Assign to worker with fewest jobs
5. Update worker metrics

### Finding Generation

When scan reaches 100%:
1. Create 5 realistic findings with:
   - Title (e.g., "Exposed Admin Panel")
   - Severity (critical, high, medium, low, info)
   - CVSS score
   - Description
   - Remediation steps
2. Link to scan_id and asset_id
3. Create 3 evidence artifacts (logs, response headers, JSON)

---

## Performance Characteristics

| Endpoint | Avg Latency | Notes |
|----------|-------------|-------|
| POST /start | 50ms | Creates job record |
| POST /progress | 30ms | Updates progress |
| GET /details | 100ms | Joins multiple tables |
| POST /workers | 40ms | Creates record |
| GET /workers | 60ms | Lists 50+ workers |
| POST /heartbeat | 20ms | Timestamp update |
| GET /stats | 150ms | Aggregates across DB |
| GET /activity | 120ms | Sorts by timestamp |

---

## Rate Limiting

Currently **not implemented** (Phase 5 task).

Recommendation:
- API calls: 1000/hour per IP
- Scan starts: 100/hour per engagement
- Dashboard refreshes: 60/minute per session

---

## Deprecation Notes

None. These are new endpoints, no deprecations.

---

## Future API Additions (Phase 5+)

- `PATCH /scans/{scan_id}` - Update scan settings
- `DELETE /scans/{scan_id}` - Cancel scan
- `POST /scans/{scan_id}/rerun` - Re-run scan
- `GET /workers/{worker_id}/metrics` - Detailed worker metrics
- `POST /workers/{worker_id}/restart` - Restart worker
- `GET /findings/{finding_id}` - Get finding details
- `PATCH /findings/{finding_id}` - Update finding status
- `GET /reports/{scan_id}` - Generate PDF report
- `POST /engagements/{eng_id}/archive` - Archive engagement

---

## Testing Endpoints

### Health Check (Existing)
```bash
curl http://localhost:8000/health
```

### API Docs (Auto-Generated)
```
http://localhost:8000/docs
```

Interactive Swagger UI to test all endpoints.

---

## Integration with Frontend

### Scans Page
- Lists scans: `GET /scans?engagement_id={id}`
- Shows details: `GET /scans/{id}/details`
- Starts scan: `POST /scans/{id}/start`
- Updates progress: `POST /scans/{id}/progress` (5s interval)

### Dashboard
- Loads stats: `GET /dashboard/stats`
- Loads activity: `GET /dashboard/activity`

### Agents Page
- Lists workers: `GET /workers`
- Heartbeat (backend only): `POST /workers/{id}/heartbeat`

---

## Authorization

All endpoints require `Authorization: Bearer {token}` header.

**Demo Token**: `demo-token`

For production (Phase 6):
- Implement JWT verification
- Add user roles and permissions
- Add engagement-scoped access
- Add audit logging

---

## Changelog

### v0.1-alpha (2026-07-13)
- Initial 8 endpoints for scan workflow
- Worker management
- Dashboard statistics
- Activity timeline
