"""add question drafts and questions

Revision ID: 012
Revises: 011
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "012"
down_revision: str | None = "011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    targets = {"draft_items", "question_drafts", "questions", "question_sources"}
    existing = targets.intersection(inspector.get_table_names())
    if existing:
        raise RuntimeError(
            "Batch 3 target tables already exist outside migration 012: "
            + ", ".join(sorted(existing))
        )

    op.create_table(
        "draft_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("draft_type", sa.String(30), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_id", sa.String(64), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("validation_errors", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("target_type", sa.String(30), nullable=True),
        sa.Column("target_id", sa.String(64), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("draft_type = 'question'", name="ck_draft_items_type"),
        sa.CheckConstraint("source_type = 'manual'", name="ck_draft_items_source"),
        sa.CheckConstraint(
            "status IN ('pending', 'needs_fix', 'rejected', 'converted')",
            name="ck_draft_items_status",
        ),
        sa.CheckConstraint("version > 0", name="ck_draft_items_version"),
        sa.CheckConstraint(
            "(status = 'converted' AND target_type = 'question' AND target_id IS NOT NULL) "
            "OR (status <> 'converted' AND target_type IS NULL AND target_id IS NULL)",
            name="ck_draft_items_conversion_target",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_draft_items_created_by", ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_draft_items_status_updated", "draft_items", ["status", "updated_at"])
    op.create_index("idx_draft_items_type_status", "draft_items", ["draft_type", "status"])

    op.create_table(
        "question_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("draft_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(30), nullable=False),
        sa.Column("options", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "question_type IN "
            "('single_choice', 'multiple_choice', 'true_false', 'short_answer', 'essay')",
            name="ck_question_drafts_type",
        ),
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('easy', 'medium', 'hard')",
            name="ck_question_drafts_difficulty",
        ),
        sa.ForeignKeyConstraint(
            ["draft_item_id"],
            ["draft_items.id"],
            name="fk_question_drafts_draft_item",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name="fk_question_drafts_subject",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("draft_item_id", name="uq_question_drafts_draft_item"),
    )
    op.create_index("idx_question_drafts_subject", "question_drafts", ["subject_id"])

    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(30), nullable=False),
        sa.Column("options", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("visibility", sa.String(20), server_default="private", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "question_type IN "
            "('single_choice', 'multiple_choice', 'true_false', 'short_answer', 'essay')",
            name="ck_questions_type",
        ),
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('easy', 'medium', 'hard')",
            name="ck_questions_difficulty",
        ),
        sa.CheckConstraint("status IN ('active', 'archived')", name="ck_questions_status"),
        sa.CheckConstraint("visibility = 'private'", name="ck_questions_visibility"),
        sa.CheckConstraint("version > 0", name="ck_questions_version"),
        sa.ForeignKeyConstraint(
            ["subject_id"], ["subjects.id"], name="fk_questions_subject", ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_questions_subject_status", "questions", ["subject_id", "status"])
    op.create_index("idx_questions_updated", "questions", ["updated_at"])

    op.create_table(
        "question_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("source_name", sa.String(200), nullable=True),
        sa.Column("source_ref", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("source_type = 'manual'", name="ck_question_sources_type"),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name="fk_question_sources_question",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_type", "source_ref", name="uq_question_sources_ref"),
    )
    op.create_index("idx_question_sources_question", "question_sources", ["question_id"])


def downgrade() -> None:
    op.execute(
        "DELETE FROM knowledge_point_links "
        "WHERE target_type IN ('question', 'question_draft')"
    )
    op.drop_table("question_sources")
    op.drop_table("questions")
    op.drop_table("question_drafts")
    op.drop_table("draft_items")
