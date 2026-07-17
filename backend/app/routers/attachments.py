import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.attachment import AttachmentLinkCreate, AttachmentLinkOut, AttachmentOut
from app.services import attachment_service

router = APIRouter(
    prefix="/api/admin/attachments",
    tags=["admin-attachments"],
    dependencies=[Depends(get_current_admin)],
)

links_router = APIRouter(
    prefix="/api/admin/attachment-links",
    tags=["admin-attachment-links"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: attachment_service.AttachmentError) -> None:
    if isinstance(error, attachment_service.AttachmentNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, attachment_service.AttachmentConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[AttachmentOut])
async def list_attachments(
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    return await attachment_service.list_attachments(db, status=status_filter)


@router.post("", response_model=AttachmentOut, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return await attachment_service.create_attachment_from_stream(
            db,
            original_name=file.filename or "attachment",
            mime_type=file.content_type or "application/octet-stream",
            stream=file,
            created_by=admin.id,
        )
    except attachment_service.AttachmentError as error:
        _raise_http(error)


@router.get("/{attachment_id}", response_model=AttachmentOut)
async def get_attachment(
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await attachment_service.get_attachment(db, attachment_id)
    except attachment_service.AttachmentError as error:
        _raise_http(error)


@router.get("/{attachment_id}/content")
async def get_attachment_content(
    attachment_id: uuid.UUID,
    disposition: Literal["inline", "attachment"] = Query(default="inline"),
    db: AsyncSession = Depends(get_db),
):
    try:
        attachment = await attachment_service.get_attachment(db, attachment_id)
        path = await attachment_service.get_attachment_content_path(db, attachment_id)
        return FileResponse(
            path,
            media_type=attachment.mime_type,
            filename=attachment.original_name,
            content_disposition_type=disposition,
        )
    except attachment_service.AttachmentError as error:
        _raise_http(error)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        await attachment_service.delete_attachment(db, attachment_id)
    except attachment_service.AttachmentError as error:
        _raise_http(error)


@links_router.get("", response_model=list[AttachmentLinkOut])
async def list_attachment_links(
    target_type: str | None = None,
    target_id: str | None = None,
    attachment_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await attachment_service.list_attachment_links(
        db,
        target_type=target_type,
        target_id=target_id,
        attachment_id=attachment_id,
    )


@links_router.post("", response_model=AttachmentLinkOut, status_code=status.HTTP_201_CREATED)
async def create_attachment_link(
    payload: AttachmentLinkCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await attachment_service.create_attachment_link(db, payload)
    except attachment_service.AttachmentError as error:
        _raise_http(error)


@links_router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment_link(
    link_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        await attachment_service.delete_attachment_link(db, link_id)
    except attachment_service.AttachmentError as error:
        _raise_http(error)
