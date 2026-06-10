from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GuestMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    nickname: Optional[str] = Field(None, max_length=100)
    attachment_type: Optional[str] = Field(None, pattern="^(home|blog|note|mistake)$")
    attachment_slug: Optional[str] = Field(None, max_length=255)


class GuestMessageOut(BaseModel):
    id: str
    content: str
    nickname: Optional[str] = None
    attachment_type: Optional[str] = None
    attachment_slug: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class GuestMessageListResponse(BaseModel):
    items: list[GuestMessageOut]
    total: int
    page: int
    size: int


class GuestMessageModerate(BaseModel):
    status: str = Field(..., pattern="^(visible|hidden|deleted)$")
