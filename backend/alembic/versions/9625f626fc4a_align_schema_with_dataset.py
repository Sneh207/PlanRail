"""align_schema_with_dataset

Revision ID: 9625f626fc4a
Revises: 8ffd8b42e2f7
Create Date: 2026-09-02 13:41:03.008617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9625f626fc4a'
down_revision: Union[str, Sequence[str], None] = '8ffd8b42e2f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to align with PlanRail dataset."""
    # 1. Update STATIONS
    op.add_column('stations', sa.Column('station_id', sa.String(length=30), nullable=False))
    op.add_column('stations', sa.Column('station_name', sa.String(length=100), nullable=False))
    op.add_column('stations', sa.Column('km_from_ndls', sa.Float(), nullable=True))
    op.add_column('stations', sa.Column('source_type', sa.String(length=50), nullable=True))
    op.add_column('stations', sa.Column('source_note', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_stations_station_id'), 'stations', ['station_id'], unique=True)

    # 2. Update RAILWAY_SECTIONS
    op.add_column('railway_sections', sa.Column('section_id', sa.String(length=30), nullable=False))
    op.add_column('railway_sections', sa.Column('from_station_code', sa.String(length=20), nullable=False))
    op.add_column('railway_sections', sa.Column('to_station_code', sa.String(length=20), nullable=False))
    op.add_column('railway_sections', sa.Column('from_station_name', sa.String(length=100), nullable=True))
    op.add_column('railway_sections', sa.Column('to_station_name', sa.String(length=100), nullable=True))
    op.add_column('railway_sections', sa.Column('distance_km', sa.Float(), nullable=False))
    op.add_column('railway_sections', sa.Column('track_configuration', sa.String(length=50), nullable=True))
    op.add_column('railway_sections', sa.Column('electrification', sa.String(length=50), nullable=True))
    op.add_column('railway_sections', sa.Column('traffic_class', sa.String(length=50), nullable=True))
    op.alter_column('railway_sections', 'section_code', existing_type=sa.VARCHAR(length=20), type_=sa.String(length=30), existing_nullable=False)
    op.alter_column('railway_sections', 'name', existing_type=sa.VARCHAR(length=100), nullable=True)
    op.drop_index(op.f('ix_railway_sections_end_station_id'), table_name='railway_sections')
    op.drop_index(op.f('ix_railway_sections_start_station_id'), table_name='railway_sections')
    op.drop_constraint(op.f('railway_sections_start_station_id_fkey'), 'railway_sections', type_='foreignkey')
    op.drop_constraint(op.f('railway_sections_end_station_id_fkey'), 'railway_sections', type_='foreignkey')
    op.drop_column('railway_sections', 'end_station_id')
    op.drop_column('railway_sections', 'length_km')
    op.drop_column('railway_sections', 'start_station_id')
    op.create_index(op.f('ix_railway_sections_from_station_code'), 'railway_sections', ['from_station_code'], unique=False)
    op.create_index(op.f('ix_railway_sections_section_id'), 'railway_sections', ['section_id'], unique=True)
    op.create_index(op.f('ix_railway_sections_to_station_code'), 'railway_sections', ['to_station_code'], unique=False)
    op.create_foreign_key(None, 'railway_sections', 'stations', ['from_station_code'], ['station_code'])
    op.create_foreign_key(None, 'railway_sections', 'stations', ['to_station_code'], ['station_code'])

    # 3. Update TRAINS
    op.add_column('trains', sa.Column('origin_code', sa.String(length=20), nullable=True))
    op.add_column('trains', sa.Column('destination_code', sa.String(length=20), nullable=True))
    op.add_column('trains', sa.Column('service_pattern', sa.String(length=50), nullable=True))
    op.add_column('trains', sa.Column('is_synthetic_schedule', sa.Boolean(), nullable=False, server_default='true'))
    op.alter_column('trains', 'train_type', existing_type=postgresql.ENUM('PASSENGER', 'EXPRESS', 'FREIGHT', 'OTHER', name='traintype'), type_=sa.String(length=50), existing_nullable=False)
    op.drop_index(op.f('ix_trains_train_code'), table_name='trains')
    op.drop_index(op.f('ix_trains_train_number'), table_name='trains')
    op.create_index(op.f('ix_trains_train_number'), 'trains', ['train_number'], unique=True)
    op.drop_column('trains', 'train_code')

    # 4. Update ASSETS
    op.add_column('assets', sa.Column('asset_id', sa.String(length=30), nullable=False))
    op.add_column('assets', sa.Column('department', sa.String(length=50), nullable=True))
    op.add_column('assets', sa.Column('installation_year', sa.Integer(), nullable=True))
    op.alter_column('assets', 'asset_code', existing_type=sa.VARCHAR(length=30), nullable=True)
    op.alter_column('assets', 'name', existing_type=sa.VARCHAR(length=100), nullable=True)
    # Drop the old FK (pointing to railway_sections.id INTEGER) BEFORE altering column type
    op.drop_constraint('assets_section_id_fkey', 'assets', type_='foreignkey')
    # Also drop the station_id FK so we can cleanly alter the assets table
    op.drop_constraint('assets_station_id_fkey', 'assets', type_='foreignkey')
    # Now safe to change section_id type from INTEGER to VARCHAR(30)
    op.alter_column('assets', 'section_id', existing_type=sa.INTEGER(), type_=sa.String(length=30), existing_nullable=False)
    op.alter_column('assets', 'asset_type', existing_type=postgresql.ENUM('TRACK', 'SIGNAL', 'POINTS', 'ELECTRICAL', 'BRIDGE', 'OTHER', name='assettype'), type_=sa.String(length=50), existing_nullable=False)
    op.alter_column('assets', 'criticality', existing_type=postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='criticalitylevel'), type_=sa.String(length=50), nullable=True)
    op.drop_index(op.f('ix_assets_asset_code'), table_name='assets')
    op.create_index(op.f('ix_assets_asset_id'), 'assets', ['asset_id'], unique=True)
    # Re-create FK pointing to the new railway_sections.section_id (VARCHAR)
    op.create_foreign_key('fk_assets_section_id', 'assets', 'railway_sections', ['section_id'], ['section_id'])

    # 5. Drop obsolete tables and constraints
    op.drop_index(op.f('ix_block_tasks_maintenance_task_id'), table_name='block_tasks')
    op.drop_constraint(op.f('block_tasks_maintenance_task_id_fkey'), 'block_tasks', type_='foreignkey')
    op.drop_constraint(op.f('uq_block_maintenance_task'), 'block_tasks', type_='unique')

    op.drop_index(op.f('ix_block_windows_section_id'), table_name='block_windows')
    op.drop_index(op.f('ix_block_windows_window_code'), table_name='block_windows')
    op.drop_constraint(op.f('optimized_blocks_block_window_id_fkey'), 'optimized_blocks', type_='foreignkey')
    op.drop_index(op.f('ix_optimized_blocks_block_window_id'), table_name='optimized_blocks')
    op.drop_table('block_windows')

    # Drop maintenance_compatibility FKs + indexes that reference maintenance_tasks BEFORE dropping maintenance_tasks.
    # (The rest of maintenance_compatibility restructuring happens in section 7.)
    op.drop_index(op.f('ix_maintenance_compatibility_task_a_id'), table_name='maintenance_compatibility')
    op.drop_index(op.f('ix_maintenance_compatibility_task_b_id'), table_name='maintenance_compatibility')
    op.drop_constraint(op.f('uq_task_pair'), 'maintenance_compatibility', type_='unique')
    op.drop_constraint(op.f('maintenance_compatibility_task_a_id_fkey'), 'maintenance_compatibility', type_='foreignkey')
    op.drop_constraint(op.f('maintenance_compatibility_task_b_id_fkey'), 'maintenance_compatibility', type_='foreignkey')
    op.drop_constraint(op.f('chk_no_self_compatibility'), 'maintenance_compatibility', type_='check')

    # Now safe to drop maintenance_tasks (no more FKs pointing to it)
    op.drop_index(op.f('idx_maint_task_search'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_asset_id'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_due_date'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_priority_score'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_section_id'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_status'), table_name='maintenance_tasks')
    op.drop_index(op.f('ix_maintenance_tasks_task_code'), table_name='maintenance_tasks')
    op.drop_table('maintenance_tasks')

    # 6. Create NEW tables
    op.create_table('crew_availability',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('crew_id', sa.String(length=30), nullable=False),
        sa.Column('crew_name', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=50), nullable=False),
        sa.Column('available_from_hour', sa.Integer(), nullable=False),
        sa.Column('available_to_hour', sa.Integer(), nullable=False),
        sa.Column('team_size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crew_availability_crew_id'), 'crew_availability', ['crew_id'], unique=True)

    op.create_table('train_schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('schedule_id', sa.String(length=30), nullable=False),
        sa.Column('train_number', sa.String(length=30), nullable=False),
        sa.Column('station_code', sa.String(length=20), nullable=False),
        sa.Column('station_name', sa.String(length=100), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('arrival_time', sa.String(length=20), nullable=True),
        sa.Column('departure_time', sa.String(length=20), nullable=True),
        sa.Column('day', sa.Integer(), nullable=False),
        sa.Column('km_from_origin', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['station_code'], ['stations.station_code'], ),
        sa.ForeignKeyConstraint(['train_number'], ['trains.train_number'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_train_sched_lookup', 'train_schedules', ['train_number', 'station_code', 'sequence'], unique=False)
    op.create_index(op.f('ix_train_schedules_schedule_id'), 'train_schedules', ['schedule_id'], unique=True)
    op.create_index(op.f('ix_train_schedules_station_code'), 'train_schedules', ['station_code'], unique=False)
    op.create_index(op.f('ix_train_schedules_train_number'), 'train_schedules', ['train_number'], unique=False)

    op.create_table('maintenance_windows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('window_id', sa.String(length=30), nullable=False),
        sa.Column('section_id', sa.String(length=30), nullable=False),
        sa.Column('start_hour', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.String(length=20), nullable=False),
        sa.Column('end_time', sa.String(length=20), nullable=False),
        sa.Column('expected_train_count', sa.Integer(), nullable=False),
        sa.Column('traffic_level', sa.String(length=50), nullable=False),
        sa.Column('is_feasible', sa.Boolean(), nullable=False),
        sa.Column('window_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['section_id'], ['railway_sections.section_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_maint_win_lookup', 'maintenance_windows', ['section_id', 'start_hour', 'is_feasible'], unique=False)
    op.create_index(op.f('ix_maintenance_windows_section_id'), 'maintenance_windows', ['section_id'], unique=False)
    op.create_index(op.f('ix_maintenance_windows_window_id'), 'maintenance_windows', ['window_id'], unique=True)

    op.create_table('traffic_windows',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('traffic_window_id', sa.String(length=30), nullable=False),
        sa.Column('section_id', sa.String(length=30), nullable=False),
        sa.Column('hour', sa.Integer(), nullable=False),
        sa.Column('train_count', sa.Integer(), nullable=False),
        sa.Column('traffic_level', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['section_id'], ['railway_sections.section_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_traffic_win_lookup', 'traffic_windows', ['section_id', 'hour'], unique=False)
    op.create_index(op.f('ix_traffic_windows_section_id'), 'traffic_windows', ['section_id'], unique=False)
    op.create_index(op.f('ix_traffic_windows_traffic_window_id'), 'traffic_windows', ['traffic_window_id'], unique=True)

    op.create_table('maintenance_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('history_id', sa.String(length=30), nullable=False),
        sa.Column('asset_id', sa.String(length=30), nullable=False),
        sa.Column('section_id', sa.String(length=30), nullable=False),
        sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.Float(), nullable=False),
        sa.Column('downtime_hours', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
        sa.ForeignKeyConstraint(['section_id'], ['railway_sections.section_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_maint_hist_lookup', 'maintenance_history', ['asset_id', 'section_id', 'event_date'], unique=False)
    op.create_index(op.f('ix_maintenance_history_asset_id'), 'maintenance_history', ['asset_id'], unique=False)
    op.create_index(op.f('ix_maintenance_history_history_id'), 'maintenance_history', ['history_id'], unique=True)
    op.create_index(op.f('ix_maintenance_history_section_id'), 'maintenance_history', ['section_id'], unique=False)

    op.create_table('maintenance_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_id', sa.String(length=30), nullable=False),
        sa.Column('task_code', sa.String(length=30), nullable=True),
        sa.Column('asset_id', sa.String(length=30), nullable=False),
        sa.Column('section_id', sa.String(length=30), nullable=False),
        sa.Column('department', sa.String(length=50), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=True),
        sa.Column('maintenance_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.Float(), nullable=False),
        sa.Column('criticality_score', sa.Float(), nullable=False),
        sa.Column('duration_hours', sa.Float(), nullable=False),
        sa.Column('created_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('overdue_days', sa.Integer(), nullable=False),
        sa.Column('baseline_risk_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('priority_score', sa.Float(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('traffic_impact_score', sa.Float(), nullable=True),
        sa.Column('crew_required', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
        sa.ForeignKeyConstraint(['section_id'], ['railway_sections.section_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_maint_req_search', 'maintenance_requests', ['section_id', 'status', 'due_date'], unique=False)
    op.create_index(op.f('ix_maintenance_requests_asset_id'), 'maintenance_requests', ['asset_id'], unique=False)
    op.create_index(op.f('ix_maintenance_requests_due_date'), 'maintenance_requests', ['due_date'], unique=False)
    op.create_index(op.f('ix_maintenance_requests_priority_score'), 'maintenance_requests', ['priority_score'], unique=False)
    op.create_index(op.f('ix_maintenance_requests_request_id'), 'maintenance_requests', ['request_id'], unique=True)
    op.create_index(op.f('ix_maintenance_requests_section_id'), 'maintenance_requests', ['section_id'], unique=False)
    op.create_index(op.f('ix_maintenance_requests_status'), 'maintenance_requests', ['status'], unique=False)

    # 7. Update BLOCK_TASKS, MAINTENANCE_COMPATIBILITY, OPTIMIZED_BLOCKS
    op.add_column('block_tasks', sa.Column('maintenance_request_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_block_tasks_maintenance_request_id'), 'block_tasks', ['maintenance_request_id'], unique=False)
    op.create_unique_constraint('uq_block_maintenance_request', 'block_tasks', ['block_id', 'maintenance_request_id'])
    op.create_foreign_key(None, 'block_tasks', 'maintenance_requests', ['maintenance_request_id'], ['id'])
    op.drop_column('block_tasks', 'maintenance_task_id')

    # maintenance_compatibility: FKs/indexes/constraints already dropped in section 5 above.
    # Add new dataset-aligned columns and constraints here.
    op.add_column('maintenance_compatibility', sa.Column('department_a', sa.String(length=50), nullable=False))
    op.add_column('maintenance_compatibility', sa.Column('department_b', sa.String(length=50), nullable=False))
    op.add_column('maintenance_compatibility', sa.Column('compatibility', sa.Boolean(), nullable=False, server_default='true'))
    op.create_unique_constraint('uq_department_pair', 'maintenance_compatibility', ['department_a', 'department_b'])
    op.drop_column('maintenance_compatibility', 'task_b_id')
    op.drop_column('maintenance_compatibility', 'task_a_id')

    op.add_column('optimized_blocks', sa.Column('maintenance_window_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_optimized_blocks_maintenance_window_id'), 'optimized_blocks', ['maintenance_window_id'], unique=False)
    op.create_foreign_key(None, 'optimized_blocks', 'maintenance_windows', ['maintenance_window_id'], ['id'])
    op.drop_constraint(op.f('chk_block_times'), 'optimized_blocks', type_='check')
    op.drop_column('optimized_blocks', 'block_window_id')


def downgrade() -> None:
    """Downgrade schema."""
    pass
