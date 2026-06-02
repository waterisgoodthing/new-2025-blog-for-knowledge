import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    parent_id: uuid.UUID | None = None


class FolderUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    parent_id: uuid.UUID | None = None
    sort_order: int | None = None


class FolderOut(BaseModel):
    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None = None
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime
    children: list["FolderOut"] = []
    note_count: int = 0

    model_config = {"from_attributes": True}


class FolderReorderItem(BaseModel):
    id: uuid.UUID
    sort_order: int


class FolderReorderRequest(BaseModel):
    items: list[FolderReorderItem]


class MoveNoteRequest(BaseModel):
    folder_id: uuid.UUID | None = None
