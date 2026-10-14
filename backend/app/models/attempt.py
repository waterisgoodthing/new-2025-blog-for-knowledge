import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False)
    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    mistake_draft_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("draft_items.id", ondelete="RESTRICT"), unique=True, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    context_type: Mapped[str] = mapped_column(String(20), default="practice", server_default="practice", nullable=False)

    __table_args__ = (
        CheckConstraint("length(trim(submitted_answer)) > 0", name="ck_attempts_answer_not_blank"),
        CheckConstraint("context_type IN ('practice','review','editor_check')", name="ck_attempts_context_type"),
        Index("idx_attempts_question_submitted", "question_id", "submitted_at"),
        Index("idx_attempts_context_submitted", "context_type", "submitted_at"),
    )
