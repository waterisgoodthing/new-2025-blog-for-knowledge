"""add managed content entries

Revision ID: 010
Revises: 009
Create Date: 2026-06-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "managed_content_entries" not in inspector.get_table_names():
        op.create_table(
            "managed_content_entries",
            sa.Column("key", sa.String(length=100), primary_key=True),
            sa.Column("data", JSON, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        return

    required = {"key", "data", "created_at", "updated_at"}
    existing = {column["name"] for column in inspector.get_columns("managed_content_entries")}
    missing = required - existing
    if missing:
        raise RuntimeError(f"managed_content_entries is missing required columns: {sorted(missing)}")


def downgrade() -> None:
    op.drop_table("managed_content_entries")
