import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


CaptureStatus = Literal[
    "uploaded",
    "recognizing",
    "recognized",
    "drafting",
    "ready",
    "failed",
    "converted",
    "archived",
]
CaptureLastStage = Literal["recognize", "draft", "convert"]


class KnowledgePointSuggestion(BaseModel):
    id: int | None = None
    label: str
    confidence: float | None = None


class CaptureCreate(BaseModel):
    """用已上传 attachment id 创建 capture_item。"""

    attachment_id: uuid.UUID


class CapturePatch(BaseModel):
    """人工编辑 capture 草稿字段。"""

    recognized_text: str | None = None
    user_error_context: str | None = None
    question_draft_text: str | None = None
    analysis_draft_text: str | None = None
    error_summary_draft: str | None = None
    subject_id: int | None = None
    knowledge_point_suggestions: list[KnowledgePointSuggestion] | None = None

    @field_validator("recognized_text", "user_error_context", "question_draft_text",
                     "analysis_draft_text", "error_summary_draft")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class CaptureConvert(BaseModel):
    """显式转换 capture → mistake_draft。

    需要管理员确认 subject_id 和知识点（与既有 mistake draft 创建对齐）。
    """

    subject_id: int
    question_text: str = Field(min_length=1)
    question_type: Literal[
        "single_choice", "multiple_choice", "true_false", "short_answer", "essay"
    ] = "short_answer"
    options: list[str] = Field(default_factory=list)
    correct_answer: str | None = None
    explanation: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    my_answer: str | None = None
    reason_category: Literal[
        "concept", "calculation", "reading", "careless", "unknown"
    ] = "unknown"
    mistake_reason: str | None = None
    knowledge_point_ids: list[int] = Field(default_factory=list)

    @field_validator("question_text")
    @classmethod
    def clean_question_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question_text must not be blank")
        return cleaned

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


class SubjectSuggestion(BaseModel):
    id: int | None = None
    label: str | None = None
    confidence: float | None = None


class MistakeDraftSuggestionV1(BaseModel):
    """AI 草稿固定输出 schema (v1)。

    所有字段进入 capture 草稿区并允许人工编辑。
    schema 校验失败视为本次 AI 阶段失败，不写入 mistake_drafts。
    """

    question_text: str = Field(min_length=1)
    analysis_text: str = Field(min_length=1)
    error_summary: str = Field(min_length=1)
    subject_suggestion: SubjectSuggestion | None = None
    knowledge_point_suggestions: list[KnowledgePointSuggestion] = []
    warnings: list[str] = []


class CaptureDraftInput(BaseModel):
    """AI 草稿生成的输入。"""

    recognized_text: str
    user_error_context: str | None = None
    subject_id: int | None = None
    subject_label: str | None = None


class CaptureOut(BaseModel):
    id: uuid.UUID
    source_attachment_id: uuid.UUID
    status: CaptureStatus
    recognized_text: str | None
    user_error_context: str | None
    question_draft_text: str | None
    analysis_draft_text: str | None
    error_summary_draft: str | None
    subject_id: int | None
    knowledge_point_suggestions: list[KnowledgePointSuggestion]
    model_output_version: str
    attempt_count: int
    last_stage: CaptureLastStage | None
    error_code: str | None
    error_message_safe: str | None
    started_at: datetime | None
    finished_at: datetime | None
    mistake_draft_item_id: uuid.UUID | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConvertResultOut(BaseModel):
    """转换结果。"""

    capture: "CaptureOut"
    mistake_draft_item_id: uuid.UUID
    question_draft_id: uuid.UUID | None
