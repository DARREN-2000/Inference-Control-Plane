"""Add role column to api_keys

Revision ID: 20260829_0002
Revises: 20260425_0001
Create Date: 2026-08-29 18:25:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '20260829_0002'
down_revision = '20260425_0001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add the column with a default value so it doesn't fail on existing rows
    op.add_column('api_keys', sa.Column('role', sa.String(length=32), server_default='tenant', nullable=False))

def downgrade() -> None:
    op.drop_column('api_keys', 'role')
