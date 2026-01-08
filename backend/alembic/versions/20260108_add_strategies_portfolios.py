"""add strategies, profiles and portfolio tables

Revision ID: 20260108_add_strategies_portfolios
Revises: 
Create Date: 2026-01-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260108_add_strategies_portfolios'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'strategy_profiles',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('archetype', sa.String(64), nullable=True),
        sa.Column('params', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'strategies',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('archetype', sa.String(64), nullable=True),
        sa.Column('params', sa.JSON, nullable=True),
        sa.Column('published', sa.Integer, nullable=False, server_default='0'),
        sa.Column('metrics', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'portfolios',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('owner_id', sa.Integer, nullable=True),
        sa.Column('risk_profile', sa.String(32), nullable=False, server_default='moderate'),
        sa.Column('initial_capital', sa.Float, nullable=False, server_default='100000.0'),
        sa.Column('current_value', sa.Float, nullable=True),
        sa.Column('strategy_profile_id', sa.Integer, sa.ForeignKey('strategy_profiles.id'), nullable=True),
        sa.Column('meta', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'portfolio_positions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('portfolio_id', sa.Integer, sa.ForeignKey('portfolios.id'), nullable=False),
        sa.Column('symbol', sa.String(32), nullable=False),
        sa.Column('quantity', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('avg_price', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

    op.create_table(
        'journal_entries',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('action', sa.String(32), nullable=False),
        sa.Column('reward', sa.Float, nullable=True),
        sa.Column('balance', sa.Float, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, nullable=True)
    )


def downgrade():
    op.drop_table('journal_entries')
    op.drop_table('portfolio_positions')
    op.drop_table('portfolios')
    op.drop_table('strategies')
    op.drop_table('strategy_profiles')
