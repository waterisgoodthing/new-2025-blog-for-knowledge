"""add ai_call_logs

Revision ID: 016
Revises: 015
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "016"
down_revision: str | None = "015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "ai_call_logs" in inspector.get_table_names():
        raise RuntimeError("Batch 9 target table already exists: ai_call_logs")

    op.create_table(
        "ai_call_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("provider_used", sa.String(50), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("success", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("attempts", postgresql.JSON(), nullable=True),
        sa.Column("input_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_ai_call_logs_created_at", "ai_call_logs", ["created_at"])
    op.create_index("idx_ai_call_logs_task_type", "ai_call_logs", ["task_type"])
    op.create_index("idx_ai_call_logs_success", "ai_call_logs", ["success"])


def downgrade() -> None:
    op.drop_index("idx_ai_call_logs_success", table_name="ai_call_logs")
    op.drop_index("idx_ai_call_logs_task_type", table_name="ai_call_logs")
    op.drop_index("idx_ai_call_logs_created_at", table_name="ai_call_logs")
    op.drop_table("ai_call_logs")
