import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ReviewSubmit(BaseModel):
    rating: int = Field(ge=0, le=5)
    expected_next_review_at: datetime
    attempt_id: uuid.UUID | None = None


class ReviewItemOut(BaseModel):
    id: uuid.UUID
    target_type: str
    target_id: str
    state: Literal["active", "mastered", "paused"]
    algorithm: Literal["fixed_interval_v1", "fixed_interval_v2"]
    interval_days: int
    repetitions: int
    next_review_at: datetime
    last_reviewed_at: datetime | None
    last_rating: int | None
    question_text: str
    mistake_reason: str | None

    model_config = {"from_attributes": True}


class ReviewRecordOut(BaseModel):
    id: uuid.UUID
    review_item_id: uuid.UUID
    rating: int
    reviewed_at: datetime
    previous_interval_days: int
    next_interval_days: int
    previous_next_review_at: datetime
    next_review_at: datetime
    previous_state: Literal["active", "mastered", "paused"]
    new_state: Literal["active", "mastered", "paused"]
    attempt_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
