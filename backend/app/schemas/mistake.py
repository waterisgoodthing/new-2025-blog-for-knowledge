import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator

ReasonCategory = Literal["concept", "calculation", "reading", "careless", "unknown"]
Difficulty = Literal["easy", "medium", "hard"]
MistakeVisibility = Literal["private", "public"]


class MistakeDraftCreate(BaseModel):
    question_id: uuid.UUID | None = None
    question_draft_id: uuid.UUID | None = None
    attempt_id: uuid.UUID | None = None
    my_answer: str | None = None
    reason_category: ReasonCategory = "unknown"
    mistake_reason: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] = Field(default_factory=list)
    # F05: optional provenance. When set, the succeeded creation-type AiRun is
    # bound to the newly created draft in this same transaction.
    source_run_id: uuid.UUID | None = None

    @field_validator("my_answer", "mistake_reason")
    @classmethod
    def clean(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def exactly_one_source(self):
        if self.attempt_id is not None and self.question_id is None:
            raise ValueError("attempt source requires question_id")
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


class MistakeVisibilityUpdate(BaseModel):
    version: int = Field(ge=1)
    visibility: MistakeVisibility


class MistakeDraftOut(BaseModel):
    id: uuid.UUID
    draft_item_id: uuid.UUID
    question_id: uuid.UUID | None
    question_draft_id: uuid.UUID | None
    attempt_id: uuid.UUID | None
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
    visibility: MistakeVisibility
    version: int
    knowledge_point_ids: list[int]
    review_item_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicMistakeOut(BaseModel):
    """W3-D03 public allowlist DTO. Field set is frozen; do not extend."""

    id: uuid.UUID
    title: str | None
    question_text: str
    correct_answer: str | None
    analysis: str | None
    reason_category: ReasonCategory
    mistake_reason: str | None
    difficulty: Difficulty | None
    knowledge_point_ids: list[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicMistakeListResponse(BaseModel):
    """Public list envelope matching the NoteListResponse convention."""

    items: list[PublicMistakeOut]
    total: int
    page: int
    size: int
    empty: bool = False
    message: str | None = None


# --- B05 canonical AI-assisted mistake-draft creation ---


class MistakeAiCandidateRequest(BaseModel):
    question_id: uuid.UUID
    my_answer: str | None = None
    user_error_reason: str = Field(min_length=1)

    @field_validator("my_answer", "user_error_reason")
    @classmethod
    def clean(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class MistakeAiCandidateResponse(BaseModel):
    run_id: uuid.UUID
    review_revision: int
    candidate: dict


class MistakeAiConfirmRequest(BaseModel):
    run_id: uuid.UUID
    review_revision: int = Field(ge=0)
    question_id: uuid.UUID
    my_answer: str | None = None
    user_error_reason: str | None = None
    reason_category: ReasonCategory = "unknown"
    mistake_reason: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_ids: list[int] = Field(default_factory=list)
    confirmed_candidate: dict = Field(default_factory=dict)
