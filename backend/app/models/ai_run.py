import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AiRun(Base):
    """Private business audit record for one AI task execution."""

    __tablename__ = "ai_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_used: Mapped[str | None] = mapped_column(String(50), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", server_default="pending"
    )
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    replay_input: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict | list | str | None] = mapped_column(JSON, nullable=True)
    warnings: Mapped[list | None] = mapped_column(JSON, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message_safe: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    parent_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    review_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_required", server_default="not_required"
    )
    review_revision: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'succeeded', 'failed')",
            name="ck_ai_runs_status",
        ),
        CheckConstraint(
            "validation_status IN ('pending', 'passed', 'failed', 'warning', 'not_applicable')",
            name="ck_ai_runs_validation_status",
        ),
        CheckConstraint(
            "review_status IN ('not_required', 'pending', 'accepted', 'rejected')",
            name="ck_ai_runs_review_status",
        ),
        CheckConstraint("attempt >= 1", name="ck_ai_runs_attempt"),
        CheckConstraint(
            "parent_run_id IS NULL OR parent_run_id <> id",
            name="ck_ai_runs_parent_not_self",
        ),
        Index("idx_ai_runs_created_at", "created_at"),
        Index("idx_ai_runs_task_type", "task_type"),
        Index("idx_ai_runs_status", "status"),
        Index("idx_ai_runs_review_status", "review_status"),
        Index("idx_ai_runs_parent_run_id", "parent_run_id"),
    )
