import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_provider: Mapped[str] = mapped_column(
        String(30), default="local", server_default="local", nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    visibility: Mapped[str] = mapped_column(
        String(20), default="private", server_default="private", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active", server_default="active", nullable=False
    )
    folder_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trashed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("storage_provider = 'local'", name="ck_attachments_storage_provider"),
        CheckConstraint("visibility = 'private'", name="ck_attachments_visibility"),
        CheckConstraint("status IN ('active','missing','trashed','deleted')", name="ck_attachments_status"),
        CheckConstraint("size_bytes >= 0", name="ck_attachments_size"),
        CheckConstraint("char_length(checksum_sha256) = 64", name="ck_attachments_checksum"),
        Index("idx_attachments_status_created", "status", "created_at"),
        Index("idx_attachments_checksum", "checksum_sha256"),
        Index("idx_attachments_folder_display", "folder_id", "display_name"),
    )


class AttachmentLink(Base):
    __tablename__ = "attachment_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attachments.id", ondelete="CASCADE"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "target_type IN ('question_draft','question','mistake')",
            name="ck_attachment_links_target_type",
        ),
        CheckConstraint(
            "purpose IN ('source','question','answer','inline','ai_input','ai_output')",
            name="ck_attachment_links_purpose",
        ),
        UniqueConstraint(
            "attachment_id",
            "target_type",
            "target_id",
            "purpose",
            name="uq_attachment_links_target_purpose",
        ),
        Index("idx_attachment_links_attachment", "attachment_id"),
        Index("idx_attachment_links_target", "target_type", "target_id"),
    )
