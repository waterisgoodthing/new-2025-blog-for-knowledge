"""add attachments

Revision ID: 014
Revises: 013
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "014"
down_revision: str | None = "013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    targets = {"attachments", "attachment_links"}
    existing = targets.intersection(inspector.get_table_names())
    if existing:
        raise RuntimeError(
            "Batch 5 target tables already exist: " + ", ".join(sorted(existing))
        )

    op.create_table(
        "attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("storage_provider", sa.String(30), server_default="local", nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("visibility", sa.String(20), server_default="private", nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("storage_provider='local'", name="ck_attachments_storage_provider"),
        sa.CheckConstraint("visibility='private'", name="ck_attachments_visibility"),
        sa.CheckConstraint("status IN ('active','missing','deleted')", name="ck_attachments_status"),
        sa.CheckConstraint("size_bytes>=0", name="ck_attachments_size"),
        sa.CheckConstraint("char_length(checksum_sha256)=64", name="ck_attachments_checksum"),
    )
    op.create_index("idx_attachments_status_created", "attachments", ["status", "created_at"])
    op.create_index("idx_attachments_checksum", "attachments", ["checksum_sha256"])

    op.create_table(
        "attachment_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.String(64), nullable=False),
        sa.Column("purpose", sa.String(30), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["attachment_id"], ["attachments.id"], ondelete="CASCADE"),
        sa.CheckConstraint(
            "target_type IN ('question_draft','question','mistake')",
            name="ck_attachment_links_target_type",
        ),
        sa.CheckConstraint(
            "purpose IN ('source','question','answer','inline','ai_input','ai_output')",
            name="ck_attachment_links_purpose",
        ),
        sa.UniqueConstraint(
            "attachment_id",
            "target_type",
            "target_id",
            "purpose",
            name="uq_attachment_links_target_purpose",
        ),
    )
    op.create_index("idx_attachment_links_attachment", "attachment_links", ["attachment_id"])
    op.create_index("idx_attachment_links_target", "attachment_links", ["target_type", "target_id"])


def downgrade() -> None:
    op.drop_table("attachment_links")
    op.drop_table("attachments")
