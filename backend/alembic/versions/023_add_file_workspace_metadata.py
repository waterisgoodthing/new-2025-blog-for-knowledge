"""add file workspace metadata

Revision ID: 023
Revises: 022
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "023"
down_revision: str | None = "022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("attachments", sa.Column("display_name", sa.String(255), nullable=True))
    op.add_column("attachments", sa.Column("folder_id", sa.UUID(), nullable=True))
    op.add_column("attachments", sa.Column("trashed_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE attachments SET display_name = original_name WHERE display_name IS NULL")
    op.alter_column("attachments", "display_name", nullable=False)
    op.create_foreign_key("fk_attachments_folder_id", "attachments", "folders", ["folder_id"], ["id"], ondelete="SET NULL")
    op.drop_constraint("ck_attachments_status", "attachments", type_="check")
    op.create_check_constraint(
        "ck_attachments_status", "attachments", "status IN ('active','missing','trashed','deleted')"
    )
    op.create_index("idx_attachments_folder_display", "attachments", ["folder_id", "display_name"])


def downgrade() -> None:
    op.drop_index("idx_attachments_folder_display", table_name="attachments")
    op.drop_constraint("ck_attachments_status", "attachments", type_="check")
    op.create_check_constraint("ck_attachments_status", "attachments", "status IN ('active','missing','deleted')")
    op.drop_constraint("fk_attachments_folder_id", "attachments", type_="foreignkey")
    op.drop_column("attachments", "trashed_at")
    op.drop_column("attachments", "folder_id")
    op.drop_column("attachments", "display_name")
