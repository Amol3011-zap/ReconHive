# ReconHive Developer Tools

Complete suite of development and monitoring tools integrated into docker-compose.

---

## Quick Start

### Start All Services
```bash
docker-compose up -d
```

### Access Developer Tools

| Tool | URL | Purpose |
|------|-----|---------|
| **API** | http://localhost:8000 | ReconHive API |
| **API Docs** | http://localhost:8000/docs | Swagger OpenAPI |
| **Frontend** | http://localhost:3000 | Next.js frontend |
| **pgAdmin** | http://localhost:5050 | PostgreSQL admin |
| **Adminer** | http://localhost:8080 | Database browser |
| **Mailpit** | http://localhost:8025 | Email testing |
| **Flower** | http://localhost:5555 | Celery task monitor |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Grafana** | http://localhost:3001 | Dashboards & alerts |

---

## 🗄️ Database Management

### pgAdmin (http://localhost:5050)
PostgreSQL web-based administration tool.

**Login**:
- Email: `admin@reconhive.local` (or set `PGADMIN_EMAIL`)
- Password: `admin` (or set `PGADMIN_PASSWORD`)

**Features**:
- Create/drop databases
- Manage users and permissions
- Query builder
- Backup/restore
- Performance monitoring

**Add ReconHive Database**:
1. Right-click "Servers" → Register → Server
2. General: Name = "ReconHive"
3. Connection:
   - Host: `postgres`
   - Port: `5432`
   - Username: `reconhive_user`
   - Password: `secure_password_change_me`
4. Save

### Adminer (http://localhost:8080)
Lightweight alternative for database browsing.

**Login**:
- System: PostgreSQL
- Server: `postgres`
- Username: `reconhive_user`
- Password: `secure_password_change_me`
- Database: `reconhive`

**Features**:
- Browse tables
- Edit data directly
- Export/import
- Run SQL queries

---

## 📧 Email Testing

### Mailpit (http://localhost:8025)

Local SMTP server for testing email functionality without sending real emails.

**Configuration**:
```python
# In your FastAPI app
SMTP_HOST = "mailpit"
SMTP_PORT = 1025
SMTP_USER = ""
SMTP_PASSWORD = ""
SMTP_TLS = False
```

**Features**:
- Capture all outgoing emails
- View email content, headers, attachments
- Release emails to real SMTP
- Web UI to inspect messages

**Access**: http://localhost:8025

---

## 🔄 Task Queue & Background Jobs

### Redis (Port 6379)
In-memory data store for Celery task queue and caching.

**CLI Access**:
```bash
docker-compose exec redis redis-cli
> PING
PONG
> INFO
```

**Commands**:
```bash
# List all keys
KEYS *

# Get value
GET key_name

# Delete key
DEL key_name

# Monitor in real-time
MONITOR
```

### Celery Worker
Background job processing for:
- Long-running scans
- Plugin execution
- Report generation
- Scheduled tasks

**View Logs**:
```bash
docker-compose logs -f celery
```

### Flower (http://localhost:5555)
Real-time Celery task monitoring dashboard.

**Features**:
- Active tasks
- Task history
- Worker status
- Task timing and performance
- Retry tracking
- Task termination

**Monitor**:
```bash
# View real-time tasks
Open http://localhost:5555

# Click on "Tasks" tab for history
# Click on "Workers" tab for status
```

---

## 📊 Metrics & Monitoring

### Prometheus (http://localhost:9090)
Time-series database for metrics collection.

**Metrics Scraped**:
- API response times
- Request counts
- Redis performance
- PostgreSQL connections
- Celery task metrics

**Query Examples**:
```promql
# API request rate (requests/sec)
rate(http_requests_total[5m])

# API response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Redis connections
redis_connected_clients

# Celery active tasks
celery_tasks_active
```

**Access**:
1. Go to http://localhost:9090
2. Click "Metrics" tab
3. Select metric and click "Execute"
4. Graph appears automatically

### Grafana (http://localhost:3001)
Beautiful dashboards and alerting on Prometheus metrics.

**Login**:
- Username: `admin` (or set `GRAFANA_USER`)
- Password: `admin` (or set `GRAFANA_PASSWORD`)

**Dashboards Included**:
- System metrics (CPU, memory, disk)
- API performance
- Database performance
- Redis status
- Celery task monitoring

**Create Dashboard**:
1. Click "+" → Dashboard
2. Click "Add panel"
3. Select Prometheus datasource
4. Write PromQL query
5. Configure visualization
6. Save

