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


class DashboardWeakKnowledgePoint(BaseModel):
    knowledge_point_id: int
    name: str
    attempt_count: int
    wrong_rate: float
    lapse_count: int
    due_count: int


class DashboardRecentlyMasteredItem(BaseModel):
    review_item_id: uuid.UUID
    mistake_id: uuid.UUID
    question_text: str
    mastered_at: datetime


class DashboardSectionAction(BaseModel):
    section: Literal["review", "practice"]
    count: int
    available: bool
    target_route: str
    reason: str


class DashboardSectionActions(BaseModel):
    review: DashboardSectionAction
    practice: DashboardSectionAction


class DashboardTodayFirstAction(BaseModel):
    kind: Literal["review", "practice", "none"]
    count: int
    target_route: str | None
    reason: str


class DashboardSummary(BaseModel):
    generated_at: datetime
    counts: DashboardCounts
    recent_questions: list[DashboardQuestionActivity]
    recent_mistakes: list[DashboardMistakeActivity]
    recent_reviews: list[DashboardReviewActivity]
    sections: DashboardSections
    system: DashboardSystemStatus
    review_today_count: int
    practice_today_count: int
    weak_top3: list[DashboardWeakKnowledgePoint]
    recently_mastered_4: list[DashboardRecentlyMasteredItem]
    today_first_action: DashboardTodayFirstAction
    section_actions: DashboardSectionActions
