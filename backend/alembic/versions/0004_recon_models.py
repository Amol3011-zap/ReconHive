"""Add reconnaissance models for Phase 2

Revision ID: 0004
Revises: 0003_worker_tracking
Create Date: 2026-07-13 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '0004'
down_revision = '0003_worker_tracking'
branch_labels = None
depends_on = None

def upgrade():
    # Create subdomain table
    op.create_table(
        'subdomains',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('is_wildcard', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('status', sa.Enum('DISCOVERED', 'ALIVE', 'DEAD', 'PENDING_VERIFICATION', name='subdomainstatus'), nullable=False, server_default='DISCOVERED'),
        sa.Column('a_records', postgresql.JSONB(), nullable=True),
        sa.Column('aaaa_records', postgresql.JSONB(), nullable=True),
        sa.Column('cname', sa.String(255), nullable=True),
        sa.Column('mx_records', postgresql.JSONB(), nullable=True),
        sa.Column('txt_records', postgresql.JSONB(), nullable=True),
        sa.Column('ns_records', postgresql.JSONB(), nullable=True),
        sa.Column('sources', postgresql.JSONB(), nullable=True),
        sa.Column('first_discovered_date', sa.DateTime(), nullable=False),
        sa.Column('last_verified_date', sa.DateTime(), nullable=True),
        sa.Column('last_active_date', sa.DateTime(), nullable=True),
        sa.Column('is_takeover_candidate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('technologies', postgresql.JSONB(), nullable=True),
        sa.Column('endpoints', postgresql.JSONB(), nullable=True),
        sa.Column('custom_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subdomains_engagement_id', 'subdomains', ['engagement_id'])
    op.create_index('ix_subdomains_asset_id', 'subdomains', ['asset_id'])
    op.create_index('ix_subdomains_name', 'subdomains', ['name'])
    op.create_index('ix_subdomains_status', 'subdomains', ['status'])
    op.create_index('ix_subdomains_is_takeover_candidate', 'subdomains', ['is_takeover_candidate'])

    # Create dns_records table
    op.create_table(
        'dns_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subdomain_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hostname', sa.String(255), nullable=False),
        sa.Column('record_type', sa.Enum('A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'PTR', 'SOA', 'SRV', 'CAA', name='dnsrecordtype'), nullable=False),
        sa.Column('value', sa.String(500), nullable=False),
        sa.Column('ttl', sa.Integer(), nullable=True),
        sa.Column('resolver_used', sa.String(100), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.String(10), nullable=False, server_default='unknown'),
        sa.Column('raw_response', postgresql.JSONB(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(), nullable=True),
        sa.Column('discovered_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subdomain_id'], ['subdomains.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_dns_records_engagement_id', 'dns_records', ['engagement_id'])
    op.create_index('ix_dns_records_subdomain_id', 'dns_records', ['subdomain_id'])
    op.create_index('ix_dns_records_hostname', 'dns_records', ['hostname'])
    op.create_index('ix_dns_records_type', 'dns_records', ['record_type'])

    # Create url_endpoints table
    op.create_table(
        'url_endpoints',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subdomain_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('url', sa.String(1000), nullable=False),
        sa.Column('method', sa.Enum('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', name='httpmethod'), nullable=False, server_default='GET'),
        sa.Column('status', sa.Enum('ALIVE', 'DEAD', 'REDIRECT', 'TIMEOUT', 'ERROR', 'PENDING', name='urlstatus'), nullable=False, server_default='PENDING'),
        sa.Column('response_status_code', sa.Integer(), nullable=True),
        sa.Column('response_content_type', sa.String(100), nullable=True),
        sa.Column('response_content_length', sa.Integer(), nullable=True),
        sa.Column('response_headers', postgresql.JSONB(), nullable=True),
        sa.Column('response_body_preview', sa.String(2000), nullable=True),
        sa.Column('page_title', sa.String(255), nullable=True),
        sa.Column('page_description', sa.String(500), nullable=True),
        sa.Column('technologies', postgresql.JSONB(), nullable=True),
        sa.Column('discovered_from', sa.String(100), nullable=True),
        sa.Column('discovered_date', sa.DateTime(), nullable=True),
        sa.Column('first_seen_date', sa.DateTime(), nullable=False),
        sa.Column('last_probed_date', sa.DateTime(), nullable=True),
        sa.Column('has_form', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_redirect', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('redirect_to', sa.String(1000), nullable=True),
        sa.Column('has_login', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_authenticated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('screenshot_path', sa.String(500), nullable=True),
        sa.Column('favicon_hash', sa.String(100), nullable=True),
        sa.Column('custom_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subdomain_id'], ['subdomains.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_url_endpoints_engagement_id', 'url_endpoints', ['engagement_id'])
    op.create_index('ix_url_endpoints_asset_id', 'url_endpoints', ['asset_id'])
    op.create_index('ix_url_endpoints_url', 'url_endpoints', ['url'])
    op.create_index('ix_url_endpoints_status', 'url_endpoints', ['status'])

def downgrade():
    op.drop_index('ix_url_endpoints_status', table_name='url_endpoints')
    op.drop_index('ix_url_endpoints_url', table_name='url_endpoints')
    op.drop_index('ix_url_endpoints_asset_id', table_name='url_endpoints')
    op.drop_index('ix_url_endpoints_engagement_id', table_name='url_endpoints')
    op.drop_table('url_endpoints')

    op.drop_index('ix_dns_records_type', table_name='dns_records')
    op.drop_index('ix_dns_records_hostname', table_name='dns_records')
    op.drop_index('ix_dns_records_subdomain_id', table_name='dns_records')
    op.drop_index('ix_dns_records_engagement_id', table_name='dns_records')
    op.drop_table('dns_records')

    op.drop_index('ix_subdomains_is_takeover_candidate', table_name='subdomains')
    op.drop_index('ix_subdomains_status', table_name='subdomains')
    op.drop_index('ix_subdomains_name', table_name='subdomains')
    op.drop_index('ix_subdomains_asset_id', table_name='subdomains')
    op.drop_index('ix_subdomains_engagement_id', table_name='subdomains')
    op.drop_table('subdomains')
