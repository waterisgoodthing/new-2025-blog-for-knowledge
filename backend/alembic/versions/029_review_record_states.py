"""Add previous_state and new_state to review_records.

Revision ID: 029
Revises: 028
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "029"
down_revision: str | None = "028"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name, schema="public"))


def _assert_upgrade_shape(inspector) -> None:
    if not _table_exists(inspector, "review_records"):
        raise RuntimeError("review_records table is missing; refusing unsafe alteration")

    checks = {check["name"] for check in inspector.get_check_constraints("review_records", schema="public")}
    required = {"ck_review_records_rating", "ck_review_records_intervals"}
    if not required.issubset(checks):
        raise RuntimeError("review_records is missing expected check constraints")

    if _column_exists(inspector, "review_records", "previous_state"):
        raise RuntimeError("review_records.previous_state already exists; expected pre-029 shape")
    if _column_exists(inspector, "review_records", "new_state"):
        raise RuntimeError("review_records.new_state already exists; expected pre-029 shape")


def _assert_downgrade_shape(inspector) -> None:
    if not _table_exists(inspector, "review_records"):
        raise RuntimeError("review_records table is missing; refusing unsafe alteration")

    checks = {check["name"] for check in inspector.get_check_constraints("review_records", schema="public")}
    if "ck_review_records_state" not in checks or "ck_review_records_new_state" not in checks:
        raise RuntimeError("review_records is missing expected state check constraints; expected 029 shape")

    if not _column_exists(inspector, "review_records", "previous_state"):
        raise RuntimeError("review_records.previous_state is missing; expected 029 shape")
    if not _column_exists(inspector, "review_records", "new_state"):
        raise RuntimeError("review_records.new_state is missing; expected 029 shape")


def upgrade() -> None:
    bind = op.get_bind()
    lock_key = 290029
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    _assert_upgrade_shape(inspector)

    op.add_column(
        "review_records",
        sa.Column("previous_state", sa.String(length=20), nullable=False, server_default="active"),
    )
    op.add_column(
        "review_records",
        sa.Column("new_state", sa.String(length=20), nullable=False, server_default="active"),
    )
    op.create_check_constraint(
        "ck_review_records_state",
        "review_records",
        "previous_state IN ('active','mastered','paused')",
    )
    op.create_check_constraint(
        "ck_review_records_new_state",
        "review_records",
        "new_state IN ('active','mastered','paused')",
    )


def downgrade() -> None:
    bind = op.get_bind()
    lock_key = 290029
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    _assert_downgrade_shape(inspector)

    # Lossy: state-transition metadata is dropped.
    op.drop_constraint("ck_review_records_state", "review_records", type_="check")
    op.drop_constraint("ck_review_records_new_state", "review_records", type_="check")
    op.drop_column("review_records", "previous_state")
    op.drop_column("review_records", "new_state")
