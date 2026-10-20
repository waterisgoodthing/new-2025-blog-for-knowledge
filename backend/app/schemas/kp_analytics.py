from pydantic import BaseModel


class KnowledgePointAnalyticsItem(BaseModel):
    knowledge_point_id: int
    attempt_count: int
    wrong_count: int
    review_count: int
    due_count: int
    accuracy: float
    wrong_rate: float
    lapse_count: int
