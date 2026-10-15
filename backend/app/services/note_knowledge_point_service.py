import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.note_knowledge_point import NoteKnowledgePoint
from app.models.taxonomy import KnowledgePoint


class NoteKnowledgePointError(Exception):
    pass


class NoteKnowledgePointNotFound(NoteKnowledgePointError):
    pass


class NoteKnowledgePointConflict(NoteKnowledgePointError):
    pass


async def _require_note(session: AsyncSession, note_id: uuid.UUID) -> Note:
    note = await session.get(Note, note_id)
    if note is None:
        raise NoteKnowledgePointNotFound("Note not found")
    return note


async def _require_knowledge_point(
    session: AsyncSession, knowledge_point_id: int
) -> KnowledgePoint:
    knowledge_point = await session.get(KnowledgePoint, knowledge_point_id)
    if knowledge_point is None:
        raise NoteKnowledgePointNotFound("Knowledge point not found")
    return knowledge_point


async def _lock_knowledge_point(
    session: AsyncSession, knowledge_point_id: int
) -> KnowledgePoint:
    """Refresh the KP row without a blocking write lock.

    EV02/B03: delete-side ``delete_knowledge_point`` takes the KP ``FOR UPDATE``
    and serialises the two write families; the link/unlink side deliberately
    refreshes only (a blocking lock here deadlocks the canonical concurrent
    link re-play case). If a link races a committed delete, its FK insert
    fails and surfaces as an idempotent conflict instead of dangling data.
    """
    knowledge_point = (
        await session.execute(
            select(KnowledgePoint)
            .where(KnowledgePoint.id == knowledge_point_id)
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    if knowledge_point is None:
        raise NoteKnowledgePointNotFound("Knowledge point not found")
    return knowledge_point


async def link(
    session: AsyncSession,
    note_id: uuid.UUID,
    knowledge_point_id: int,
) -> bool:
    """Create an explicit Note <-> KP association.

    Returns ``True`` when a new row was created and ``False`` when the pair was
    already linked. The operation is idempotent: duplicates, including a
    concurrent insert that wins the composite-primary-key race, are treated as
    a success no-op and never surface as a 500.
    """
    await _lock_knowledge_point(session, knowledge_point_id)
    await _require_note(session, note_id)

    existing = await session.get(NoteKnowledgePoint, (note_id, knowledge_point_id))
    if existing is not None:
        return False

    row = NoteKnowledgePoint(
        note_id=note_id, knowledge_point_id=knowledge_point_id
    )
    try:
        async with session.begin_nested():
            session.add(row)
    except IntegrityError:
        survivor = await session.get(
            NoteKnowledgePoint, (note_id, knowledge_point_id)
        )
        if survivor is None:
            raise NoteKnowledgePointConflict(
                "Failed to link note to knowledge point"
            ) from None
        return False
    return True


async def unlink(
    session: AsyncSession,
    note_id: uuid.UUID,
    knowledge_point_id: int,
) -> bool:
    """Remove a Note <-> KP association.

    Returns ``True`` when a row was removed and ``False`` when the pair was not
    linked. Unlinking an absent relation is an idempotent no-op.
    """
    await _lock_knowledge_point(session, knowledge_point_id)
    await _require_note(session, note_id)

    row = await session.get(NoteKnowledgePoint, (note_id, knowledge_point_id))
    if row is None:
        return False
    await session.delete(row)
    await session.flush()
    return True


async def list_knowledge_points(
    session: AsyncSession, note_id: uuid.UUID
) -> list[KnowledgePoint]:
    await _require_note(session, note_id)
    statement = (
        select(KnowledgePoint)
        .join(
            NoteKnowledgePoint,
            NoteKnowledgePoint.knowledge_point_id == KnowledgePoint.id,
        )
        .where(NoteKnowledgePoint.note_id == note_id)
        .order_by(KnowledgePoint.sort_order, KnowledgePoint.id)
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


async def list_notes(
    session: AsyncSession, knowledge_point_id: int
) -> list[Note]:
    await _require_knowledge_point(session, knowledge_point_id)
    statement = (
        select(Note)
        .join(NoteKnowledgePoint, NoteKnowledgePoint.note_id == Note.id)
        .where(NoteKnowledgePoint.knowledge_point_id == knowledge_point_id)
        .order_by(Note.updated_at.desc(), Note.id)
    )
    result = await session.execute(statement)
    return list(result.scalars().all())
