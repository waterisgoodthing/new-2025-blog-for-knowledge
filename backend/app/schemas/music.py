from datetime import datetime

from pydantic import BaseModel, Field


class MusicItemOut(BaseModel):
    id: int
    title: str
    artist: str | None = None
    artwork: str | None = None
    apple_music_url: str
    preview_url: str | None = None
    track_id: int | None = None
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}


class MusicItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    artist: str | None = None
    artwork: str | None = None
    apple_music_url: str = Field(..., min_length=1, max_length=500)
    preview_url: str | None = None
    track_id: int | None = None
    sort_order: int = 0
    is_active: bool = True


class MusicItemUpdate(BaseModel):
    title: str | None = None
    artist: str | None = None
    artwork: str | None = None
    apple_music_url: str | None = None
    preview_url: str | None = None
    track_id: int | None = None
    sort_order: int | None = None
    is_active: bool | None = None
