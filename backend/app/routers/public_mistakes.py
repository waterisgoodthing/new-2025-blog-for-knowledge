"""Unauthenticated public read of explicitly published canonical mistakes (W3-D03)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.mistake import PublicMistakeListResponse, PublicMistakeOut
from app.services import mistake_service

router = APIRouter(prefix="/api/public/mistakes", tags=["public-mistakes"])


@router.get("", response_model=PublicMistakeListResponse)
async def list_public_mistakes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await mistake_service.list_public_mistakes(db, page=page, size=size)
    empty = total == 0
    return PublicMistakeListResponse(
        items=[PublicMistakeOut(**item) for item in items],
        total=total,
        page=page,
        size=size,
        empty=empty,
        message="No published mistakes yet." if empty else None,
    )
