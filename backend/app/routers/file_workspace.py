import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attachment import Attachment
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.attachment import AttachmentOut
from app.schemas.file_workspace import FileMoveRequest, FileRenameRequest
from app.services.file_workspace_service import (
    FileWorkspaceConflict,
    FileWorkspaceError,
    FileWorkspaceNotFound,
    move_attachment,
    rename_attachment,
    restore_attachment,
    trash_attachment,
)

router = APIRouter(
    prefix="/api/admin/workspace/files",
    tags=["admin-file-workspace"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: FileWorkspaceError) -> None:
    if isinstance(error, FileWorkspaceNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, FileWorkspaceConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[AttachmentOut])
async def list_workspace_files(
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    query = select(Attachment).order_by(Attachment.updated_at.desc())
    if status_filter:
        query = query.where(Attachment.status == status_filter)
    return list((await db.scalars(query)).all())


@router.patch("/{attachment_id}/rename", response_model=AttachmentOut)
async def rename_workspace_file(
    attachment_id: uuid.UUID,
    payload: FileRenameRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    try:
        return await rename_attachment(db, attachment_id, payload.display_name)
    except FileWorkspaceError as error:
        _raise_http(error)


@router.patch("/{attachment_id}/move", response_model=AttachmentOut)
async def move_workspace_file(
    attachment_id: uuid.UUID,
    payload: FileMoveRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    try:
        return await move_attachment(db, attachment_id, payload.folder_id)
    except FileWorkspaceError as error:
        _raise_http(error)


@router.post("/{attachment_id}/trash", response_model=AttachmentOut)
async def trash_workspace_file(
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    try:
        return await trash_attachment(db, attachment_id)
    except FileWorkspaceError as error:
        _raise_http(error)


@router.post("/{attachment_id}/restore", response_model=AttachmentOut)
async def restore_workspace_file(
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    try:
        return await restore_attachment(db, attachment_id)
    except FileWorkspaceError as error:
        _raise_http(error)
