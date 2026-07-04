import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ReviewItem(Base):
    __tablename__ = "review_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(20), default="active", server_default="active", nullable=False)
    algorithm: Mapped[str] = mapped_column(String(30), default="fixed_interval_v1", server_default="fixed_interval_v1", nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("target_type = 'mistake'", name="ck_review_items_target_type"),
        CheckConstraint("state IN ('active','paused')", name="ck_review_items_state"),
        CheckConstraint("algorithm = 'fixed_interval_v1'", name="ck_review_items_algorithm"),
        CheckConstraint("interval_days >= 0 AND repetitions >= 0", name="ck_review_items_counts"),
        UniqueConstraint("target_type", "target_id", name="uq_review_items_target"),
        Index("idx_review_items_due", "state", "next_review_at"),
    )


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("review_items.id", ondelete="RESTRICT"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    previous_interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    next_interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_review_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 0 AND 5", name="ck_review_records_rating"),
        CheckConstraint("previous_interval_days >= 0 AND next_interval_days > 0", name="ck_review_records_intervals"),
        Index("idx_review_records_item_time", "review_item_id", "reviewed_at"),
    )
