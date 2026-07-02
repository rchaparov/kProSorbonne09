"""Add performance indexes on hot query fields.

Revision ID: 009_performance_indexes
Revises: 008_checklist_deadline
Create Date: 2026-06-25

"""
from alembic import op


revision = "009_performance_indexes"
down_revision = "008_checklist_deadline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_notes_project_id", "notes", ["project_id"])
    op.create_index("ix_notes_parent_id", "notes", ["parent_id"])
    op.create_index(
        "ix_notifications_user_id_is_read",
        "notifications",
        ["user_id", "is_read"],
    )
    op.create_index("ix_project_members_user_id", "project_members", ["user_id"])
    op.create_index("ix_checklist_items_project_id", "checklist_items", ["project_id"])
    op.create_index("ix_note_mentions_user_id", "note_mentions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_note_mentions_user_id", table_name="note_mentions")
    op.drop_index("ix_checklist_items_project_id", table_name="checklist_items")
    op.drop_index("ix_project_members_user_id", table_name="project_members")
    op.drop_index("ix_notifications_user_id_is_read", table_name="notifications")
    op.drop_index("ix_notes_parent_id", table_name="notes")
    op.drop_index("ix_notes_project_id", table_name="notes")
