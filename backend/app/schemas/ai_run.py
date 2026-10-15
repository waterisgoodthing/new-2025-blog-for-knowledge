import re
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


_SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "session_token",
    "storage_key",
    "secret",
    "token",
}
_PATH_KEYS = {"path", "absolute_path", "file_path"}
_WINDOWS_ABSOLUTE_PATH = re.compile(r"^[A-Za-z]:[\\/]")


def sanitize_run_output(value: Any) -> Any:
    """Recursively remove credentials, storage keys, data URLs, and absolute paths."""

    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            normalized = str(key).casefold()
            if normalized in _SENSITIVE_KEYS:
                continue
            if (
                normalized in _PATH_KEYS
                and isinstance(item, str)
                and (item.startswith("/") or _WINDOWS_ABSOLUTE_PATH.match(item))
            ):
                continue
            cleaned[key] = sanitize_run_output(item)
        return cleaned
    if isinstance(value, list):
        return [sanitize_run_output(item) for item in value]
    if isinstance(value, str) and value.startswith("data:"):
        return "[redacted-data-url]"
    return value


class AiRunListItem(BaseModel):
    id: uuid.UUID
    task_type: str
    target_type: str | None = None
    target_id: str | None = None
    provider_used: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    status: Literal["running", "succeeded", "failed"]
    validation_status: Literal[
        "pending", "passed", "failed", "warning", "not_applicable"
    ]
    review_status: Literal["not_required", "pending", "accepted", "rejected"]
    review_revision: int
    attempt: int
    parent_run_id: uuid.UUID | None = None
    latency_ms: int | None = None
    error_code: str | None = None
    error_message_safe: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AiRunListResponse(BaseModel):
    items: list[AiRunListItem]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class AiRunDetail(AiRunListItem):
    output_data: dict | list | str | None = None
    warnings: list | None = None
    reviewed_at: datetime | None = None
    review_note: str | None = None

    @field_validator("output_data", mode="before")
    @classmethod
    def sanitize_output_data(cls, value: Any) -> Any:
        return sanitize_run_output(value)


class AiRunDecisionRequest(BaseModel):
    decision: Literal["accepted", "rejected"]
    expected_revision: int = Field(ge=0)
    note: str | None = Field(default=None, max_length=1000)


class AiRunRetryRequest(BaseModel):
    expected_revision: int | None = Field(default=None, ge=0)
