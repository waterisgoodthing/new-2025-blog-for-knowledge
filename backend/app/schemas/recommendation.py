from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class RecommendationType(str, Enum):
    note = "note"
    mistake = "mistake"
    review = "review"
    resource = "resource"
    music = "music"
    podcast = "podcast"


class DailyRecommendationOut(BaseModel):
    date: date
    title: str
    type: RecommendationType
    reason: str
    target: str | None = None
    action_label: str | None = None
    source: str | None = None

    model_config = {"from_attributes": True}


class RecommendationHistoryItem(BaseModel):
    id: int
    date: date
    title: str
    type: RecommendationType
    reason: str
    target: str | None = None
    action_label: str | None = None
    source: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