**Example Panel - API Response Time**:
```
Metric: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
Title: "API Response Time (p95)"
Unit: seconds
Type: Graph
```

---

## 🚀 Common Workflows

### Monitor a Celery Task
```bash
# Terminal 1: Watch Flower dashboard
open http://localhost:5555

# Terminal 2: Trigger task from API
curl -X POST http://localhost:8000/api/v1/scans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"engagement_id": "...", "target": "192.168.1.1"}'

# Flower shows:
# - Task ID
# - Status (PENDING → STARTED → SUCCESS/FAILURE)
# - Duration
# - Worker assigned
```

### Debug Database Query
```bash
# Open Adminer
http://localhost:8080

# Run SQL to analyze query
SELECT COUNT(*) FROM engagements;
SELECT * FROM engagements WHERE status = 'active';
EXPLAIN ANALYZE SELECT * FROM findings WHERE severity = 'critical';
```

### Check Email Delivery
```bash
# Trigger email-sending operation in API
# Check Mailpit for received email
http://localhost:8025

# View email:
# - Subject, From, To
# - Headers
# - HTML content
# - Text content
# - Attachments
```

### Performance Analysis
```bash
# 1. Generate load (in another terminal)
ab -n 1000 -c 10 http://localhost:8000/api/v1/engagements

# 2. Watch metrics in Prometheus
http://localhost:9090
Query: rate(http_requests_total[1m])

# 3. Create Grafana panel for visualization
http://localhost:3001
```

---

## 🔍 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs -f postgres
docker-compose logs -f api
docker-compose logs -f celery

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Failed
```bash
# Verify PostgreSQL is running
docker-compose exec postgres pg_isready

# Check credentials
docker-compose exec postgres psql -U reconhive_user -d reconhive

# View logs
docker-compose logs postgres
```

### Redis Connection Issues
```bash
# Test Redis
docker-compose exec redis redis-cli ping
PONG

# Check memory
docker-compose exec redis redis-cli info memory

# Clear all keys (careful!)
docker-compose exec redis redis-cli FLUSHALL
```

### Flower Not Showing Tasks
```bash
# Verify Celery is running
docker-compose logs celery

# Restart Flower
docker-compose restart flower

# Trigger a task to test
# Task should appear in Flower within seconds
```

### Grafana Datasource Not Working
```bash
# Verify Prometheus is running
curl http://localhost:9090/-/healthy

# Check datasource in Grafana
http://localhost:3001
Settings → Data Sources → Prometheus
Click "Test" button
```

---

## 📝 Environment Variables

Add to `.env` file to customize tools:

```bash
# pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=secure_password

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=secure_password

# Mailpit (optional - defaults are fine)
MAILPIT_PORT=1025
MAILPIT_WEB_PORT=8025

# Redis (optional)
REDIS_PASSWORD=secure_redis_password
```

---

## 🔧 Advanced Configuration

### Custom Prometheus Scrape Config
Edit `monitoring/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'custom_service'
    static_configs:
      - targets: ['custom_service:8080']
```

### Custom Grafana Dashboard
Create JSON dashboard file and add to `monitoring/grafana/provisioning/dashboards/`

### Alert Rules
Create `monitoring/prometheus/alerts.yml`:
```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
```

---

## 📚 Documentation Links

- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/
- **Celery**: https://docs.celeryproject.io/
- **Flower**: https://flower.readthedocs.io/
- **pgAdmin**: https://www.pgadmin.org/docs/
- **Adminer**: https://www.adminer.org/

---

## 💡 Tips

1. **Auto-refresh Dashboards**: Grafana → Top right "Refresh" button
2. **Export Metrics**: Prometheus → Graph tab → Export → JSON
3. **Task Retry**: Flower → Tasks → Right-click → Revoke/Retry
4. **Email Preview**: Mailpit → Click email → View HTML
5. **Query Performance**: pgAdmin → Tools → Query Tool → EXPLAIN ANALYZE

---

## 🚨 Production Notes

⚠️ These tools are for **development only**:
- Disable pgAdmin in production
- Use managed Prometheus/Grafana in production
- Use transactional email service (SendGrid, AWS SES)
- Secure Grafana with authentication
- Use Redis persistence in production

---

**Last Updated**: July 7, 2026  
**Status**: All tools operational  
**Health Check**: `docker-compose ps`
