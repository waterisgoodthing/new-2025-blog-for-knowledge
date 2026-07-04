"""add admin sessions, passkey credentials, and admin passwords

Revision ID: 006
Revises: 005
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_map(table_name: str) -> dict[str, dict]:
    return {column["name"]: column for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _require_columns(table_name: str, required: set[str]) -> None:
    missing = required - set(_column_map(table_name))
    if missing:
        raise RuntimeError(f"{table_name} is missing required columns: {sorted(missing)}")


def _has_index(table_name: str, columns: list[str], *, unique: bool | None = None) -> bool:
    inspector = sa.inspect(op.get_bind())
    target = tuple(columns)
    for index in inspector.get_indexes(table_name):
        if tuple(index.get("column_names") or ()) == target and (
            unique is None or bool(index.get("unique")) is unique
        ):
            return True
    for constraint in inspector.get_unique_constraints(table_name):
        if tuple(constraint.get("column_names") or ()) == target and unique is not False:
            return True
    return False


def _ensure_index(
    name: str,
    table_name: str,
    columns: list[str],
    *,
    unique: bool = False,
) -> None:
    if not _has_index(table_name, columns, unique=unique):
        op.create_index(name, table_name, columns, unique=unique)


def _ensure_passkey_public_key_type() -> None:
    column = _column_map("passkey_credentials")["public_key"]
    if isinstance(column["type"], sa.LargeBinary):
        return

    row_count = op.get_bind().execute(sa.text("SELECT count(*) FROM passkey_credentials")).scalar_one()
    if row_count:
        raise RuntimeError(
            "passkey_credentials.public_key is not BYTEA and contains data; "
            "manual key-format migration is required"
        )
    op.alter_column(
        "passkey_credentials",
        "public_key",
        existing_type=column["type"],
        type_=sa.LargeBinary(),
        postgresql_using="convert_to(public_key, 'UTF8')",
    )


def upgrade() -> None:
    tables = _table_names()
    if "admin_sessions" not in tables:
        op.create_table(
            "admin_sessions",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
            sa.Column("auth_level", sa.String(20), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked", sa.Boolean(), nullable=False, server_default="false"),
            sa.Column("ip", sa.String(45), nullable=True),
            sa.Column("user_agent", sa.String(500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    else:
        _require_columns(
            "admin_sessions",
            {"id", "user_id", "token_hash", "auth_level", "expires_at", "revoked", "ip", "user_agent", "created_at"},
        )
    _ensure_index("idx_admin_sessions_user_id", "admin_sessions", ["user_id"])
    _ensure_index("idx_admin_sessions_token_hash", "admin_sessions", ["token_hash"], unique=True)

    tables = _table_names()
    if "passkey_credentials" not in tables:
        op.create_table(
            "passkey_credentials",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column("credential_id", sa.String(512), unique=True, nullable=False),
            sa.Column("public_key", sa.LargeBinary(), nullable=False),
            sa.Column("sign_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("device_name", sa.String(200), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        )
    else:
        _require_columns(
            "passkey_credentials",
            {"id", "credential_id", "public_key", "sign_count", "device_name", "created_at", "last_used_at"},
        )
        _ensure_passkey_public_key_type()

    tables = _table_names()
    if "admin_passwords" not in tables:
        op.create_table(
            "admin_passwords",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("username", sa.String(100), unique=True, nullable=False),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "updated_by_session_id",
                UUID(as_uuid=True),
                sa.ForeignKey("admin_sessions.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
    else:
        _require_columns(
            "admin_passwords",
            {"id", "username", "password_hash", "updated_at", "updated_by_session_id"},
        )


def downgrade() -> None:
    op.drop_table("admin_passwords")
    op.drop_table("passkey_credentials")
    op.drop_index("idx_admin_sessions_token_hash", table_name="admin_sessions")
    op.drop_index("idx_admin_sessions_user_id", table_name="admin_sessions")
    op.drop_table("admin_sessions")
