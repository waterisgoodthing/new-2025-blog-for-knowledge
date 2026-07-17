import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


StorageProvider = Literal["local"]
AttachmentVisibility = Literal["private"]
AttachmentStatus = Literal["active", "missing", "deleted"]
AttachmentTargetType = Literal["question_draft", "question", "mistake"]
AttachmentPurpose = Literal["source", "question", "answer", "inline", "ai_input", "ai_output"]
AttachmentCreatePurpose = Literal["source", "question", "answer", "inline"]

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "application/pdf",
    "text/plain",
}


def _clean_name(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("original_name must not be blank")
    if (
        "/" in cleaned
        or "\\" in cleaned
        or cleaned in {".", ".."}
        or any(ord(char) < 32 or ord(char) == 127 for char in cleaned)
    ):
        raise ValueError("original_name must be a file name, not a path")
    return cleaned


class AttachmentUploadCreate(BaseModel):
    original_name: str = Field(max_length=255)
    mime_type: str = Field(max_length=120)
    size_bytes: int = Field(ge=0)
    checksum_sha256: str = Field(min_length=64, max_length=64)
    storage_provider: StorageProvider = "local"
    visibility: AttachmentVisibility = "private"

    @field_validator("original_name")
    @classmethod
    def clean_original_name(cls, value: str) -> str:
        return _clean_name(value)

    @field_validator("mime_type")
    @classmethod
    def validate_mime_type(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in ALLOWED_MIME_TYPES:
            raise ValueError("unsupported mime_type")
        return cleaned

    @field_validator("checksum_sha256")
    @classmethod
    def validate_checksum(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if any(char not in "0123456789abcdef" for char in cleaned):
            raise ValueError("checksum_sha256 must be lowercase hex")
        return cleaned


class AttachmentOut(BaseModel):
    id: uuid.UUID
    original_name: str
    storage_provider: StorageProvider
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    visibility: AttachmentVisibility
    status: AttachmentStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class AttachmentLinkCreate(BaseModel):
    attachment_id: uuid.UUID
    target_type: AttachmentTargetType
    target_id: uuid.UUID
    purpose: AttachmentCreatePurpose
    sort_order: int = 0


class AttachmentLinkOut(BaseModel):
    id: uuid.UUID
    attachment_id: uuid.UUID
    target_type: AttachmentTargetType
    target_id: str
    purpose: AttachmentPurpose
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}
