"""add independent ai_runs business audit table

Revision ID: 018
Revises: 017
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "018"
down_revision: str | None = "017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=True),
        sa.Column("target_id", sa.String(100), nullable=True),
        sa.Column("provider_used", sa.String(50), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("prompt_version", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "validation_status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("replay_input", postgresql.JSON(), nullable=True),
        sa.Column("output_data", postgresql.JSON(), nullable=True),
        sa.Column("warnings", postgresql.JSON(), nullable=True),
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message_safe", sa.Text(), nullable=True),
        sa.Column("attempt", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "parent_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_runs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "review_status",
            sa.String(20),
            nullable=False,
            server_default="not_required",
        ),
        sa.Column("review_revision", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('running', 'succeeded', 'failed')",
            name="ck_ai_runs_status",
        ),
        sa.CheckConstraint(
            "validation_status IN ('pending', 'passed', 'failed', 'warning', 'not_applicable')",
            name="ck_ai_runs_validation_status",
        ),
        sa.CheckConstraint(
            "review_status IN ('not_required', 'pending', 'accepted', 'rejected')",
            name="ck_ai_runs_review_status",
        ),
        sa.CheckConstraint("attempt >= 1", name="ck_ai_runs_attempt"),
        sa.CheckConstraint(
            "parent_run_id IS NULL OR parent_run_id <> id",
            name="ck_ai_runs_parent_not_self",
        ),
    )
    op.create_index("idx_ai_runs_created_at", "ai_runs", ["created_at"])
    op.create_index("idx_ai_runs_task_type", "ai_runs", ["task_type"])
    op.create_index("idx_ai_runs_status", "ai_runs", ["status"])
    op.create_index("idx_ai_runs_review_status", "ai_runs", ["review_status"])
    op.create_index("idx_ai_runs_parent_run_id", "ai_runs", ["parent_run_id"])


def downgrade() -> None:
    op.drop_table("ai_runs")
