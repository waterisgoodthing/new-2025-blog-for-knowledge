import uuid
from datetime import datetime
from typing import Literal

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
    context_type: Literal["practice", "review", "editor_check"]
    mistake_draft_item_id: uuid.UUID | None
    submitted_at: datetime

    model_config = {"from_attributes": True}


class EvaluationOut(BaseModel):
    verdict: Literal["correct", "incorrect", "needs_human"]
    recommendation: int | None = Field(default=None, ge=0, le=5)


class ReanswerCreate(BaseModel):
    question_id: uuid.UUID
    submitted_answer: str = Field(min_length=1)

    @field_validator("submitted_answer")
    @classmethod
    def clean_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("submitted_answer must not be blank")
        return value


class ReanswerOut(BaseModel):
    attempt: AttemptOut
    evaluation: EvaluationOut
