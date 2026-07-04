import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.mistake import MistakeOut, MistakeUpdate, VersionCommand
from app.services import mistake_service

router = APIRouter(
    prefix="/api/admin/mistakes",
    tags=["admin-mistakes"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: mistake_service.MistakeError) -> None:
    if isinstance(error, mistake_service.MistakeNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, mistake_service.MistakeConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[MistakeOut])
async def list_mistakes(
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    return await mistake_service.list_mistakes(db, status=status_filter)


@router.get("/{mistake_id}", response_model=MistakeOut)
async def get_mistake(
    mistake_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.get_mistake(db, mistake_id)
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.put("/{mistake_id}", response_model=MistakeOut)
async def update_mistake(
    mistake_id: uuid.UUID,
    payload: MistakeUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.update_mistake(db, mistake_id, payload)
    except mistake_service.MistakeError as error:
        _raise_http(error)


@router.delete("/{mistake_id}", response_model=MistakeOut)
async def archive_mistake(
    mistake_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await mistake_service.archive_mistake(
            db,
            mistake_id,
            version=payload.version,
        )
    except mistake_service.MistakeError as error:
        _raise_http(error)
