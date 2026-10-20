"""Trusted provenance for canonical AI creation (B05a/B05b).

Adds server-injected provenance to ``ai_runs`` so a canonical AI-assisted
creation (for example a mistake draft confirmed from an AI error-interpretation
candidate) can be traced and replayed safely:

  * ``created_by``              the admin who requested the run (server-injected
                                actor; never client-selectable);
  * ``creation_context``        server-built, immutable JSON object describing
                                the purpose, source question id/version, the
                                normalized input hash, output schema and prompt
                                version;
  * ``confirmed_payload_hash``  sha256 of the confirmed entity payload, used for
                                idempotent replay detection;
  * ``confirmed_at``            when the run was confirmed into an entity.

Historical runs keep these columns NULL and remain readable; they are simply
not eligible for canonical confirmation.

``downgrade()`` is safe: the columns are provenance-only and contain no
authoritative business state, so dropping them reverts to the pre-034 shape.

Revision ID: 034
Revises: 033
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql


revision: str = "034"
down_revision: str | None = "033"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE = "ai_runs"
LOCK_KEY = 340034


def _assert_prerequisites(bind) -> None:
    if TABLE not in inspect(bind).get_table_names(schema="public"):
        raise RuntimeError(f"{TABLE} is missing; refusing unsafe alteration")
    if "users" not in inspect(bind).get_table_names(schema="public"):
        raise RuntimeError("users table is missing; refusing unsafe alteration")


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": LOCK_KEY})
    _assert_prerequisites(bind)

    existing = {column["name"] for column in inspect(bind).get_columns(TABLE)}
    if "creation_context" in existing:
        return

    op.add_column(
        TABLE,
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        TABLE,
        sa.Column("creation_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        TABLE,
        sa.Column("confirmed_payload_hash", sa.String(length=64), nullable=True),
    )
    op.add_column(
        TABLE,
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_ai_runs_created_by",
        TABLE,
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": LOCK_KEY})
    _assert_prerequisites(bind)

    existing = {column["name"] for column in inspect(bind).get_columns(TABLE)}
    if "creation_context" not in existing:
        return

    op.drop_constraint("fk_ai_runs_created_by", TABLE, type_="foreignkey")
    op.drop_column(TABLE, "confirmed_at")
    op.drop_column(TABLE, "confirmed_payload_hash")
    op.drop_column(TABLE, "creation_context")
    op.drop_column(TABLE, "created_by")
