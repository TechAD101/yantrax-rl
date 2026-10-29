"""add ceo_decision_records table for persistent CEO memory

Revision ID: 20261030_add_ceo_decision_records
Revises: 20260108_add_memecoins
Create Date: 2026-10-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20261030_add_ceo_decision_records'
down_revision = '20260108_add_memecoins'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ceo_decision_records',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('decision_type', sa.String(32), nullable=False),
        sa.Column('symbol', sa.String(32), nullable=True),
        sa.Column('decision_hash', sa.String(16), nullable=True),
        sa.Column('reasoning', sa.Text, nullable=False),
        sa.Column('confidence', sa.Float, nullable=False),
        sa.Column('outcome_id', sa.String(64), nullable=True),
        sa.Column('position_id', sa.String(64), nullable=True),
        sa.Column('memory_tags', sa.JSON, nullable=True),
        sa.Column('metadata_json', sa.JSON, nullable=True),
    )
    op.create_index('ix_ceo_decision_records_symbol', 'ceo_decision_records', ['symbol'])
    op.create_index('ix_ceo_decision_records_outcome_id', 'ceo_decision_records', ['outcome_id'])
    op.create_index('ix_ceo_decision_records_position_id', 'ceo_decision_records', ['position_id'])

    op.create_table(
        'learning_state',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('key', sa.String(128), nullable=False, unique=True),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('learning_state')
    op.drop_index('ix_ceo_decision_records_position_id', table_name='ceo_decision_records')
    op.drop_index('ix_ceo_decision_records_outcome_id', table_name='ceo_decision_records')
    op.drop_index('ix_ceo_decision_records_symbol', table_name='ceo_decision_records')
    op.drop_table('ceo_decision_records')
