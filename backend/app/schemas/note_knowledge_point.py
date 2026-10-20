import uuid

from pydantic import BaseModel


class NoteKnowledgePointLinkOut(BaseModel):
    """Result of an explicit admin link action (idempotent)."""

    note_id: uuid.UUID
    knowledge_point_id: int
    linked: bool = True


class KnowledgePointNoteItem(BaseModel):
    """Compact Note projection for the KP -> note direction."""

    id: uuid.UUID
    slug: str
    title: str
    type: str
    status: str
    hidden: bool

    model_config = {"from_attributes": True}
