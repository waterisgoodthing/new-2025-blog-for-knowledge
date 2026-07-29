import uuid
from datetime import datetime, date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MusicSourceRule(Base):
    __tablename__ = "music_source_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_value: Mapped[str] = mapped_column(String(500), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MusicCandidate(Base):
    __tablename__ = "music_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("music_source_rules.id", ondelete="SET NULL"), nullable=True
    )
    netease_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(300), nullable=True)
    album: Mapped[str | None] = mapped_column(String(300), nullable=True)
    artwork_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    netease_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_music_candidates_netease_id", "netease_id"),
    )


class DailySong(Base):
    __tablename__ = "daily_songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Shanghai")
    netease_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(300), nullable=True)
    album: Mapped[str | None] = mapped_column(String(300), nullable=True)
    artwork_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    netease_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    recommendation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("music_source_rules.id", ondelete="SET NULL"), nullable=True
    )
    candidate_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("music_candidates.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MusicSyncLog(Base):
    __tablename__ = "music_sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("music_source_rules.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    candidates_found: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_music_sync_logs_created_at", "created_at"),
    )


class NetEaseApiConfig(Base):
    __tablename__ = "netease_api_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_base_url: Mapped[str] = mapped_column(String(500), nullable=False, default="http://localhost:3000")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=10)
    retry_count: Mapped[int] = mapped_column(Integer, default=3)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
