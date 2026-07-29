import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MistakeDraft(Base):
    __tablename__ = "mistake_drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("draft_items.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    question_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=True
    )
    question_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("question_drafts.id", ondelete="RESTRICT"), nullable=True
    )
    attempt_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attempts.id", ondelete="RESTRICT"), unique=True, nullable=True
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    my_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason_category: Mapped[str] = mapped_column(
        String(20), default="unknown", server_default="unknown", nullable=False
    )
    mistake_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "((question_id IS NOT NULL AND question_draft_id IS NULL AND attempt_id IS NULL) OR "
            "(question_id IS NULL AND question_draft_id IS NOT NULL AND attempt_id IS NULL) OR "
            "(question_id IS NOT NULL AND question_draft_id IS NULL AND attempt_id IS NOT NULL))",
            name="ck_mistake_drafts_question_source",
        ),
        CheckConstraint(
            "reason_category IN ('concept','calculation','reading','careless','unknown')",
            name="ck_mistake_drafts_reason_category",
        ),
        CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('easy','medium','hard')",
            name="ck_mistake_drafts_difficulty",
        ),
        Index("idx_mistake_drafts_subject", "subject_id"),
    )


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_draft_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("draft_items.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    my_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason_category: Mapped[str] = mapped_column(String(20), nullable=False)
    mistake_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active", nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), default="private", server_default="private", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('active','archived')", name="ck_mistakes_status"),
        CheckConstraint("visibility = 'private'", name="ck_mistakes_visibility"),
        CheckConstraint("version > 0", name="ck_mistakes_version"),
        Index("idx_mistakes_subject_status", "subject_id", "status"),
    )
