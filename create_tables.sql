CREATE TABLE IF NOT EXISTS engagements (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  type VARCHAR(50),
  status VARCHAR(50),
  client VARCHAR(255),
  scope TEXT,
  owner VARCHAR(255),
  team_members VARCHAR(1000),
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP,
  due_date TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS assets (
  id UUID PRIMARY KEY,
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  name VARCHAR(255),
  display_name VARCHAR(255),
  description TEXT,
  type VARCHAR(50),
  environment VARCHAR(50),
  criticality VARCHAR(50),
  status VARCHAR(50) DEFAULT 'active',
  owner VARCHAR(255),
  tags JSONB,
  technology_stack JSONB,
  operating_system VARCHAR(100),
  risk_score FLOAT DEFAULT 0.0,
  scan_history JSONB,
  custom_metadata JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scans (
  id UUID PRIMARY KEY,
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
  name VARCHAR(255),
  description VARCHAR(500),
  plugin_names JSONB,
  configuration JSONB,
  status VARCHAR(50) DEFAULT 'queued',
  progress_percent INTEGER DEFAULT 0,
  current_stage VARCHAR(100),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  worker_id UUID,
  duration_seconds INTEGER,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findings (
  id UUID PRIMARY KEY,
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
  scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
  title VARCHAR(255),
  description TEXT,
  severity VARCHAR(50),
  cvss_score FLOAT,
  status VARCHAR(50),
  remediation TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidence (
  id UUID PRIMARY KEY,
  engagement_id UUID NOT NULL REFERENCES engagements(id) ON DELETE CASCADE,
  asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
  scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
  finding_id UUID REFERENCES findings(id) ON DELETE CASCADE,
  name VARCHAR(255),
  type VARCHAR(50),
  size_bytes BIGINT,
  content_path VARCHAR(500),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
