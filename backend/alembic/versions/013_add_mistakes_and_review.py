"""add mistakes and review

Revision ID: 013
Revises: 012
"""

from collections.abc import Sequence
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "013"
down_revision: str | None = "012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    targets = {"mistake_drafts", "mistakes", "review_items", "review_records"}
    existing = targets.intersection(inspector.get_table_names())
    if existing:
        raise RuntimeError("Batch 4 target tables already exist: " + ", ".join(sorted(existing)))
    checks = {item["name"] for item in inspector.get_check_constraints("draft_items")}
    required = {"ck_draft_items_type", "ck_draft_items_source", "ck_draft_items_conversion_target"}
    if not required.issubset(checks):
        raise RuntimeError("Unexpected draft_items constraints; refusing unsafe alteration")

    for name in required:
        op.drop_constraint(name, "draft_items", type_="check")
    op.create_check_constraint(
        "ck_draft_items_type", "draft_items", "draft_type IN ('question','mistake')"
    )
    op.create_check_constraint(
        "ck_draft_items_source",
        "draft_items",
        "(draft_type='question' AND source_type='manual') OR "
        "(draft_type='mistake' AND source_type IN ('question','question_draft'))",
    )
    op.create_check_constraint(
        "ck_draft_items_conversion_target",
        "draft_items",
        "(status='converted' AND target_id IS NOT NULL AND "
        "((draft_type='question' AND target_type='question') OR "
        "(draft_type='mistake' AND target_type='mistake'))) OR "
        "(status<>'converted' AND target_type IS NULL AND target_id IS NULL)",
    )

    op.create_table(
        "mistake_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("draft_item_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("question_draft_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("my_answer", sa.Text(), nullable=True),
        sa.Column("correct_answer_snapshot", sa.Text(), nullable=True),
        sa.Column("explanation_snapshot", sa.Text(), nullable=True),
        sa.Column("reason_category", sa.String(20), server_default="unknown", nullable=False),
        sa.Column("mistake_reason", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["draft_item_id"], ["draft_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["question_draft_id"], ["question_drafts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "(question_id IS NOT NULL AND question_draft_id IS NULL) OR "
            "(question_id IS NULL AND question_draft_id IS NOT NULL)",
            name="ck_mistake_drafts_question_source",
        ),
        sa.CheckConstraint(
            "reason_category IN ('concept','calculation','reading','careless','unknown')",
            name="ck_mistake_drafts_reason_category",
        ),
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('easy','medium','hard')",
            name="ck_mistake_drafts_difficulty",
        ),
    )
    op.create_index("idx_mistake_drafts_subject", "mistake_drafts", ["subject_id"])

    op.create_table(
        "mistakes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_draft_item_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("my_answer", sa.Text(), nullable=True),
        sa.Column("correct_answer", sa.Text(), nullable=True),
        sa.Column("analysis", sa.Text(), nullable=True),
        sa.Column("reason_category", sa.String(20), nullable=False),
        sa.Column("mistake_reason", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("visibility", sa.String(20), server_default="private", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_draft_item_id"], ["draft_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('active','archived')", name="ck_mistakes_status"),
        sa.CheckConstraint("visibility='private'", name="ck_mistakes_visibility"),
        sa.CheckConstraint("version>0", name="ck_mistakes_version"),
    )
    op.create_index("idx_mistakes_subject_status", "mistakes", ["subject_id", "status"])

    op.create_table(
        "review_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_id", sa.String(64), nullable=False),
        sa.Column("state", sa.String(20), server_default="active", nullable=False),
        sa.Column("algorithm", sa.String(30), server_default="fixed_interval_v1", nullable=False),
        sa.Column("interval_days", sa.Integer(), server_default="0", nullable=False),
        sa.Column("repetitions", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("target_type='mistake'", name="ck_review_items_target_type"),
        sa.CheckConstraint("state IN ('active','paused')", name="ck_review_items_state"),
        sa.CheckConstraint("algorithm='fixed_interval_v1'", name="ck_review_items_algorithm"),
        sa.CheckConstraint("interval_days>=0 AND repetitions>=0", name="ck_review_items_counts"),
        sa.UniqueConstraint("target_type", "target_id", name="uq_review_items_target"),
    )
    op.create_index("idx_review_items_due", "review_items", ["state", "next_review_at"])

    op.create_table(
        "review_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("review_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("previous_interval_days", sa.Integer(), nullable=False),
        sa.Column("next_interval_days", sa.Integer(), nullable=False),
        sa.Column("previous_next_review_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["review_item_id"], ["review_items.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("rating BETWEEN 0 AND 5", name="ck_review_records_rating"),
        sa.CheckConstraint(
            "previous_interval_days>=0 AND next_interval_days>0",
            name="ck_review_records_intervals",
        ),
    )
    op.create_index(
        "idx_review_records_item_time", "review_records", ["review_item_id", "reviewed_at"]
    )


def downgrade() -> None:
    op.drop_table("review_records")
    op.drop_table("review_items")
    op.execute(
        "DELETE FROM knowledge_point_links WHERE target_type IN ('mistake','mistake_draft')"
    )
    op.drop_table("mistakes")
    op.drop_table("mistake_drafts")
    for name in ("ck_draft_items_type", "ck_draft_items_source", "ck_draft_items_conversion_target"):
        op.drop_constraint(name, "draft_items", type_="check")
    op.create_check_constraint("ck_draft_items_type", "draft_items", "draft_type='question'")
    op.create_check_constraint("ck_draft_items_source", "draft_items", "source_type='manual'")
    op.create_check_constraint(
        "ck_draft_items_conversion_target",
        "draft_items",
        "(status='converted' AND target_type='question' AND target_id IS NOT NULL) OR "
        "(status<>'converted' AND target_type IS NULL AND target_id IS NULL)",
    )
