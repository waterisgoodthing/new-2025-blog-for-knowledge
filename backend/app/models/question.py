import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


QUESTION_TYPES = (
    "single_choice",
    "multiple_choice",
    "true_false",
    "short_answer",
    "essay",
)


class DraftItem(Base):
    __tablename__ = "draft_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", server_default="pending", nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    validation_errors: Mapped[list[dict]] = mapped_column(
        JSON, default=list, server_default="[]", nullable=False
    )
    target_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "draft_type IN ('question', 'mistake')",
            name="ck_draft_items_type",
        ),
        CheckConstraint(
            "(draft_type = 'question' AND source_type = 'manual') OR "
            "(draft_type = 'mistake' AND source_type IN ('question', 'question_draft'))",
            name="ck_draft_items_source",
        ),
        CheckConstraint(
            "status IN ('pending', 'needs_fix', 'rejected', 'converted')",
            name="ck_draft_items_status",
        ),
        CheckConstraint("version > 0", name="ck_draft_items_version"),
        CheckConstraint(
            "(status = 'converted' AND target_id IS NOT NULL AND "
            "((draft_type = 'question' AND target_type = 'question') OR "
            "(draft_type = 'mistake' AND target_type = 'mistake'))) "
            "OR (status <> 'converted' AND target_type IS NULL AND target_id IS NULL)",
            name="ck_draft_items_conversion_target",
        ),
        Index("idx_draft_items_status_updated", "status", "updated_at"),
        Index("idx_draft_items_type_status", "draft_type", "status"),
    )


class QuestionDraft(Base):
    __tablename__ = "question_drafts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("draft_items.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    options: Mapped[list[str]] = mapped_column(JSON, default=list, server_default="[]", nullable=False)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "question_type IN "
            "('single_choice', 'multiple_choice', 'true_false', 'short_answer', 'essay')",
            name="ck_question_drafts_type",
        ),
        CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('easy', 'medium', 'hard')",
            name="ck_question_drafts_difficulty",
        ),
        Index("idx_question_drafts_subject", "subject_id"),
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    options: Mapped[list[str]] = mapped_column(JSON, default=list, server_default="[]", nullable=False)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="active", server_default="active", nullable=False
    )
    visibility: Mapped[str] = mapped_column(
        String(20), default="private", server_default="private", nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "question_type IN "
            "('single_choice', 'multiple_choice', 'true_false', 'short_answer', 'essay')",
            name="ck_questions_type",
        ),
        CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('easy', 'medium', 'hard')",
            name="ck_questions_difficulty",
        ),
        CheckConstraint("status IN ('active', 'archived')", name="ck_questions_status"),
        CheckConstraint("visibility = 'private'", name="ck_questions_visibility"),
        CheckConstraint("version > 0", name="ck_questions_version"),
        Index("idx_questions_subject_status", "subject_id", "status"),
        Index("idx_questions_updated", "updated_at"),
    )


class QuestionSource(Base):
    __tablename__ = "question_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_ref: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("source_type = 'manual'", name="ck_question_sources_type"),
        UniqueConstraint("source_type", "source_ref", name="uq_question_sources_ref"),
        Index("idx_question_sources_question", "question_id"),
    )
