import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DashboardCounts(BaseModel):
    questions: int
    mistakes: int
    knowledge_points: int
    attachments: int
    due_reviews: int


class DashboardQuestionActivity(BaseModel):
    id: uuid.UUID
    title: str | None
    question_text: str
    updated_at: datetime


class DashboardMistakeActivity(BaseModel):
    id: uuid.UUID
    title: str | None
    question_text: str
    reason_category: str
    updated_at: datetime


class DashboardReviewActivity(BaseModel):
    id: uuid.UUID
    review_item_id: uuid.UUID
    rating: int
    reviewed_at: datetime
    question_text: str


class DashboardSystemStatus(BaseModel):
    service: Literal["ok"]
    database: Literal["ok", "unavailable"]
    storage: Literal["ok", "unknown"]


class DashboardSections(BaseModel):
    learning: Literal["ready", "unavailable", "empty"]
    activity: Literal["ready", "unavailable", "empty"]
    storage: Literal["ready", "unknown", "empty"]


class DashboardSummary(BaseModel):
    generated_at: datetime
    counts: DashboardCounts
    recent_questions: list[DashboardQuestionActivity]
    recent_mistakes: list[DashboardMistakeActivity]
    recent_reviews: list[DashboardReviewActivity]
    sections: DashboardSections
    system: DashboardSystemStatus
