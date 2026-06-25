"""Add temp_file_tokens table.

Revision ID: 005_temp_file_tokens
Revises: 004_checklist_note_materials
Create Date: 2026-06-25

"""
from alembic import op
import sqlalchemy as sa


revision = "005_temp_file_tokens"
down_revision = "004_checklist_note_materials"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "temp_file_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=36), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_temp_file_tokens_token", "temp_file_tokens", ["token"])


def downgrade() -> None:
    op.drop_index("ix_temp_file_tokens_token", table_name="temp_file_tokens")
    op.drop_table("temp_file_tokens")
