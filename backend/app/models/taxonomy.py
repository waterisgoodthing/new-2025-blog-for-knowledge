from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("knowledge_points.id", ondelete="RESTRICT"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("subject_id", "parent_id", "name", name="uq_knowledge_points_sibling_name"),
        Index("idx_knowledge_points_subject_parent_sort", "subject_id", "parent_id", "sort_order", "id"),
        Index("idx_knowledge_points_parent", "parent_id"),
    )

    parent: Mapped["KnowledgePoint | None"] = relationship(
        "KnowledgePoint",
        remote_side=[id],
        back_populates="children",
    )
    children: Mapped[list["KnowledgePoint"]] = relationship(
        "KnowledgePoint",
        back_populates="parent",
    )


class KnowledgePointLink(Base):
    __tablename__ = "knowledge_point_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("knowledge_points.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "knowledge_point_id",
            "target_type",
            "target_id",
            name="uq_knowledge_point_links_target",
        ),
        Index("idx_knowledge_point_links_target", "target_type", "target_id"),
    )
