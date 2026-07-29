"""add audit_logs table

Revision ID: 008
Revises: 007
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def _has_index(columns: list[str]) -> bool:
    target = tuple(columns)
    return any(
        tuple(index.get("column_names") or ()) == target
        for index in sa.inspect(op.get_bind()).get_indexes("audit_logs")
    )


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "audit_logs" not in inspector.get_table_names():
        op.create_table(
            "audit_logs",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "actor_session_id",
                UUID(as_uuid=True),
                sa.ForeignKey("admin_sessions.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("auth_level", sa.String(20), nullable=True),
            sa.Column("action", sa.String(100), nullable=False),
            sa.Column("entity_type", sa.String(50), nullable=True),
            sa.Column("entity_id", sa.String(255), nullable=True),
            sa.Column("before", JSON, nullable=True),
            sa.Column("after", JSON, nullable=True),
            sa.Column("ip", sa.String(45), nullable=True),
            sa.Column("user_agent", sa.String(500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
    else:
        required = {
            "id", "actor_session_id", "auth_level", "action", "entity_type", "entity_id",
            "before", "after", "ip", "user_agent", "created_at",
        }
        existing = {column["name"] for column in inspector.get_columns("audit_logs")}
        missing = required - existing
        if missing:
            raise RuntimeError(f"audit_logs is missing required columns: {sorted(missing)}")

    if not _has_index(["created_at"]):
        op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])
    if not _has_index(["action"]):
        op.create_index("idx_audit_logs_action", "audit_logs", ["action"])
    if not _has_index(["entity_type", "entity_id"]):
        op.create_index("idx_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])


def downgrade() -> None:
    op.drop_index("idx_audit_logs_entity", table_name="audit_logs")
    op.drop_index("idx_audit_logs_action", table_name="audit_logs")
    op.drop_index("idx_audit_logs_created_at", table_name="audit_logs")
    op.drop_table("audit_logs")
