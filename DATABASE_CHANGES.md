# Database Changes - Worker Tracking System

**Version**: v0.1-alpha  
**Migration**: 0003_worker_tracking.py  
**Status**: Ready to deploy

---

## Summary

Added a complete `workers` table to track agents/workers in the ReconHive system. This enables:
- Worker health monitoring
- Job assignment and queuing
- Resource tracking (CPU/memory)
- Heartbeat-based availability
- Worker capability classification

---

## New Table: `workers`

### Purpose
Tracks all worker nodes (reconnaissance agents, scanning workers, evidence collectors, reporting engines) in the system.

### Schema

```sql
CREATE TABLE workers (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    type ENUM('reconnaissance', 'vulnerability_assessment', 'exploitation', 'evidence', 'reporting'),
    
    -- Status & Availability
    status ENUM('online', 'offline', 'busy', 'paused') DEFAULT 'online',
    is_enabled BOOLEAN DEFAULT true,
    last_heartbeat TIMESTAMP DEFAULT NOW(),
    
    -- Location
    hostname VARCHAR(255),
    ip_address VARCHAR(45),
    port INTEGER DEFAULT 5000,
    
    -- Resource Metrics
    cpu_usage FLOAT DEFAULT 0.0,
    memory_usage FLOAT DEFAULT 0.0,
    disk_usage FLOAT DEFAULT 0.0,
    
    -- Job Tracking
    current_job_id UUID,
    active_jobs INTEGER DEFAULT 0,
    queue_depth INTEGER DEFAULT 0,
    
    -- Statistics
    completed_jobs INTEGER DEFAULT 0,
    failed_jobs INTEGER DEFAULT 0,
    total_runtime_seconds INTEGER DEFAULT 0,
    
    -- Capabilities
    supported_plugins JSONB DEFAULT '{}',
    capabilities JSONB DEFAULT '{}',
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    INDEX ix_workers_name ON workers(name),
    INDEX ix_workers_status ON workers(status),
    INDEX ix_workers_type ON workers(type),
    INDEX ix_workers_is_enabled ON workers(is_enabled),
    INDEX ix_workers_last_heartbeat ON workers(last_heartbeat)
);
```

### Column Descriptions

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique worker identifier |
| `name` | VARCHAR(255) | NO | - | Unique worker name (e.g., "recon-worker-1") |
| `type` | ENUM | NO | - | Worker specialization (reconnaissance, vuln assessment, etc.) |
| `status` | ENUM | NO | 'online' | Current state (online/offline/busy/paused) |
| `is_enabled` | BOOLEAN | NO | true | Whether worker is active in pool |
| `last_heartbeat` | TIMESTAMP | NO | NOW() | Last keep-alive timestamp |
| `hostname` | VARCHAR(255) | YES | NULL | Hostname/DNS name |
| `ip_address` | VARCHAR(45) | YES | NULL | IPv4 or IPv6 address |
| `port` | INTEGER | NO | 5000 | Communication port |
| `cpu_usage` | FLOAT | NO | 0.0 | CPU utilization percentage |
| `memory_usage` | FLOAT | NO | 0.0 | Memory utilization percentage |
| `disk_usage` | FLOAT | NO | 0.0 | Disk utilization percentage |
| `current_job_id` | UUID | YES | NULL | Currently executing job ID |
| `active_jobs` | INTEGER | NO | 0 | Number of running jobs |
| `queue_depth` | INTEGER | NO | 0 | Queued jobs count |
| `completed_jobs` | INTEGER | NO | 0 | Lifetime completed jobs |
| `failed_jobs` | INTEGER | NO | 0 | Lifetime failed jobs |
| `total_runtime_seconds` | INTEGER | NO | 0 | Cumulative job execution time |
| `supported_plugins` | JSONB | NO | '{}' | List of available plugins/tools |
| `capabilities` | JSONB | NO | '{}' | Worker capabilities/features |
| `metadata` | JSONB | YES | NULL | Custom metadata |
| `created_at` | TIMESTAMP | NO | NOW() | Registration timestamp |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update timestamp |

---

## Enum Types Created

### WorkerStatus
```
- 'online'    → Worker accepting jobs
- 'offline'   → Worker unavailable  
- 'busy'      → Processing jobs
- 'paused'    → Temporarily paused
```

### WorkerType
```
- 'reconnaissance'             → Network/domain discovery
- 'vulnerability_assessment'   → Security scanning (Nuclei, etc.)
- 'exploitation'              → Active exploitation
- 'evidence'                  → Evidence collection/processing
- 'reporting'                 → Report generation
```

---

## Indexes

Created 5 indexes for optimal query performance:

```sql
CREATE INDEX ix_workers_name ON workers(name);
CREATE INDEX ix_workers_status ON workers(status);
CREATE INDEX ix_workers_type ON workers(type);
CREATE INDEX ix_workers_is_enabled ON workers(is_enabled);
CREATE INDEX ix_workers_last_heartbeat ON workers(last_heartbeat);
```

These enable:
- Fast worker lookup by name
- Filtering online workers
- Finding workers by specialization
- Filtering enabled/disabled workers
- Finding stale heartbeats

---

## Related Tables (No Schema Changes)

### `scans` table
Already has `worker_id` column (VARCHAR(255)) to track which worker executed the scan.

### `jobs` table
Already has complete job tracking:
- `worker_id` - Assigned worker
- `status` - Job state (queued/running/completed/failed)
- `progress_percent` - Job progress
- `logs` - Execution logs
- Timestamps for job lifecycle

