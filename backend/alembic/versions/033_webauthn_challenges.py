"""WebAuthn challenge persistence table (W4-D03 / PR-15).

Replaces the three process-global in-memory challenge stores
(``_reg_challenge_store``, ``_auth_challenge_store``,
``_operator_reg_challenge_store``) with a durable, per-ceremony challenge
lifecycle:

  * ``id``              UUID PK (``gen_random_uuid()``)
  * ``challenge``       b64url raw challenge (W4-E08 approved deviation from the
                        plan's hash-only schema: the WebAuthn verifier needs the
                        exact raw server-side bytes; the raw value is never logged)
  * ``challenge_hash``  sha256 hex of the raw challenge bytes
  * ``purpose``         CHECK in ('registration','authentication',
                        'operator_registration')
  * ``session_id``      operator_registration binding (nullable)
  * ``user_id``         user-scoped binding, FK -> users.id ON DELETE CASCADE
  * ``created_at`` / ``expires_at`` / ``consumed_at`` lifecycle timestamps

Partial indexes cover the query patterns: (purpose, session_id) and
(purpose, user_id) for bound lookups, (expires_at) for unexpired scans, plus
(challenge_hash) for hash verification.

``downgrade()`` is FAIL-CLOSED: it refuses while any challenge is still live
(``consumed_at IS NULL AND expires_at > now()``); only consumed or expired rows
may be dropped.

Revision ID: 033
Revises: 032
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql


revision: str = "033"
down_revision: str | None = "032"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLE = "webauthn_challenges"
IDX_PURPOSE_SESSION = "idx_webauthn_challenges_purpose_session"
IDX_PURPOSE_USER = "idx_webauthn_challenges_purpose_user"
IDX_EXPIRES = "idx_webauthn_challenges_expires"
IDX_HASH = "idx_webauthn_challenges_challenge_hash"
LOCK_KEY = 330033

PURPOSE_CHECK = "purpose IN ('registration','authentication','operator_registration')"


def _table_exists(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names(schema="public")


def _assert_prerequisites(bind) -> None:
    inspector = inspect(bind)
    if not _table_exists(inspector, "users"):
        raise RuntimeError("users table is missing; refusing unsafe alteration")


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": LOCK_KEY})

    _assert_prerequisites(bind)
    inspector = inspect(bind)
    if _table_exists(inspector, TABLE):
        raise RuntimeError(f"{TABLE} already exists; expected pre-033 shape")

    op.create_table(
        TABLE,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("challenge", sa.String(length=128), nullable=False),
        sa.Column("challenge_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_webauthn_challenges_user_id",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(PURPOSE_CHECK, name="ck_webauthn_challenges_purpose"),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        IDX_PURPOSE_SESSION,
        TABLE,
        ["purpose", "session_id"],
        unique=False,
        schema="public",
        postgresql_where=sa.text("session_id IS NOT NULL"),
    )
    op.create_index(
        IDX_PURPOSE_USER,
        TABLE,
        ["purpose", "user_id"],
        unique=False,
        schema="public",
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        IDX_EXPIRES,
        TABLE,
        ["expires_at"],
        unique=False,
        schema="public",
        postgresql_where=sa.text("consumed_at IS NULL"),
    )
    op.create_index(
        IDX_HASH,
        TABLE,
        ["challenge_hash"],
        unique=False,
        schema="public",
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": LOCK_KEY})

    inspector = inspect(bind)
    if not _table_exists(inspector, TABLE):
        raise RuntimeError(f"{TABLE} is missing; expected 033 shape")

    live = bind.execute(
        text(
            f"SELECT count(*) FROM public.{TABLE} "
            "WHERE consumed_at IS NULL AND expires_at > now()"
        )
    ).scalar_one()
    if live:
        raise RuntimeError(
            f"{live} live (unconsumed, unexpired) webauthn challenge(s) exist; "
            "refusing fail-closed downgrade"
        )

    op.drop_index(IDX_HASH, table_name=TABLE, schema="public")
    op.drop_index(IDX_EXPIRES, table_name=TABLE, schema="public")
    op.drop_index(IDX_PURPOSE_USER, table_name=TABLE, schema="public")
    op.drop_index(IDX_PURPOSE_SESSION, table_name=TABLE, schema="public")
    op.drop_table(TABLE, schema="public")
