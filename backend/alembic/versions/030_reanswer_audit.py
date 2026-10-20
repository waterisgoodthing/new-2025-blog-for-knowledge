"""Re-answer audit linkage (R02/D4/D5).

- attempts.context_type VARCHAR(20) NOT NULL DEFAULT 'practice'
  with CHECK IN ('practice','review','editor_check').
- idx_attempts_context_submitted(context_type, submitted_at) for review stats.
- review_records.attempt_id UUID NULL REFERENCES attempts(id) ON DELETE RESTRICT.

Revision ID: 030
Revises: 029
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "030"
down_revision: str | None = "029"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name, schema="public"))


def _assert_upgrade_shape(inspector) -> None:
    for table in ("attempts", "review_records"):
        if not _table_exists(inspector, table):
            raise RuntimeError(f"{table} table is missing; refusing unsafe alteration")
    if _column_exists(inspector, "attempts", "context_type"):
        raise RuntimeError("attempts.context_type already exists; expected pre-030 shape")
    if _column_exists(inspector, "review_records", "attempt_id"):
        raise RuntimeError("review_records.attempt_id already exists; expected pre-030 shape")


def _assert_downgrade_shape(inspector) -> None:
    if not _column_exists(inspector, "attempts", "context_type"):
        raise RuntimeError("attempts.context_type is missing; expected 030 shape")
    checks = {check["name"] for check in inspector.get_check_constraints("attempts", schema="public")}
    if "ck_attempts_context_type" not in checks:
        raise RuntimeError("attempts is missing ck_attempts_context_type; expected 030 shape")
    if not _column_exists(inspector, "review_records", "attempt_id"):
        raise RuntimeError("review_records.attempt_id is missing; expected 030 shape")


def upgrade() -> None:
    bind = op.get_bind()
    lock_key = 300030
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    _assert_upgrade_shape(inspector)

    op.add_column(
        "attempts",
        sa.Column("context_type", sa.String(length=20), nullable=False, server_default="practice"),
    )
    op.create_check_constraint(
        "ck_attempts_context_type",
        "attempts",
        "context_type IN ('practice','review','editor_check')",
    )
    op.create_index(
        "idx_attempts_context_submitted",
        "attempts",
        ["context_type", "submitted_at"],
    )
    op.add_column("review_records", sa.Column("attempt_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_review_records_attempt",
        "review_records",
        "attempts",
        ["attempt_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    bind = op.get_bind()
    lock_key = 300030
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    _assert_downgrade_shape(inspector)

    # Lossy: re-answer audit linkage is dropped.
    op.drop_constraint("fk_review_records_attempt", "review_records", type_="foreignkey")
    op.drop_column("review_records", "attempt_id")
    op.drop_index("idx_attempts_context_submitted", table_name="attempts")
    op.drop_constraint("ck_attempts_context_type", "attempts", type_="check")
    op.drop_column("attempts", "context_type")
