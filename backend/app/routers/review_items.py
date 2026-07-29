import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.review_item import ReviewItemOut, ReviewRecordOut, ReviewSubmit
from app.services import review_item_service

router = APIRouter(
    prefix="/api/admin/review/items",
    tags=["admin-review-items"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: review_item_service.ReviewError) -> None:
    if isinstance(error, review_item_service.ReviewNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, review_item_service.ReviewConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


def _item_out(item, mistake) -> ReviewItemOut:
    return ReviewItemOut(
        id=item.id,
        target_type=item.target_type,
        target_id=item.target_id,
        state=item.state,
        algorithm=item.algorithm,
        interval_days=item.interval_days,
        repetitions=item.repetitions,
        next_review_at=item.next_review_at,
        last_reviewed_at=item.last_reviewed_at,
        question_text=mistake.question_text,
        mistake_reason=mistake.mistake_reason,
    )


@router.get("", response_model=list[ReviewItemOut])
async def list_review_items(
    due: bool = True,
    db: AsyncSession = Depends(get_db),
):
    if not due:
        raise HTTPException(status_code=400, detail="Only the due queue is enabled")
    return [
        _item_out(item, mistake)
        for item, mistake in await review_item_service.list_due_items(db)
    ]


@router.get("/{item_id}/records", response_model=list[ReviewRecordOut])
async def list_review_records(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await review_item_service.list_records(db, item_id)
    except review_item_service.ReviewError as error:
        _raise_http(error)


@router.post("/{item_id}/submit", response_model=ReviewItemOut)
async def submit_review(
    item_id: uuid.UUID,
    payload: ReviewSubmit,
    db: AsyncSession = Depends(get_db),
):
    try:
        item, _record = await review_item_service.submit_review(
            db,
            item_id,
            rating=payload.rating,
            expected_next_review_at=payload.expected_next_review_at,
        )
        mistake = await review_item_service.get_review_mistake(db, item)
        return _item_out(item, mistake)
    except review_item_service.ReviewError as error:
        _raise_http(error)
