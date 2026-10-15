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
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CaptureItem(Base):
    """采集过程工作区。不是正式错题事实源。

    AI/OCR 输出只进入本表的草稿字段，不得直接写 mistakes 或 review_items。
    转换后通过 mistake_draft_item_id 关联到既有错题草稿链路。
    """

    __tablename__ = "capture_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attachments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), default="uploaded", server_default="uploaded", nullable=False
    )
    recognized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_error_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_draft_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    analysis_draft_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_summary_draft: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=True
    )
    knowledge_point_suggestions: Mapped[list[dict]] = mapped_column(
        JSON, default=list, server_default="[]", nullable=False
    )
    model_output_version: Mapped[str] = mapped_column(
        String(20), default="v1", server_default="v1", nullable=False
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    last_stage: Mapped[str | None] = mapped_column(String(20), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message_safe: Mapped[str | None] = mapped_column(String(300), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    mistake_draft_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("draft_items.id", ondelete="RESTRICT"),
        unique=True,
        nullable=True,
    )
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
            "status IN ('uploaded','recognizing','recognized','drafting','ready','failed','converted','archived')",
            name="ck_capture_items_status",
        ),
        CheckConstraint(
            "(status = 'converted' AND mistake_draft_item_id IS NOT NULL) OR "
            "(status <> 'converted' AND mistake_draft_item_id IS NULL)",
            name="ck_capture_items_conversion",
        ),
        CheckConstraint("attempt_count >= 0", name="ck_capture_items_attempt_count"),
        CheckConstraint(
            "last_stage IS NULL OR last_stage IN ('recognize','draft','convert')",
            name="ck_capture_items_last_stage",
        ),
        Index("idx_capture_items_status_created", "status", "created_at"),
        Index("idx_capture_items_source_attachment", "source_attachment_id"),
    )
