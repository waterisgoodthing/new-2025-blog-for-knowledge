import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note
from app.routers.auth import get_current_admin
from app.schemas.note_knowledge_point import (
    KnowledgePointNoteItem,
    NoteKnowledgePointLinkOut,
)
from app.schemas.taxonomy import KnowledgePointOut
from app.services import note_knowledge_point_service
from app.services.legacy_mistake_freeze import (
    LegacyMistakeWriteFrozen,
    assert_not_legacy_mistake_write,
    freeze_error_detail,
)
from app.services.note_knowledge_point_service import (
    NoteKnowledgePointConflict,
    NoteKnowledgePointError,
    NoteKnowledgePointNotFound,
)

router = APIRouter(
    prefix="/api/admin/notes",
    tags=["admin-notes"],
    dependencies=[Depends(get_current_admin)],
)


async def _assert_note_not_frozen(
    db: AsyncSession, note_id: uuid.UUID, operation: str
) -> None:
    """F03: a Note<->KP link is a metadata write on the note; freeze legacy ones."""
    note = await db.get(Note, note_id)
    if note is None:
        return
    try:
        assert_not_legacy_mistake_write(note.type, operation=operation)
    except LegacyMistakeWriteFrozen as freeze:
        raise HTTPException(
            status_code=410,
            detail=freeze_error_detail(freeze.operation),
        ) from freeze


def _raise_http(error: NoteKnowledgePointError) -> None:
    if isinstance(error, NoteKnowledgePointNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, NoteKnowledgePointConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get(
    "/knowledge-points/{knowledge_point_id}/notes",
    response_model=list[KnowledgePointNoteItem],
)
async def list_notes_for_knowledge_point(
    knowledge_point_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await note_knowledge_point_service.list_notes(db, knowledge_point_id)
    except NoteKnowledgePointError as error:
        _raise_http(error)


@router.get("/{note_id}/knowledge-points", response_model=list[KnowledgePointOut])
async def list_knowledge_points_for_note(
    note_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await note_knowledge_point_service.list_knowledge_points(db, note_id)
    except NoteKnowledgePointError as error:
        _raise_http(error)


@router.post(
    "/{note_id}/knowledge-points/{knowledge_point_id}",
    response_model=NoteKnowledgePointLinkOut,
)
async def link_note_knowledge_point(
    note_id: uuid.UUID,
    knowledge_point_id: int,
    db: AsyncSession = Depends(get_db),
):
    await _assert_note_not_frozen(db, note_id, "admin_notes.link_knowledge_point")
    try:
        await note_knowledge_point_service.link(db, note_id, knowledge_point_id)
    except NoteKnowledgePointError as error:
        _raise_http(error)
    return NoteKnowledgePointLinkOut(
        note_id=note_id,
        knowledge_point_id=knowledge_point_id,
        linked=True,
    )


@router.delete(
    "/{note_id}/knowledge-points/{knowledge_point_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlink_note_knowledge_point(
    note_id: uuid.UUID,
    knowledge_point_id: int,
    db: AsyncSession = Depends(get_db),
):
    await _assert_note_not_frozen(db, note_id, "admin_notes.unlink_knowledge_point")
    try:
        await note_knowledge_point_service.unlink(db, note_id, knowledge_point_id)
    except NoteKnowledgePointError as error:
        _raise_http(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
