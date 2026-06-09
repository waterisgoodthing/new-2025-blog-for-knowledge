import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    children: Mapped[list["Folder"]] = relationship(
        back_populates="parent", lazy="selectin", cascade="save-update, merge"
    )
    parent: Mapped["Folder | None"] = relationship(
        back_populates="children", remote_side="Folder.id", lazy="selectin"
    )
    notes: Mapped[list] = relationship(
        "Note", foreign_keys="[Note.folder_id]", lazy="selectin", viewonly=True
    )

    __table_args__ = (
        Index("idx_folders_parent_id", "parent_id"),
        Index("idx_folders_sort_order", "sort_order"),
    )