### `findings` table
No changes needed - already supports scan-based finding linkage.

### `evidence` table
No changes needed - already supports scan-based evidence linkage.

---

## Migration Rollback

If needed, rollback removes the workers table:

```sql
DROP TABLE workers CASCADE;
DROP TYPE workerstatus;
DROP TYPE workertype;
```

---

## Sample Data

### Default Workers (Auto-Seeded)

```python
workers = [
    Worker(name="recon-worker-1", type=WorkerType.RECONNAISSANCE),
    Worker(name="recon-worker-2", type=WorkerType.RECONNAISSANCE),
    Worker(name="nuclei-worker", type=WorkerType.VULNERABILITY_ASSESSMENT),
    Worker(name="evidence-worker", type=WorkerType.EVIDENCE),
    Worker(name="ai-copilot", type=WorkerType.REPORTING),
]
```

---

## Foreign Key Relationships

**NOT direct foreign keys** (workers are independent):
- Jobs reference workers by ID
- Scans reference workers by ID
- No cascade deletes (workers persist independently)

---

## Performance Considerations

### Query Examples

**Get available workers**:
```sql
SELECT * FROM workers
WHERE is_enabled = true 
  AND status IN ('online', 'busy')
ORDER BY active_jobs ASC
LIMIT 5;
```

**Find stale workers** (no heartbeat in 5 minutes):
```sql
SELECT * FROM workers
WHERE last_heartbeat < NOW() - INTERVAL '5 minutes';
```

**Worker statistics**:
```sql
SELECT name, status, completed_jobs, failed_jobs, 
       ROUND(100.0 * failed_jobs / (completed_jobs + failed_jobs), 2) AS failure_rate
FROM workers;
```

### Index Usage
- `ix_workers_status` → "Get online workers"
- `ix_workers_type` → "Get scanning workers"  
- `ix_workers_is_enabled` → "Get active workers"
- `ix_workers_last_heartbeat` → "Find stale workers"
- `ix_workers_name` → "Lookup specific worker"

---

## Migration Steps

### Automatic (Recommended)
```bash
cd backend
alembic upgrade head
```

### Manual (If Needed)
```sql
-- Create enum types
CREATE TYPE workerstatus AS ENUM ('online', 'offline', 'busy', 'paused');
CREATE TYPE workertype AS ENUM (
    'reconnaissance',
    'vulnerability_assessment', 
    'exploitation',
    'evidence',
    'reporting'
);

-- Create table (use schema from above)
CREATE TABLE workers ( ... );

-- Create indexes
CREATE INDEX ix_workers_name ON workers(name);
... (5 indexes total)
```

---

## Compatibility

### Backward Compatibility
✅ **Full** - No changes to existing tables. Safe to deploy.

### Existing Code
- `scans.worker_id` column already exists
- `jobs.worker_id` column already exists
- No breaking changes to APIs

### Data Migration
- No historical data to migrate
- New table populated on worker registration

---

## Monitoring

### Health Checks
```sql
-- Worker availability
SELECT COUNT(*) 
FROM workers
WHERE status = 'online' AND is_enabled = true;

-- Queue depth
SELECT SUM(queue_depth) as total_queued
FROM workers
WHERE is_enabled = true;

-- Success rate
SELECT 
    COUNT(*) as total_workers,
    SUM(CASE WHEN completed_jobs > 0 THEN 1 ELSE 0 END) as active_workers,
    ROUND(AVG(100.0 * completed_jobs / NULLIF(completed_jobs + failed_jobs, 0)), 2) as avg_success_rate
FROM workers;
```

---

## Future Enhancements

### Planned Additions (Phase 5+)
- Worker authentication tokens
- Geo-location tagging
- Cost tracking per worker
- Custom metrics storage
- Worker grouping/clustering
- Batch job support
- Worker upgrade versioning

### Potential Columns (Later)
```sql
-- Version tracking
version VARCHAR(50),

-- Cost tracking
cost_per_hour DECIMAL(10,2),
monthly_cost DECIMAL(10,2),

-- Geographic tagging
region VARCHAR(50),
zone VARCHAR(50),
availability_zone VARCHAR(50),

-- Advanced scheduling
priority_boost INTEGER,
max_concurrent_jobs INTEGER,
preferred_job_types TEXT[],
```

---

## Testing

### Test Queries

```sql
-- Insert test worker
INSERT INTO workers (id, name, type, status, cpu_usage, memory_usage, active_jobs)
VALUES (gen_random_uuid(), 'test-worker', 'reconnaissance', 'online', 25.5, 45.2, 2);

-- Verify insertion
SELECT * FROM workers WHERE name = 'test-worker';

-- Check enum values
SELECT * FROM workers WHERE type = 'reconnaissance';

-- Test status filtering
SELECT * FROM workers WHERE status IN ('online', 'busy') AND is_enabled = true;

-- Clean up
DELETE FROM workers WHERE name = 'test-worker';
```

---

## Deployment Checklist

- [ ] Run migration: `alembic upgrade head`
- [ ] Verify table exists: `\d workers`
- [ ] Check indexes: `\d+ workers`
- [ ] Seed default workers
- [ ] Verify worker list API: `GET /api/v1/workers`
- [ ] Test worker heartbeat: `POST /api/v1/workers/{id}/heartbeat`
- [ ] Verify dashboard stats: `GET /api/v1/dashboard/stats`

---

## Support

**Questions**?
- Check `alembic/versions/0003_worker_tracking.py` for full migration
- See `app/models/worker.py` for ORM definition
- See `app/services/worker_service.py` for service layer
