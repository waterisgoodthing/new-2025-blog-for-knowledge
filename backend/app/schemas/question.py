import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

QuestionType = Literal[
    "single_choice",
    "multiple_choice",
    "true_false",
    "short_answer",
    "essay",
]
Difficulty = Literal["easy", "medium", "hard"]
DraftStatus = Literal["pending", "needs_fix", "rejected", "converted"]
QuestionStatus = Literal["active", "archived"]

CHOICE_TYPES = {"single_choice", "multiple_choice"}


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class QuestionDraftCreate(BaseModel):
    subject_id: int
    title: str | None = Field(default=None, max_length=300)
    question_text: str
    question_type: QuestionType
    options: list[str] = Field(default_factory=list)
    correct_answer: str | None = None
    explanation: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] = Field(default_factory=list)

    @field_validator("question_text")
    @classmethod
    def clean_question_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question_text must not be blank")
        return cleaned

    @field_validator("title", "correct_answer", "explanation")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return _clean_optional(value)

    @field_validator("options")
    @classmethod
    def clean_options(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError("options must not contain blank values")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("options must be unique")
        return cleaned

    @field_validator("knowledge_point_ids")
    @classmethod
    def unique_knowledge_points(cls, value: list[int]) -> list[int]:
        if len(set(value)) != len(value):
            raise ValueError("knowledge_point_ids must be unique")
        return value

    @model_validator(mode="after")
    def validate_options_contract(self):
        if self.question_type in CHOICE_TYPES and len(self.options) < 2:
            raise ValueError("choice questions require at least two options")
        if self.question_type not in CHOICE_TYPES and self.options:
            raise ValueError("non-choice questions must not contain options")
        return self


class QuestionDraftUpdate(BaseModel):
    version: int = Field(ge=1)
    subject_id: int | None = None
    title: str | None = Field(default=None, max_length=300)
    question_text: str | None = None
    question_type: QuestionType | None = None
    options: list[str] | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] | None = None

    @field_validator("question_text")
    @classmethod
    def clean_question_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question_text must not be blank")
        return cleaned

    @field_validator("title", "correct_answer", "explanation")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return _clean_optional(value)

    @field_validator("options")
    @classmethod
    def clean_options(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError("options must not contain blank values")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("options must be unique")
        return cleaned

    @field_validator("knowledge_point_ids")
    @classmethod
    def unique_knowledge_points(cls, value: list[int] | None) -> list[int] | None:
        if value is not None and len(set(value)) != len(value):
            raise ValueError("knowledge_point_ids must be unique")
        return value


class VersionCommand(BaseModel):
    version: int = Field(ge=1)


class DraftItemOut(BaseModel):
    id: uuid.UUID
    draft_type: str
    source_type: str
    source_id: str | None
    status: DraftStatus
    version: int
    validation_errors: list[dict]
    target_type: str | None
    target_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionDraftOut(BaseModel):
    id: uuid.UUID
    draft_item_id: uuid.UUID
    subject_id: int
    title: str | None
    question_text: str
    question_type: QuestionType
    options: list[str]
    correct_answer: str | None
    explanation: str | None
    difficulty: Difficulty | None
    knowledge_point_ids: list[int]
    item: DraftItemOut
    created_at: datetime
    updated_at: datetime


class QuestionUpdate(BaseModel):
    version: int = Field(ge=1)
    subject_id: int | None = None
    title: str | None = Field(default=None, max_length=300)
    question_text: str | None = None
    question_type: QuestionType | None = None
    options: list[str] | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] | None = None


class QuestionSourceOut(BaseModel):
    id: uuid.UUID
    source_type: str
    source_name: str | None
    source_ref: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: uuid.UUID
    subject_id: int
    title: str | None
    question_text: str
    question_type: QuestionType
    options: list[str]
    correct_answer: str | None
    explanation: str | None
    difficulty: Difficulty | None
    status: QuestionStatus
    visibility: Literal["private"]
    version: int
    knowledge_point_ids: list[int]
    sources: list[QuestionSourceOut]
    created_at: datetime
    updated_at: datetime
