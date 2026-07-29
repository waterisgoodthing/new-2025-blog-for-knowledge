import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models.mistake import Mistake
from app.models.review_item import ReviewItem, ReviewRecord

class ReviewError(Exception): pass
class ReviewNotFound(ReviewError): pass
class ReviewConflict(ReviewError): pass

INTERVALS={0:1,1:1,2:1,3:3,4:7,5:14}

async def list_due_items(session,now=None):
    now=now or datetime.now(timezone.utc)
    items=(await session.execute(select(ReviewItem).where(ReviewItem.state=="active",ReviewItem.next_review_at<=now).order_by(ReviewItem.next_review_at))).scalars().all()
    return [(item,await session.get(Mistake,uuid.UUID(item.target_id))) for item in items]

async def list_records(session,item_id):
    if await session.get(ReviewItem, item_id) is None:
        raise ReviewNotFound("Review item not found")
    return list((await session.execute(select(ReviewRecord).where(ReviewRecord.review_item_id==item_id).order_by(ReviewRecord.reviewed_at.desc()))).scalars().all())

async def get_review_mistake(session, item):
    mistake = await session.get(Mistake, uuid.UUID(item.target_id))
    if mistake is None:
        raise ReviewNotFound("Review target not found")
    return mistake

async def submit_review(session,item_id,rating,expected_next_review_at,now=None):
    now=now or datetime.now(timezone.utc)
    item=(await session.execute(select(ReviewItem).where(ReviewItem.id==item_id).with_for_update())).scalar_one_or_none()
    if not item: raise ReviewNotFound("Review item not found")
    if item.state!="active": raise ReviewConflict("Review item is not active")
    if item.next_review_at!=expected_next_review_at: raise ReviewConflict("Review item changed")
    if item.next_review_at>now: raise ReviewConflict("Review item is not due")
    days=INTERVALS[rating]; next_at=now+timedelta(days=days)
    record=ReviewRecord(review_item_id=item.id,rating=rating,reviewed_at=now,
        previous_interval_days=item.interval_days,next_interval_days=days,
        previous_next_review_at=item.next_review_at,next_review_at=next_at)
    session.add(record); item.interval_days=days; item.repetitions+=1; item.last_reviewed_at=now; item.next_review_at=next_at
    await session.flush(); await session.refresh(record); await session.refresh(item); return item,record
