"""Widen ck_mistakes_visibility to allow 'public' (W3-D03 / PR-09).

Only the mistakes visibility CHECK is replaced. The sibling private-only
constraints ck_questions_visibility and ck_attachments_visibility are left
untouched.

downgrade is fail-closed: restoring ``visibility = 'private'`` is refused while
any row carries ``visibility = 'public'``.

Revision ID: 031
Revises: 030
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = "031"
down_revision: str | None = "030"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_OLD_CHECK = "visibility = 'private'"
_NEW_CHECK = "visibility IN ('private','public')"


def _check_constraints(bind, table_name: str) -> dict[str, str]:
    inspector = inspect(bind)
    result: dict[str, str] = {}
    for check in inspector.get_check_constraints(table_name, schema="public"):
        name = check.get("name")
        if name:
            result[name] = (check.get("sqltext") or "").strip()
    return result


def _normalize(sqltext: str) -> str:
    return " ".join(sqltext.lower().split())


def _public_row_count(bind) -> int:
    row = bind.execute(
        text("SELECT count(*) FROM public.mistakes WHERE visibility = 'public'")
    ).scalar()
    return int(row or 0)


def upgrade() -> None:
    bind = op.get_bind()
    lock_key = 300031
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    if "mistakes" not in inspector.get_table_names(schema="public"):
        raise RuntimeError("mistakes table is missing; refusing unsafe alteration")

    checks = _check_constraints(bind, "mistakes")
    if "ck_mistakes_visibility" not in checks:
        raise RuntimeError("ck_mistakes_visibility is missing; expected pre-031 shape")
    existing = _normalize(checks["ck_mistakes_visibility"])
    if _normalize(_NEW_CHECK) in existing and _normalize(_OLD_CHECK) not in existing:
        raise RuntimeError("ck_mistakes_visibility already widened; expected pre-031 shape")

    op.drop_constraint("ck_mistakes_visibility", "mistakes", type_="check")
    op.create_check_constraint(
        "ck_mistakes_visibility",
        "mistakes",
        _NEW_CHECK,
    )


def downgrade() -> None:
    bind = op.get_bind()
    lock_key = 300031
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})

    inspector = inspect(bind)
    if "mistakes" not in inspector.get_table_names(schema="public"):
        raise RuntimeError("mistakes table is missing; refusing unsafe alteration")

    checks = _check_constraints(bind, "mistakes")
    if "ck_mistakes_visibility" not in checks:
        raise RuntimeError("ck_mistakes_visibility is missing; expected 031 shape")

    public_rows = _public_row_count(bind)
    if public_rows > 0:
        raise RuntimeError(
            "downgrade fail-closed: "
            f"{public_rows} mistake row(s) have visibility='public'; "
            "re-narrowing ck_mistakes_visibility to private-only would violate data. "
            "Re-point those rows to 'private' before downgrading."
        )

    op.drop_constraint("ck_mistakes_visibility", "mistakes", type_="check")
    op.create_check_constraint(
        "ck_mistakes_visibility",
        "mistakes",
        _OLD_CHECK,
    )
