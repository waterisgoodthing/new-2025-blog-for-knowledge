import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.mistake import (
    MistakeDraftCreate,
    MistakeDraftOut,
    MistakeDraftUpdate,
    MistakeOut,
    VersionCommand,
)
from app.services import mistake_service

router = APIRouter(
    prefix="/api/admin/mistake-drafts",
    tags=["admin-mistake-drafts"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: mistake_service.MistakeError) -> None:
    if isinstance(error, mistake_service.MistakeNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, mistake_service.MistakeConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[MistakeDraftOut])
async def list_mistake_drafts(
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    records = await mistake_service.list_mistake_drafts(db)
    if status_filter is not None:
        records = [record for record in records if record.status == status_filter]
    return records


@router.post("", response_model=MistakeDraftOut, status_code=status.HTTP_201_CREATED)
async def create_mistake_draft(
    payload: MistakeDraftCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return await mistake_service.create_mistake_draft(
            db,
            payload,
            created_by=admin.id,
        )
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.get("/{draft_item_id}", response_model=MistakeDraftOut)
async def get_mistake_draft(
    draft_item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.get_mistake_draft(db, draft_item_id)
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.put("/{draft_item_id}", response_model=MistakeDraftOut)
async def update_mistake_draft(
    draft_item_id: uuid.UUID,
    payload: MistakeDraftUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.update_mistake_draft(db, draft_item_id, payload)
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.post("/{draft_item_id}/reject", response_model=MistakeDraftOut)
async def reject_mistake_draft(
    draft_item_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.reject_mistake_draft(
            db,
            draft_item_id,
            version=payload.version,
        )
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.post("/{draft_item_id}/convert", response_model=MistakeOut)
async def convert_mistake_draft(
    draft_item_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.convert_mistake_draft(
            db,
            draft_item_id,
            version=payload.version,
        )
    except mistake_service.MistakeError as error:
        _raise_http(error)
