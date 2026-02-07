"""Add status field to hotels table

Revision ID: 002_add_hotel_status
Revises: 001_initial
Create Date: 2025-01-15 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_hotel_status'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status column to hotels table
    op.add_column(
        'hotels',
        sa.Column('status', sa.String(length=20), nullable=True, server_default='active')
    )
    
    # Update existing rows to have 'active' status
    op.execute("UPDATE hotels SET status = 'active' WHERE status IS NULL")
    
    # Add a check constraint to ensure status has valid values
    op.create_check_constraint(
        'ck_hotel_status',
        'hotels',
        "status IN ('active', 'inactive', 'maintenance')"
    )


def downgrade() -> None:
    # Drop the check constraint first
    op.drop_constraint('ck_hotel_status', 'hotels', type_='check')
    
    # Drop the status column
    op.drop_column('hotels', 'status')
