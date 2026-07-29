import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AttemptCreate(BaseModel):
    question_id: uuid.UUID
    submitted_answer: str = Field(min_length=1)

    @field_validator("submitted_answer")
    @classmethod
    def clean_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("submitted_answer must not be blank")
        return value


class AttemptOut(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    submitted_answer: str
    is_correct: bool
    mistake_draft_item_id: uuid.UUID | None
    submitted_at: datetime

    model_config = {"from_attributes": True}
