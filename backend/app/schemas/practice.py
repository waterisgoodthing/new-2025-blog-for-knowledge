from pydantic import BaseModel


class PracticeItem(BaseModel):
    """One daily-practice item; never carries answer/explanation data (W3-D05)."""

    question_id: str
    knowledge_point_id: int
    selection_reason: str


class PracticeEmptyMetadata(BaseModel):
    """Honest selection diagnostics for GET /api/admin/practice/today."""

    reason: str
    raw_candidate_count: int
    recent_attempt_excluded_count: int
    mastered_excluded_count: int
    eligible_candidate_count: int
    target_count: int
    returned_count: int
    window_hours: int


class PracticeTodayResponse(BaseModel):
    items: list[PracticeItem]
    empty_metadata: PracticeEmptyMetadata
