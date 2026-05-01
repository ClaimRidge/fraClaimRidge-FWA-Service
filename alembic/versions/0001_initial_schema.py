"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-05-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create Enum types
    op.execute("CREATE TYPE severity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')")
    op.execute("CREATE TYPE casestatus AS ENUM ('OPEN', 'IN_PROGRESS', 'RESOLVED_FRAUD', 'RESOLVED_LEGITIMATE', 'CLOSED')")

    # Create Tables
    op.create_table(
        'fraud_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('claim_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('l1_anomaly_score', sa.Float(), nullable=True),
        sa.Column('l2_drift_score', sa.Float(), nullable=True),
        sa.Column('l3_graph_score', sa.Float(), nullable=True),
        sa.Column('l4_timeseries_score', sa.Float(), nullable=True),
        sa.Column('composite_score', sa.Float(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    
    op.create_table(
        'fraud_flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('layer', sa.String(), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity'), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'fraud_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('OPEN', 'IN_PROGRESS', 'RESOLVED_FRAUD', 'RESOLVED_LEGITIMATE', 'CLOSED', name='casestatus'), server_default='OPEN'),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity'), nullable=False),
        sa.Column('investigator_id', sa.String(), nullable=True),
        sa.Column('summary', sa.String(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(), server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        'case_flags',
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fraud_cases.id'), primary_key=True),
        sa.Column('flag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fraud_flags.id'), primary_key=True),
    )

def downgrade():
    op.drop_table('case_flags')
    op.drop_table('fraud_cases')
    op.drop_table('fraud_flags')
    op.drop_table('fraud_scores')
    op.execute("DROP TYPE casestatus")
    op.execute("DROP TYPE severity")
