from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MusicItem(Base):
    __tablename__ = "music_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str | None] = mapped_column(String(200), nullable=True)
    artwork: Mapped[str | None] = mapped_column(String(500), nullable=True)
    apple_music_url: Mapped[str] = mapped_column(String(500), nullable=False)
    preview_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    track_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
