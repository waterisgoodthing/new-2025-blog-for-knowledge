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


def upgrade() -> None:
    op.create_table(
        "admin_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("auth_level", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), server_default="false"),
        sa.Column("ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_admin_sessions_user_id", "admin_sessions", ["user_id"])
    op.create_index("idx_admin_sessions_token_hash", "admin_sessions", ["token_hash"], unique=True)

    op.create_table(
        "passkey_credentials",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("credential_id", sa.String(512), unique=True, nullable=False),
        sa.Column("public_key", sa.String(1024), nullable=False),
        sa.Column("sign_count", sa.Integer(), server_default="0"),
        sa.Column("device_name", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "admin_passwords",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_by_session_id", UUID(as_uuid=True), sa.ForeignKey("admin_sessions.id", ondelete="SET NULL"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("admin_passwords")
    op.drop_table("passkey_credentials")
    op.drop_index("idx_admin_sessions_token_hash", table_name="admin_sessions")
    op.drop_index("idx_admin_sessions_user_id", table_name="admin_sessions")
    op.drop_table("admin_sessions")
