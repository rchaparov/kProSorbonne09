"""Add checklist_item_assignees and remove assigned_to column.

Revision ID: 007_checklist_multi_assignees
Revises: 006_note_replies
Create Date: 2026-06-25

"""
from alembic import op
import sqlalchemy as sa


revision = "007_checklist_multi_assignees"
down_revision = "006_note_replies"
branch_labels = None
depends_on = None


def _drop_assigned_to_fk() -> None:
    """Drop foreign key on checklist_items.assigned_to if present."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for fk in inspector.get_foreign_keys("checklist_items"):
        if fk.get("constrained_columns") == ["assigned_to"]:
            op.drop_constraint(fk["name"], "checklist_items", type_="foreignkey")
            return


def upgrade() -> None:
    op.create_table(
        "checklist_item_assignees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["checklist_items.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id", "user_id", name="uq_checklist_assignees"),
    )
    op.execute(
        """
        INSERT INTO checklist_item_assignees (item_id, user_id)
        SELECT id, assigned_to FROM checklist_items
        WHERE assigned_to IS NOT NULL
        """
    )
    _drop_assigned_to_fk()
    op.drop_column("checklist_items", "assigned_to")


def downgrade() -> None:
    op.add_column(
        "checklist_items",
        sa.Column("assigned_to", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_checklist_items_assigned_to",
        "checklist_items",
        "users",
        ["assigned_to"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        """
        UPDATE checklist_items ci
        SET assigned_to = (
            SELECT user_id FROM checklist_item_assignees cia
            WHERE cia.item_id = ci.id
            LIMIT 1
        )
        """
    )
    op.drop_table("checklist_item_assignees")
