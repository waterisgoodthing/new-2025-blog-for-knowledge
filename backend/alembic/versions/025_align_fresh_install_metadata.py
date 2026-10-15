"""align fresh-install schema with current model metadata

Revision ID: 025
Revises: 024
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "025"
down_revision: str | None = "024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


NOT_NULL_DEFAULTS = {
    "categories": {"sort_order": "0"},
    "music_items": {
        "sort_order": "0",
        "is_active": "TRUE",
        "created_at": "now()",
    },
    "notes": {
        "hidden": "FALSE",
        "created_at": "now()",
        "updated_at": "now()",
        "ef": "2.5",
        "interval": "0",
        "repetitions": "0",
    },
    "recommendations": {"created_at": "now()"},
    "users": {"created_at": "now()"},
}


def _set_not_null(table_name: str, column_name: str, default_sql: str) -> None:
    quoted_table = f'"{table_name}"'
    quoted_column = f'"{column_name}"'
    op.execute(
        sa.text(
            f"UPDATE {quoted_table} "
            f"SET {quoted_column} = {default_sql} "
            f"WHERE {quoted_column} IS NULL"
        )
    )
    op.execute(
        sa.text(
            f"ALTER TABLE {quoted_table} "
            f"ALTER COLUMN {quoted_column} SET NOT NULL"
        )
    )


def _drop_not_null(table_name: str, column_name: str) -> None:
    op.execute(
        sa.text(
            f'ALTER TABLE "{table_name}" '
            f'ALTER COLUMN "{column_name}" DROP NOT NULL'
        )
    )


def _has_unique_constraint(table_name: str, constraint_name: str) -> bool:
    return any(
        constraint.get("name") == constraint_name
        for constraint in sa.inspect(op.get_bind()).get_unique_constraints(table_name)
    )


def upgrade() -> None:
    op.execute(
        "ALTER TABLE admin_sessions "
        "DROP CONSTRAINT IF EXISTS admin_sessions_token_hash_key"
    )
    op.execute("DROP INDEX IF EXISTS idx_admin_sessions_user_id")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_admin_sessions_token_hash "
        "ON admin_sessions (token_hash)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_admin_sessions_user_id "
        "ON admin_sessions (user_id)"
    )

    op.execute(
        "ALTER TABLE daily_songs "
        "DROP CONSTRAINT IF EXISTS daily_songs_date_key"
    )
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_daily_songs_date "
        "ON daily_songs (date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_music_candidates_netease_id "
        "ON music_candidates (netease_id)"
    )

    for table_name, columns in NOT_NULL_DEFAULTS.items():
        for column_name, default_sql in columns.items():
            _set_not_null(table_name, column_name, default_sql)


def downgrade() -> None:
    for table_name, columns in NOT_NULL_DEFAULTS.items():
        for column_name in columns:
            _drop_not_null(table_name, column_name)

    op.execute("DROP INDEX IF EXISTS ix_music_candidates_netease_id")
    op.execute("DROP INDEX IF EXISTS ix_daily_songs_date")
    if not _has_unique_constraint("daily_songs", "daily_songs_date_key"):
        op.create_unique_constraint(
            "daily_songs_date_key",
            "daily_songs",
            ["date"],
        )

    op.execute("DROP INDEX IF EXISTS ix_admin_sessions_token_hash")
    op.execute("DROP INDEX IF EXISTS ix_admin_sessions_user_id")
    if not _has_unique_constraint(
        "admin_sessions",
        "admin_sessions_token_hash_key",
    ):
        op.create_unique_constraint(
            "admin_sessions_token_hash_key",
            "admin_sessions",
            ["token_hash"],
        )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_admin_sessions_user_id "
        "ON admin_sessions (user_id)"
    )
