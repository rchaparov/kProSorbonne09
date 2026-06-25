"""Add deadline column to checklist_items.

Revision ID: 008_checklist_deadline
Revises: 007_checklist_multi_assignees
Create Date: 2026-06-25

"""
from alembic import op
import sqlalchemy as sa


revision = "008_checklist_deadline"
down_revision = "007_checklist_multi_assignees"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "checklist_items",
        sa.Column("deadline", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("checklist_items", "deadline")
