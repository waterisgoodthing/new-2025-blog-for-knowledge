import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.review_item import ReviewItem, ReviewRecord

class ReviewError(Exception): pass
class ReviewNotFound(ReviewError): pass
class ReviewConflict(ReviewError): pass
class ReviewInvalid(ReviewError): pass

# fixed_interval_v2 (design D2, final — no v1/v2 selection): failures reset the
# streak (lapse), successes climb a ladder keyed by the post-increment streak,
# capped at 30d. rating=5 only feeds mastery, it never jumps the ladder.
LAPSE_INTERVALS={0:1,1:1,2:2}
SUCCESS_LADDER={1:3,2:7,3:14,4:30}
MASTERY_REPETITIONS=4
MASTERY_MIN_RATING=4

def schedule_v2(rating,repetitions):
    if not isinstance(rating,int) or isinstance(rating,bool) or not 0<=rating<=5:
        raise ValueError("rating must be an int in 0..5")
    if rating in LAPSE_INTERVALS: return 0,LAPSE_INTERVALS[rating]
    streak=repetitions+1
    return streak,SUCCESS_LADDER[min(streak,4)]

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

async def _resolve_reanswer_attempt(session,item,attempt_id):
    """Validate the audit linkage for a re-answer flow submission (D5).

    Returns the attempt UUID to record, or None for the legal no-attempt
    paths (human-only confirm for question-less mistakes, plain rating
    without re-answer). Raises ReviewInvalid (HTTP 400) on misuse.
    """
    if attempt_id is None: return None
    attempt=await session.get(Attempt,attempt_id)
    if attempt is None: raise ReviewNotFound("Re-answer attempt not found")
    if attempt.context_type!="review":
        raise ReviewInvalid("Only review-context attempts can back a review record")
    mistake=await session.get(Mistake,item.mistake_id)
    if mistake is None: raise ReviewNotFound("Review target not found")
    if mistake.question_id is not None and attempt.question_id!=mistake.question_id:
        raise ReviewInvalid("Re-answer attempt does not belong to this mistake's question")
    return attempt.id

async def submit_review(session,item_id,rating,expected_next_review_at,now=None,attempt_id=None):
    now=now or datetime.now(timezone.utc)
    item=(await session.execute(select(ReviewItem).where(ReviewItem.id==item_id).with_for_update())).scalar_one_or_none()
    if not item: raise ReviewNotFound("Review item not found")
    if item.state!="active": raise ReviewConflict("Review item is not active")
    if item.next_review_at!=expected_next_review_at: raise ReviewConflict("Review item changed")
    if item.next_review_at>now: raise ReviewConflict("Review item is not due")
    previous_state=item.state
    streak,days=schedule_v2(rating,item.repetitions)
    new_state="mastered" if streak>=MASTERY_REPETITIONS and rating>=MASTERY_MIN_RATING else "active"
    next_at=now+timedelta(days=days)
    record=ReviewRecord(review_item_id=item.id,rating=rating,reviewed_at=now,
        previous_interval_days=item.interval_days,next_interval_days=days,
        previous_next_review_at=item.next_review_at,next_review_at=next_at,
        previous_state=previous_state,new_state=new_state,
        attempt_id=await _resolve_reanswer_attempt(session,item,attempt_id))
    session.add(record)
    item.interval_days=days; item.repetitions=streak; item.last_rating=rating
    item.state=new_state; item.last_reviewed_at=now; item.next_review_at=next_at
    await session.flush(); await session.refresh(record); await session.refresh(item); return item,record
