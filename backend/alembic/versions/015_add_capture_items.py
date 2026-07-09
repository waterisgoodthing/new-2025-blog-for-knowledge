"""add capture_items

Revision ID: 015
Revises: 014
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "015"
down_revision: str | None = "014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "capture_items" in inspector.get_table_names():
        raise RuntimeError("Batch 8 target table already exists: capture_items")

    op.create_table(
        "capture_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), server_default="uploaded", nullable=False),
        sa.Column("recognized_text", sa.Text(), nullable=True),
        sa.Column("user_error_context", sa.Text(), nullable=True),
        sa.Column("question_draft_text", sa.Text(), nullable=True),
        sa.Column("analysis_draft_text", sa.Text(), nullable=True),
        sa.Column("error_summary_draft", sa.Text(), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=True),
        sa.Column("knowledge_point_suggestions", postgresql.JSON(), server_default="[]", nullable=False),
        sa.Column("model_output_version", sa.String(20), server_default="v1", nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_stage", sa.String(20), nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message_safe", sa.String(300), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mistake_draft_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_attachment_id"], ["attachments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mistake_draft_item_id"], ["draft_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("mistake_draft_item_id", name="uq_capture_items_mistake_draft"),
        sa.CheckConstraint(
            "status IN ('uploaded','recognizing','recognized','drafting','ready','failed','converted','archived')",
            name="ck_capture_items_status",
        ),
        sa.CheckConstraint(
            "(status = 'converted' AND mistake_draft_item_id IS NOT NULL) OR "
            "(status <> 'converted' AND mistake_draft_item_id IS NULL)",
            name="ck_capture_items_conversion",
        ),
        sa.CheckConstraint("attempt_count >= 0", name="ck_capture_items_attempt_count"),
        sa.CheckConstraint(
            "last_stage IS NULL OR last_stage IN ('recognize','draft','convert')",
            name="ck_capture_items_last_stage",
        ),
    )
    op.create_index("idx_capture_items_status_created", "capture_items", ["status", "created_at"])
    op.create_index("idx_capture_items_source_attachment", "capture_items", ["source_attachment_id"])


def downgrade() -> None:
    op.drop_index("idx_capture_items_source_attachment", table_name="capture_items")
    op.drop_index("idx_capture_items_status_created", table_name="capture_items")
    op.drop_table("capture_items")
