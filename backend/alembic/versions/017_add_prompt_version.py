"""add prompt_version to ai_call_logs

Revision ID: 017
Revises: 016
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "017"
down_revision: str | None = "016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = [c["name"] for c in inspector.get_columns("ai_call_logs")]
    if "prompt_version" not in columns:
        op.add_column(
            "ai_call_logs",
            sa.Column("prompt_version", sa.String(20), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("ai_call_logs", "prompt_version")
