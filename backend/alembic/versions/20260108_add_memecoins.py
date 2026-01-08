"""add memecoin table

Revision ID: 20260108_add_memecoins
Revises: 20260108_add_strategies_portfolios
Create Date: 2026-01-08 00:15:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260108_add_memecoins'
down_revision = '20260108_add_strategies_portfolios'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'memecoins',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(32), nullable=False, unique=True),
        sa.Column('score', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('memecoins')
