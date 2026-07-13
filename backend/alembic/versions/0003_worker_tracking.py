"""Add worker/agent tracking tables

Revision ID: 0003
Revises: 0002_plugin_configuration
Create Date: 2026-07-13 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002_plugin_configuration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create WorkerStatus enum
    worker_status_enum = postgresql.ENUM(
        'online',
        'offline',
        'busy',
        'paused',
        name='workerstatus'
    )
    worker_status_enum.create(op.get_bind())

    # Create WorkerType enum
    worker_type_enum = postgresql.ENUM(
        'reconnaissance',
        'vulnerability_assessment',
        'exploitation',
        'evidence',
        'reporting',
        name='workertype'
    )
    worker_type_enum.create(op.get_bind())

    # Create workers table
    op.create_table(
        'workers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('type', worker_type_enum, nullable=False),
        sa.Column('status', worker_status_enum, server_default='online', nullable=False),

        sa.Column('hostname', sa.String(255)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('port', sa.Integer(), server_default='5000'),

        sa.Column('cpu_usage', sa.Float(), server_default='0.0'),
        sa.Column('memory_usage', sa.Float(), server_default='0.0'),
        sa.Column('disk_usage', sa.Float(), server_default='0.0'),

        sa.Column('current_job_id', postgresql.UUID(as_uuid=True)),
        sa.Column('active_jobs', sa.Integer(), server_default='0'),
        sa.Column('queue_depth', sa.Integer(), server_default='0'),

        sa.Column('completed_jobs', sa.Integer(), server_default='0'),
        sa.Column('failed_jobs', sa.Integer(), server_default='0'),
        sa.Column('total_runtime_seconds', sa.Integer(), server_default='0'),

        sa.Column('supported_plugins', postgresql.JSONB(), server_default='{}'),
        sa.Column('capabilities', postgresql.JSONB(), server_default='{}'),
        sa.Column('metadata', postgresql.JSONB()),

        sa.Column('is_enabled', sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column('last_heartbeat', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),

        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_workers_name', 'workers', ['name'])
    op.create_index('ix_workers_status', 'workers', ['status'])
    op.create_index('ix_workers_type', 'workers', ['type'])
    op.create_index('ix_workers_is_enabled', 'workers', ['is_enabled'])
    op.create_index('ix_workers_last_heartbeat', 'workers', ['last_heartbeat'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_workers_last_heartbeat', table_name='workers')
    op.drop_index('ix_workers_is_enabled', table_name='workers')
    op.drop_index('ix_workers_type', table_name='workers')
    op.drop_index('ix_workers_status', table_name='workers')
    op.drop_index('ix_workers_name', table_name='workers')

    # Drop table
    op.drop_table('workers')

    # Drop enums
    worker_status_enum = postgresql.ENUM(
        'online',
        'offline',
        'busy',
        'paused',
        name='workerstatus'
    )
    worker_status_enum.drop(op.get_bind())

    worker_type_enum = postgresql.ENUM(
        'reconnaissance',
        'vulnerability_assessment',
        'exploitation',
        'evidence',
        'reporting',
        name='workertype'
    )
    worker_type_enum.drop(op.get_bind())
