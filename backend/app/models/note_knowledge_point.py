import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NoteKnowledgePoint(Base):
    """Canonical Note <-> KnowledgePoint association (W3-D04, migration 032).

    The pair is the primary key; both foreign keys cascade on delete. This is
    distinct from the polymorphic ``knowledge_point_links`` table (which stays
    untouched). ``Note.subject`` remains free text, so no subject-consistency
    rule is enforced here by design (deferred normalisation, PR-12 scope).
    """

    __tablename__ = "note_knowledge_points"

    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "notes.id",
            ondelete="CASCADE",
            name="fk_note_knowledge_points_note_id",
        ),
        primary_key=True,
    )
    knowledge_point_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "knowledge_points.id",
            ondelete="CASCADE",
            name="fk_note_knowledge_points_knowledge_point_id",
        ),
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_note_knowledge_points_kp", "knowledge_point_id", "note_id"),
    )
