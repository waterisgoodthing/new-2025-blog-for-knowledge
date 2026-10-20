"""add protected learning attempts and attempt-backed mistake drafts

Revision ID: 021
Revises: 020
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "021"
down_revision: str | None = "020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("submitted_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("mistake_draft_item_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(submitted_answer)) > 0", name="ck_attempts_answer_not_blank"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mistake_draft_item_id"], ["draft_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mistake_draft_item_id", name="uq_attempts_mistake_draft_item"),
    )
    op.create_index("idx_attempts_question_submitted", "attempts", ["question_id", "submitted_at"])
    op.add_column("mistake_drafts", sa.Column("attempt_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_mistake_drafts_attempt", "mistake_drafts", "attempts", ["attempt_id"], ["id"], ondelete="RESTRICT")
    op.create_unique_constraint("uq_mistake_drafts_attempt", "mistake_drafts", ["attempt_id"])
    op.drop_constraint("ck_mistake_drafts_question_source", "mistake_drafts", type_="check")
    op.create_check_constraint(
        "ck_mistake_drafts_question_source",
        "mistake_drafts",
        "((question_id IS NOT NULL AND question_draft_id IS NULL AND attempt_id IS NULL) OR "
        "(question_id IS NULL AND question_draft_id IS NOT NULL AND attempt_id IS NULL) OR "
        "(question_id IS NOT NULL AND question_draft_id IS NULL AND attempt_id IS NOT NULL))",
    )


def downgrade() -> None:
    bind = op.get_bind()
    attempts = bind.execute(sa.text("SELECT count(*) FROM attempts")).scalar_one()
    linked = bind.execute(sa.text("SELECT count(*) FROM mistake_drafts WHERE attempt_id IS NOT NULL")).scalar_one()
    if attempts or linked:
        raise RuntimeError("Refusing to downgrade while Attempt learning data exists")
    op.drop_constraint("ck_mistake_drafts_question_source", "mistake_drafts", type_="check")
    op.create_check_constraint(
        "ck_mistake_drafts_question_source",
        "mistake_drafts",
        "(question_id IS NOT NULL AND question_draft_id IS NULL) OR "
        "(question_id IS NULL AND question_draft_id IS NOT NULL)",
    )
    op.drop_constraint("uq_mistake_drafts_attempt", "mistake_drafts", type_="unique")
    op.drop_constraint("fk_mistake_drafts_attempt", "mistake_drafts", type_="foreignkey")
    op.drop_column("mistake_drafts", "attempt_id")
    op.drop_index("idx_attempts_question_submitted", table_name="attempts")
    op.drop_table("attempts")
