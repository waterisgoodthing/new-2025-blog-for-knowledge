import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    note = "note"
    mistake = "mistake"


class RelationType(str, Enum):
    explains = "explains"
    similar = "similar"
    prerequisite = "prerequisite"
    follow_up = "follow_up"
    source_for = "source_for"


class RelationStatus(str, Enum):
    suggested = "suggested"


class ReviewStateFilter(str, Enum):
    due = "due"
    overdue = "overdue"
    upcoming = "upcoming"
    all = "all"


class SourceRef(BaseModel):
    source_type: SourceType
    source_id: str
    title: str = ""
    slug: str = ""
    field: str = ""
    excerpt: str = ""
    url: str = ""
    confidence: float = 0.0
    match_reasons: list[str] = Field(default_factory=list)


class RelationSuggestion(BaseModel):
    source_type: SourceType
    source_id: str
    target_type: SourceType
    target_id: str
    relation_type: RelationType
    score: float = 0.0
    reason: str = ""
    status: RelationStatus = RelationStatus.suggested


class DateRange(BaseModel):
    from_date: date | None = Field(None, alias="from")
    to_date: date | None = Field(None, alias="to")

    model_config = {"populate_by_name": True}


class ContextPackRequest(BaseModel):
    subject: str | None = None
    knowledge_points: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    type: str | None = None
    difficulty: str | None = None
    date_range: DateRange | None = None
    review_state: ReviewStateFilter | None = None
    limit: int = Field(default=10, ge=1, le=100)


class ContextPackStats(BaseModel):
    mistake_count: int = 0
    note_count: int = 0
    top_error_reasons: list[str] = Field(default_factory=list)


class NoteBrief(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    type: str
    subject: str | None = None
    knowledge_points: str | None = None
    difficulty: str | None = None
    summary: str | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContextPackResponse(BaseModel):
    sources: list[SourceRef] = Field(default_factory=list)
    related_notes: list[NoteBrief] = Field(default_factory=list)
    related_mistakes: list[NoteBrief] = Field(default_factory=list)
    suggested_relations: list[RelationSuggestion] = Field(default_factory=list)
    stats: ContextPackStats = Field(default_factory=ContextPackStats)


class WeakPointItem(BaseModel):
    subject: str
    knowledge_point: str
    mistake_count: int = 0
    due_review_count: int = 0
    recent_error_count: int = 0
    top_error_reasons: list[str] = Field(default_factory=list)
    evidence_sources: list[SourceRef] = Field(default_factory=list)


class WeakPointsResponse(BaseModel):
    days: int
    weak_points: list[WeakPointItem] = Field(default_factory=list)


class CitationBlockType(str, Enum):
    source_backed_claim = "source_backed_claim"
    ai_inference = "ai_inference"
    insufficient_context = "insufficient_context"


class CitationBlock(BaseModel):
    type: CitationBlockType
    text: str = ""
    source_refs: list[SourceRef] = Field(default_factory=list)


class KnowledgeSummaryRequest(BaseModel):
    mode: str = "exam_review_summary"
    context_pack: ContextPackResponse
    requirements: dict = Field(default_factory=lambda: {
        "language": "zh-CN",
        "style": "exam_review",
        "max_length": 1200,
        "require_citations": True,
    })


class KnowledgeSummaryResponse(BaseModel):
    title: str = ""
    blocks: list[CitationBlock] = Field(default_factory=list)


class InsufficientContextResponse(BaseModel):
    status: str = "insufficient_context"
    message: str = "No usable source references are available for factual generation."
    outline: list[str] = Field(default_factory=list)
