import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.question import (
    QuestionDraftCreate,
    QuestionDraftOut,
    QuestionDraftUpdate,
    QuestionOut,
    VersionCommand,
)
from app.services import draft_service

router = APIRouter(
    prefix="/api/admin/drafts",
    tags=["admin-drafts"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: draft_service.DraftError) -> None:
    if isinstance(error, draft_service.DraftNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, draft_service.DraftConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[QuestionDraftOut])
async def list_drafts(
    draft_type: str = "question",
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    if draft_type != "question":
        raise HTTPException(status_code=400, detail="Only question drafts are enabled")
    return await draft_service.list_question_drafts(db, status=status_filter)


@router.post(
    "/questions",
    response_model=QuestionDraftOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_question_draft(
    payload: QuestionDraftCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return await draft_service.create_question_draft(
            db,
            payload,
            created_by=admin.id,
        )
    except draft_service.DraftError as error:
        _raise_http(error)


@router.get("/{draft_item_id}", response_model=QuestionDraftOut)
async def get_draft(
    draft_item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await draft_service.get_question_draft(db, draft_item_id)
    except draft_service.DraftError as error:
        _raise_http(error)


@router.put("/{draft_item_id}", response_model=QuestionDraftOut)
async def update_draft(
    draft_item_id: uuid.UUID,
    payload: QuestionDraftUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await draft_service.update_question_draft(
            db,
            draft_item_id,
            payload,
        )
    except draft_service.DraftError as error:
        _raise_http(error)


@router.post("/{draft_item_id}/reject", response_model=QuestionDraftOut)
async def reject_draft(
    draft_item_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await draft_service.reject_question_draft(
            db,
            draft_item_id,
            version=payload.version,
        )
    except draft_service.DraftError as error:
        _raise_http(error)


@router.post("/{draft_item_id}/convert", response_model=QuestionOut)
async def convert_draft(
    draft_item_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await draft_service.convert_question_draft(
            db,
            draft_item_id,
            version=payload.version,
        )
    except draft_service.DraftError as error:
        _raise_http(error)
