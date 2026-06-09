"""change folder parent_id ondelete from CASCADE to SET NULL

Revision ID: 007
Revises: 006
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("folders_parent_id_fkey", "folders", type_="foreignkey")
    op.create_foreign_key(
        "folders_parent_id_fkey",
        "folders",
        "folders",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("folders_parent_id_fkey", "folders", type_="foreignkey")
    op.create_foreign_key(
        "folders_parent_id_fkey",
        "folders",
        "folders",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )
