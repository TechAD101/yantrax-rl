"""create journal_entries table

Revision ID: 0001_create_journal
Revises: 
Create Date: 2025-11-19
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_journal'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'journal_entries',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('reward', sa.Float(), nullable=True),
        sa.Column('balance', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True)
    )

def downgrade():
    op.drop_table('journal_entries')
