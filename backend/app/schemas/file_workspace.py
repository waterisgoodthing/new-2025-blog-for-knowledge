import uuid

from pydantic import BaseModel, Field


class FileRenameRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=255)


class FileMoveRequest(BaseModel):
    folder_id: uuid.UUID | None = None
