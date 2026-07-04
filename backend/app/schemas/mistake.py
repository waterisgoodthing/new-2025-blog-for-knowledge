import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

ReasonCategory = Literal["concept", "calculation", "reading", "careless", "unknown"]
Difficulty = Literal["easy", "medium", "hard"]


class MistakeDraftCreate(BaseModel):
    question_id: uuid.UUID | None = None
    question_draft_id: uuid.UUID | None = None
    my_answer: str | None = None
    reason_category: ReasonCategory = "unknown"
    mistake_reason: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] = Field(default_factory=list)

    @field_validator("my_answer", "mistake_reason")
    @classmethod
    def clean(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def exactly_one_source(self):
        if (self.question_id is None) == (self.question_draft_id is None):
            raise ValueError("exactly one question source is required")
        return self


class MistakeDraftUpdate(BaseModel):
    version: int = Field(ge=1)
    my_answer: str | None = None
    reason_category: ReasonCategory | None = None
    mistake_reason: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] | None = None


class VersionCommand(BaseModel):
    version: int = Field(ge=1)


class MistakeUpdate(BaseModel):
    version: int = Field(ge=1)
    my_answer: str | None = None
    analysis: str | None = None
    reason_category: ReasonCategory | None = None
    mistake_reason: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] | None = None


class MistakeDraftOut(BaseModel):
    id: uuid.UUID
    draft_item_id: uuid.UUID
    question_id: uuid.UUID | None
    question_draft_id: uuid.UUID | None
    subject_id: int
    title: str | None
    question_text: str
    my_answer: str | None
    correct_answer_snapshot: str | None
    explanation_snapshot: str | None
    reason_category: ReasonCategory
    mistake_reason: str | None
    difficulty: Difficulty | None
    knowledge_point_ids: list[int]
    status: str
    version: int
    target_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MistakeOut(BaseModel):
    id: uuid.UUID
    source_draft_item_id: uuid.UUID
    question_id: uuid.UUID
    subject_id: int
    title: str | None
    question_text: str
    my_answer: str | None
    correct_answer: str | None
    analysis: str | None
    reason_category: ReasonCategory
    mistake_reason: str | None
    difficulty: Difficulty | None
    status: Literal["active", "archived"]
    visibility: Literal["private"]
    version: int
    knowledge_point_ids: list[int]
    review_item_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
