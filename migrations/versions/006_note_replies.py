"""Add note replies and quoted content.

Revision ID: 006_note_replies
Revises: 005_temp_file_tokens
Create Date: 2026-06-25

"""
from alembic import op
import sqlalchemy as sa


revision = "006_note_replies"
down_revision = "005_temp_file_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notes",
        sa.Column("parent_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "notes",
        sa.Column("quoted_content", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_notes_parent_id",
        "notes",
        "notes",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_notes_parent_id", "notes", type_="foreignkey")
    op.drop_column("notes", "quoted_content")
    op.drop_column("notes", "parent_id")
