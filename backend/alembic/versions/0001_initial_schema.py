"""Initial ReconHive schema

Revision ID: 0001
Revises:
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'engagements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('client', sa.String(255), nullable=False),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('owner', sa.String(255), nullable=False),
        sa.Column('team_members', sa.String(1000), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_engagements_status', 'engagements', ['status'])
    op.create_index('ix_engagements_is_active', 'engagements', ['is_active'])

    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('environment', sa.String(50), nullable=True),
        sa.Column('criticality', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('technology_stack', postgresql.JSON(), nullable=True),
        sa.Column('operating_system', sa.String(100), nullable=True),
        sa.Column('risk_score', sa.Float(), default=0.0),
        sa.Column('scan_history', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_assets_engagement_id', 'assets', ['engagement_id'])
    op.create_index('ix_assets_type', 'assets', ['type'])

    op.create_table(
        'targets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('port', sa.String(10), nullable=True),
        sa.Column('service', sa.String(100), nullable=True),
        sa.Column('protocol', sa.String(50), nullable=True),
        sa.Column('auth_type', sa.String(50), nullable=True),
        sa.Column('auth_credentials', postgresql.JSON(), nullable=True),
        sa.Column('is_in_scope', sa.Boolean(), default=True),
        sa.Column('priority', sa.String(20), default='medium'),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_targets_engagement_id', 'targets', ['engagement_id'])

    op.create_table(
        'scans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('plugin_names', postgresql.JSON(), nullable=True),
        sa.Column('configuration', postgresql.JSON(), nullable=True),
        sa.Column('status', sa.String(50), default='queued'),
        sa.Column('progress_percent', sa.Integer(), default=0),
        sa.Column('current_stage', sa.String(100), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('worker_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['targets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scans_engagement_id', 'scans', ['engagement_id'])

    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plugin_name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), default='queued'),
        sa.Column('priority', sa.Integer(), default=5),
        sa.Column('queue', sa.String(100), default='default'),
        sa.Column('worker_id', sa.String(255), nullable=True),
        sa.Column('configuration', postgresql.JSON(), nullable=True),
        sa.Column('progress_percent', sa.Integer(), default=0),
        sa.Column('retries', sa.Integer(), default=0),
        sa.Column('max_retries', sa.Integer(), default=3),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('result_summary', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_jobs_scan_id', 'jobs', ['scan_id'])

    op.create_table(
        'plugin_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('plugin_class_path', sa.String(255), nullable=False),
        sa.Column('config_schema', postgresql.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evidence_scan_id', 'evidence', ['scan_id'])

    op.create_table(
        'findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='open'),
        sa.Column('cvss_score', sa.Float(), nullable=True),
        sa.Column('cwe_id', sa.String(20), nullable=True),
        sa.Column('owasp_id', sa.String(20), nullable=True),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_findings_engagement_id', 'findings', ['engagement_id'])

def downgrade() -> None:
    op.drop_table('findings')
    op.drop_table('evidence')
    op.drop_table('plugin_registrations')
    op.drop_table('jobs')
    op.drop_table('scans')
    op.drop_table('targets')
    op.drop_table('assets')
    op.drop_table('engagements')
