"""Widen review_items state/algorithm enumerations and add last_rating.

Revision ID: 028
Revises: 027
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "028"
down_revision: str | None = "027"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _get_check_sql(inspector, table_name: str, constraint_name: str) -> str:
    for check in inspector.get_check_constraints(table_name, schema="public"):
        if check["name"] == constraint_name:
            return check["sqltext"] or ""
    return ""


def _normalise_sql(sql: str | None) -> str:
    if sql is None:
        return ""
    return " ".join(sql.lower().split())


def _assert_v1_shape(inspector) -> None:
    if not _table_exists(inspector, "review_items"):
        raise RuntimeError("review_items table is missing; refusing unsafe alteration")

    checks = {check["name"] for check in inspector.get_check_constraints("review_items", schema="public")}
    required = {"ck_review_items_state", "ck_review_items_algorithm"}
    if not required.issubset(checks):
        raise RuntimeError("review_items is missing expected v1 check constraints")

    state_sql = _normalise_sql(_get_check_sql(inspector, "review_items", "ck_review_items_state"))
    if "mastered" in state_sql:
        raise RuntimeError("review_items state check already allows mastered; expected v1 shape")
    if "active" not in state_sql or "paused" not in state_sql:
        raise RuntimeError("review_items state check does not match expected v1 values")

    algo_sql = _normalise_sql(_get_check_sql(inspector, "review_items", "ck_review_items_algorithm"))
    if "fixed_interval_v2" in algo_sql:
        raise RuntimeError("review_items algorithm check already allows v2; expected v1 shape")
    if "fixed_interval_v1" not in algo_sql:
        raise RuntimeError("review_items algorithm check does not match expected v1 value")


def _assert_v2_shape(inspector) -> None:
    if not _table_exists(inspector, "review_items"):
        raise RuntimeError("review_items table is missing; refusing unsafe alteration")

    checks = {check["name"] for check in inspector.get_check_constraints("review_items", schema="public")}
    required = {"ck_review_items_state", "ck_review_items_algorithm"}
    if not required.issubset(checks):
        raise RuntimeError("review_items is missing expected v2 check constraints")

    state_sql = _normalise_sql(_get_check_sql(inspector, "review_items", "ck_review_items_state"))
    if "mastered" not in state_sql:
        raise RuntimeError("review_items state check does not allow mastered; expected v2 shape")

    algo_sql = _normalise_sql(_get_check_sql(inspector, "review_items", "ck_review_items_algorithm"))
    if "fixed_interval_v2" not in algo_sql:
        raise RuntimeError("review_items algorithm check does not allow v2; expected v2 shape")


def _column_exists(inspector, table_name: str, column_name: str) -> bool:
    return any(col["name"] == column_name for col in inspector.get_columns(table_name, schema="public"))


def upgrade() -> None:
    bind = op.get_bind()
    lock_key = 280028
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    _assert_v1_shape(inspector)

    # Widen state check.
    op.drop_constraint("ck_review_items_state", "review_items", type_="check")
    op.create_check_constraint(
        "ck_review_items_state",
        "review_items",
        "state IN ('active','mastered','paused')",
    )

    # Add last_rating before widening algorithm so existing rows can carry NULL.
    if not _column_exists(inspector, "review_items", "last_rating"):
        op.add_column(
            "review_items",
            sa.Column("last_rating", sa.SmallInteger(), nullable=True),
        )

    # Widen algorithm check and switch every row + default to v2.
    op.drop_constraint("ck_review_items_algorithm", "review_items", type_="check")
    op.create_check_constraint(
        "ck_review_items_algorithm",
        "review_items",
        "algorithm IN ('fixed_interval_v1','fixed_interval_v2')",
    )
    op.execute("UPDATE review_items SET algorithm = 'fixed_interval_v2'")
    op.execute("ALTER TABLE review_items ALTER COLUMN algorithm SET DEFAULT 'fixed_interval_v2'")


def downgrade() -> None:
    bind = op.get_bind()
    lock_key = 280028
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    _assert_v2_shape(inspector)

    # Lossy: mastered collapses to active; all rows revert to v1 algorithm.
    op.execute("UPDATE review_items SET state = 'active' WHERE state = 'mastered'")
    op.execute("UPDATE review_items SET algorithm = 'fixed_interval_v1'")
    op.execute("ALTER TABLE review_items ALTER COLUMN algorithm SET DEFAULT 'fixed_interval_v1'")

    # Restore v1 state check.
    op.drop_constraint("ck_review_items_state", "review_items", type_="check")
    op.create_check_constraint(
        "ck_review_items_state",
        "review_items",
        "state IN ('active','paused')",
    )

    # Restore v1 algorithm check.
    op.drop_constraint("ck_review_items_algorithm", "review_items", type_="check")
    op.create_check_constraint(
        "ck_review_items_algorithm",
        "review_items",
        "algorithm = 'fixed_interval_v1'",
    )

    # Drop last_rating (lossy).
    if _column_exists(inspector, "review_items", "last_rating"):
        op.drop_column("review_items", "last_rating")
