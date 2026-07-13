"""Add plugin configuration tables - Phase 5 infrastructure

Revision ID: 0002
Revises: 0001_initial_schema
Create Date: 2026-07-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create config status enum
    status_enum = postgresql.ENUM(
        'draft',
        'active',
        'inactive',
        'deprecated',
        'archived',
        name='configstatus'
    )
    status_enum.create(op.get_bind())

    # Create plugin_configurations table
    op.create_table(
        'plugin_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plugin_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('version', sa.String(50), server_default='1.0.0'),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('env_vars', sa.JSON(), server_default='{}'),
        sa.Column('secrets', sa.JSON(), server_default='{}'),
        sa.Column('status', status_enum, server_default='draft', nullable=False),
        sa.Column('is_default', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('is_validated', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column('validation_errors', sa.JSON(), server_default='[]'),
        sa.Column('created_by', sa.String(255)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('activated_at', sa.DateTime()),
        sa.Column('last_used_at', sa.DateTime()),
        sa.Column('use_count', sa.String(), server_default='0'),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugin_registrations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for plugin_configurations
    op.create_index('ix_plugin_config_plugin_id', 'plugin_configurations', ['plugin_id'])
    op.create_index('ix_plugin_config_status', 'plugin_configurations', ['status'])
    op.create_index('ix_plugin_config_is_default', 'plugin_configurations', ['is_default'])
    op.create_index('ix_plugin_config_active', 'plugin_configurations', ['plugin_id', 'status'])

    # Create configuration_history table
    op.create_table(
        'configuration_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('config_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('changed_by', sa.String(255)),
        sa.Column('old_settings', sa.JSON()),
        sa.Column('new_settings', sa.JSON()),
        sa.Column('reason', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['config_id'], ['plugin_configurations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for configuration_history
    op.create_index('ix_config_history_config_id', 'configuration_history', ['config_id'])
    op.create_index('ix_config_history_action', 'configuration_history', ['action'])


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_config_history_action', table_name='configuration_history')
    op.drop_index('ix_config_history_config_id', table_name='configuration_history')
    op.drop_table('configuration_history')

    op.drop_index('ix_plugin_config_active', table_name='plugin_configurations')
    op.drop_index('ix_plugin_config_is_default', table_name='plugin_configurations')
    op.drop_index('ix_plugin_config_status', table_name='plugin_configurations')
    op.drop_index('ix_plugin_config_plugin_id', table_name='plugin_configurations')
    op.drop_table('plugin_configurations')

    # Drop enum
    status_enum = postgresql.ENUM(
        'draft',
        'active',
        'inactive',
        'deprecated',
        'archived',
        name='configstatus'
    )
    status_enum.drop(op.get_bind())
