"""add folders table and folder_id/sort_order to notes

Revision ID: 005
Revises: 004
Create Date: 2026-06-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "folders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("folders.id", ondelete="CASCADE"), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_folders_parent_id", "folders", ["parent_id"])
    op.create_index("idx_folders_sort_order", "folders", ["sort_order"])

    op.add_column("notes", sa.Column("folder_id", UUID(as_uuid=True), sa.ForeignKey("folders.id", ondelete="SET NULL"), nullable=True))
    op.add_column("notes", sa.Column("sort_order", sa.Integer(), server_default="0"))
    op.create_index("idx_notes_folder_id", "notes", ["folder_id"])


def downgrade() -> None:
    op.drop_index("idx_notes_folder_id", table_name="notes")
    op.drop_column("notes", "sort_order")
    op.drop_column("notes", "folder_id")
    op.drop_index("idx_folders_sort_order", table_name="folders")
    op.drop_index("idx_folders_parent_id", table_name="folders")
    op.drop_table("folders")
