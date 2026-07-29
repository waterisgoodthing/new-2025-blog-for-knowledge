import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.capture import (
    CaptureConvert,
    CaptureCreate,
    CaptureOut,
    CapturePatch,
    ConvertResultOut,
)
from app.services import capture_service

router = APIRouter(
    prefix="/api/admin/captures",
    tags=["admin-captures"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: capture_service.CaptureError) -> None:
    if isinstance(error, capture_service.CaptureNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, capture_service.CaptureConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, capture_service.CaptureValidationError):
        raise HTTPException(status_code=422, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[CaptureOut])
async def list_captures(
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    return await capture_service.list_captures(db, status=status_filter)


@router.post("", response_model=CaptureOut, status_code=status.HTTP_201_CREATED)
async def create_capture(
    payload: CaptureCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return await capture_service.create_capture(
            db, payload, created_by=admin.id
        )
    except capture_service.CaptureError as error:
        _raise_http(error)


@router.get("/{capture_id}", response_model=CaptureOut)
async def get_capture(
    capture_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await capture_service.get_capture(db, capture_id)
    except capture_service.CaptureError as error:
        _raise_http(error)


@router.patch("/{capture_id}", response_model=CaptureOut)
async def patch_capture(
    capture_id: uuid.UUID,
    payload: CapturePatch,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await capture_service.patch_capture(db, capture_id, payload)
    except capture_service.CaptureError as error:
        _raise_http(error)


@router.post("/{capture_id}/recognize", response_model=CaptureOut)
async def trigger_recognition(
    capture_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await capture_service.trigger_recognition(db, capture_id)
    except capture_service.CaptureError as error:
        _raise_http(error)


@router.post("/{capture_id}/draft", response_model=CaptureOut)
async def trigger_draft(
    capture_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await capture_service.trigger_draft(db, capture_id)
    except capture_service.CaptureError as error:
        _raise_http(error)


@router.post("/{capture_id}/convert", response_model=ConvertResultOut)
async def convert_capture(
    capture_id: uuid.UUID,
    payload: CaptureConvert,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        result = await capture_service.convert_capture(
            db, capture_id, payload, created_by=admin.id
        )
        return ConvertResultOut(
            capture=CaptureOut.model_validate(result.capture),
            mistake_draft_item_id=result.mistake_draft_item_id,
            question_draft_id=result.question_draft_id,
        )
    except capture_service.CaptureError as error:
        _raise_http(error)
