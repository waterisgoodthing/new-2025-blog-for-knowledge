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
Difficulty = Literal["unspecified", "easy", "medium", "hard"]
DraftStatus = Literal["pending", "needs_fix", "rejected", "converted"]
QuestionStatus = Literal["active", "archived"]

CHOICE_TYPES = {"single_choice", "multiple_choice"}


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class QuestionOption(BaseModel):
    key: str = Field(min_length=1, max_length=30)
    text: str = Field(min_length=1)

    @field_validator("key", "text")
    @classmethod
    def clean_value(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question option values must not be blank")
        return cleaned


class QuestionCreate(BaseModel):
    subject_id: int
    title: str | None = Field(default=None, max_length=300)
    stem_md: str
    question_type: QuestionType
    options: list[QuestionOption] = Field(default_factory=list)
    answer_data: dict = Field(default_factory=dict)
    analysis_md: str | None = None
    difficulty: Difficulty = "unspecified"
    knowledge_point_links: list["QuestionKnowledgePointLink"] = Field(default_factory=list)
    sources: list["QuestionSourceCreate"] = Field(default_factory=list)

    @field_validator("stem_md")
    @classmethod
    def clean_stem(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("stem_md must not be blank")
        return cleaned

    @field_validator("title", "analysis_md")
    @classmethod
    def clean_optional_markdown(cls, value: str | None) -> str | None:
        return _clean_optional(value)

    @model_validator(mode="after")
    def validate_answer_contract(self):
        option_keys = [option.key for option in self.options]
        if len(option_keys) != len(set(option_keys)):
            raise ValueError("options keys must be unique")
        if self.question_type in CHOICE_TYPES and len(self.options) < 2:
            raise ValueError("choice questions require at least two options")
        if self.question_type == "true_false" and self.options:
            raise ValueError("true_false questions must not contain options")
        if self.question_type not in CHOICE_TYPES and self.question_type != "true_false" and self.options:
            raise ValueError("non-choice questions must not contain options")
        kind = self.answer_data.get("kind")
        if kind != self.question_type:
            raise ValueError("answer_data.kind must match question_type")
        value = self.answer_data.get("value")
        if self.question_type == "single_choice":
            if not isinstance(value, list) or len(value) != 1 or value[0] not in option_keys:
                raise ValueError("single_choice answer must contain one valid option key")
        elif self.question_type == "multiple_choice":
            if not isinstance(value, list) or not value or any(item not in option_keys for item in value):
                raise ValueError("multiple_choice answer must contain valid option keys")
        elif self.question_type == "true_false":
            if not isinstance(value, bool):
                raise ValueError("true_false answer must be boolean")
        elif self.question_type == "short_answer":
            if not isinstance(value, str) or not value.strip():
                raise ValueError("short_answer answer must contain text")
        elif self.question_type == "essay":
            if not isinstance(value, str) or not value.strip():
                raise ValueError("essay answer must contain text")
        return self


class QuestionPatch(BaseModel):
    version: int = Field(ge=1)
    subject_id: int | None = None
    title: str | None = Field(default=None, max_length=300)
    stem_md: str | None = None
    question_type: QuestionType | None = None
    options: list[QuestionOption] | None = None
    answer_data: dict | None = None
    analysis_md: str | None = None
    difficulty: Difficulty | None = None
    knowledge_point_links: list["QuestionKnowledgePointLink"] | None = None
    sources: list["QuestionSourceCreate"] | None = None

    @field_validator("stem_md")
    @classmethod
    def clean_patch_stem(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("stem_md must not be blank")
        return cleaned


class QuestionKnowledgePointLink(BaseModel):
    knowledge_point_id: int
    role: Literal["primary", "secondary", "prerequisite"] = "primary"
    sort_order: int = Field(default=0, ge=0)


class QuestionSourceCreate(BaseModel):
    source_type: Literal["manual", "book", "exam", "note", "url", "other"] = "manual"
    source_title: str | None = Field(default=None, max_length=300)
    source_ref: str | None = Field(default=None, max_length=500)
    source_url: str | None = None
    source_note: str | None = None

    @model_validator(mode="after")
    def validate_url_source(self):
        if self.source_type == "url" and not self.source_url:
            raise ValueError("url sources require source_url")
        return self


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
    source_title: str | None
    source_ref: str | None
    source_url: str | None
    source_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: uuid.UUID
    subject_id: int
    title: str | None
    stem_md: str
    question_text: str
    question_type: QuestionType
    options: list[QuestionOption]
    answer_data: dict
    correct_answer: str | None
    analysis_md: str | None
    explanation: str | None
    difficulty: Difficulty
    status: QuestionStatus
    visibility: Literal["private"]
    version: int
    knowledge_point_ids: list[int]
    sources: list[QuestionSourceOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


QuestionCreate.model_rebuild()
QuestionPatch.model_rebuild()
