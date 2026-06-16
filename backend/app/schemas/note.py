import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class NoteType(str, Enum):
    note = "note"
    blog = "blog"
    mistake = "mistake"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class NoteStatus(str, Enum):
    draft = "draft"
    published = "published"


class NoteCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=255)
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    type: NoteType = NoteType.note
    status: NoteStatus = NoteStatus.published
    hidden: bool = False
    tags: list[str] = []
    folder_id: uuid.UUID | None = None
    sort_order: int = 0

    summary: str | None = None
    cover: str | None = None
    category: str | None = None

    subject: str | None = None
    difficulty: Difficulty | None = None
    question: str | None = None
    my_answer: str | None = None
    correct_answer: str | None = None
    analysis: str | None = None
    knowledge_points: str | None = None
    images: list[str] | None = None
    ai_metadata: dict | None = None


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    type: NoteType | None = None
    status: NoteStatus | None = None
    hidden: bool | None = None
    tags: list[str] | None = None
    sort_order: int | None = None

    summary: str | None = None
    cover: str | None = None
    category: str | None = None

    subject: str | None = None
    difficulty: Difficulty | None = None
    question: str | None = None
    my_answer: str | None = None
    correct_answer: str | None = None
    analysis: str | None = None
    knowledge_points: str | None = None
    images: list[str] | None = None
    ai_metadata: dict | None = None
    folder_id: uuid.UUID | None = None


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class NoteOut(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    content: str
    type: NoteType
    status: NoteStatus = NoteStatus.published
    hidden: bool
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut] = []
    folder_id: uuid.UUID | None = None
    sort_order: int = 0

    summary: str | None = None
    cover: str | None = None
    category: str | None = None

    subject: str | None = None
    difficulty: Difficulty | None = None
    question: str | None = None
    my_answer: str | None = None
    correct_answer: str | None = None
    analysis: str | None = None
    knowledge_points: str | None = None
    ef: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review: date | None = None
    last_reviewed: datetime | None = None
    images: list[str] | None = None
    ai_metadata: dict | None = None

    model_config = {"from_attributes": True}


class NoteListItem(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    type: NoteType
    status: NoteStatus = NoteStatus.published
    hidden: bool
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut] = []
    folder_id: uuid.UUID | None = None
    sort_order: int = 0

    summary: str | None = None
    cover: str | None = None
    category: str | None = None

    subject: str | None = None
    difficulty: Difficulty | None = None
    ef: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review: date | None = None
    last_reviewed: datetime | None = None
    images: list[str] | None = None
    ai_metadata: dict | None = None

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    items: list[NoteListItem]
    total: int
    page: int
    size: int


class ReviewRequest(BaseModel):
    quality: int = Field(..., ge=0, le=5)


class ReviewStats(BaseModel):
    total_mistakes: int
    mastered: int
    pending_review: int
    due_today: int


class ReviewSubjectSummary(BaseModel):
    subject: str
    total: int
    due_today: int
    hard: int
    average_ef: float


class ReviewWeaknessItem(BaseModel):
    name: str
    count: int
    due_today: int
    subjects: list[str] = Field(default_factory=list)


class ReviewPlan(BaseModel):
    today_count: int
    overdue_count: int
    week_count: int
    next_review_date: date | None = None
    subject_summaries: list[ReviewSubjectSummary] = Field(default_factory=list)
    weaknesses: list[ReviewWeaknessItem] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SubjectOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    sort_order: int

    model_config = {"from_attributes": True}


class NameCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
