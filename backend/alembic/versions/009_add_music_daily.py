"""add music daily song tables

Revision ID: 009
Revises: 008
Create Date: 2026-06-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON, UUID

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "netease_api_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("api_base_url", sa.String(500), nullable=False, server_default="http://localhost:3000"),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("timeout_seconds", sa.Integer(), server_default="10"),
        sa.Column("retry_count", sa.Integer(), server_default="3"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "music_source_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_value", sa.String(500), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "music_candidates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_rule_id", sa.Integer(), sa.ForeignKey("music_source_rules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("netease_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("artist", sa.String(300), nullable=True),
        sa.Column("album", sa.String(300), nullable=True),
        sa.Column("artwork_url", sa.String(1000), nullable=True),
        sa.Column("preview_url", sa.String(1000), nullable=True),
        sa.Column("netease_url", sa.String(1000), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_music_candidates_netease_id", "music_candidates", ["netease_id"])

    op.create_table(
        "daily_songs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date(), unique=True, nullable=False),
        sa.Column("timezone", sa.String(50), server_default="Asia/Shanghai"),
        sa.Column("netease_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("artist", sa.String(300), nullable=True),
        sa.Column("album", sa.String(300), nullable=True),
        sa.Column("artwork_url", sa.String(1000), nullable=True),
        sa.Column("preview_url", sa.String(1000), nullable=True),
        sa.Column("netease_url", sa.String(1000), nullable=True),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("source_rule_id", sa.Integer(), sa.ForeignKey("music_source_rules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("music_candidates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_daily_songs_date", "daily_songs", ["date"], unique=True)

    op.create_table(
        "music_sync_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_rule_id", sa.Integer(), sa.ForeignKey("music_source_rules.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("candidates_found", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_music_sync_logs_created_at", "music_sync_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_music_sync_logs_created_at", table_name="music_sync_logs")
    op.drop_table("music_sync_logs")
    op.drop_index("idx_daily_songs_date", table_name="daily_songs")
    op.drop_table("daily_songs")
    op.drop_index("idx_music_candidates_netease_id", table_name="music_candidates")
    op.drop_table("music_candidates")
    op.drop_table("music_source_rules")
    op.drop_table("netease_api_configs")
