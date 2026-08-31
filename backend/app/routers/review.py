from datetime import date, datetime, timezone

from app.utils.datetime import utc_now_naive

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.note import Note
from app.routers.auth import get_current_admin
from app.schemas.note import NoteOut, ReviewPlan, ReviewRequest, ReviewStats
from app.services.review_planner import build_review_plan
from app.services.sm2 import sm2

router = APIRouter(prefix="/api/review", tags=["review"])


@router.get("/queue", response_model=list[NoteOut])
async def get_review_queue(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    today = date.today()
    result = await db.execute(
        select(Note)
        .options(selectinload(Note.tags))
        .where(Note.type == "mistake")
        .where(Note.next_review <= today)
        .order_by(Note.next_review.asc())
    )
    return result.scalars().all()


@router.post("/{slug}", response_model=NoteOut)
async def submit_review(
    slug: str,
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(Note).options(selectinload(Note.tags)).where(Note.slug == slug).where(Note.type == "mistake")
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Mistake not found")

    ef, interval, repetitions, next_review = sm2(
        quality=req.quality,
        ef=note.ef or 2.5,
        interval=note.interval or 0,
        repetitions=note.repetitions or 0,
    )

    note.ef = ef
    note.interval = interval
    note.repetitions = repetitions
    note.next_review = next_review
    note.last_reviewed = utc_now_naive()
    note.updated_at = utc_now_naive()

    await db.flush()
    await db.refresh(note)
    return note


@router.get("/stats", response_model=ReviewStats)
async def get_review_stats(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    today = date.today()

    total = (await db.execute(select(func.count()).where(Note.type == "mistake"))).scalar() or 0
    mastered = (
        await db.execute(select(func.count()).where(Note.type == "mistake").where(Note.next_review.is_(None)))
    ).scalar() or 0
    pending = (
        await db.execute(
            select(func.count()).where(Note.type == "mistake").where(Note.next_review.isnot(None))
        )
    ).scalar() or 0
    due_today = (
        await db.execute(
            select(func.count()).where(Note.type == "mistake").where(Note.next_review <= today)
        )
    ).scalar() or 0

    return ReviewStats(total_mistakes=total, mastered=mastered, pending_review=pending, due_today=due_today)


@router.get("/plan", response_model=ReviewPlan)
async def get_review_plan(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Note).options(selectinload(Note.tags)).where(Note.type == "mistake"))
    return build_review_plan(result.scalars().all())
