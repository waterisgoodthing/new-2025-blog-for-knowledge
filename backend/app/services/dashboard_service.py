from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import String, cast, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.mistake import Mistake
from app.models.question import Question
from app.models.review_item import ReviewItem, ReviewRecord
from app.models.taxonomy import KnowledgePoint
from app.schemas.dashboard import (
    DashboardCounts,
    DashboardMistakeActivity,
    DashboardQuestionActivity,
    DashboardRecentlyMasteredItem,
    DashboardReviewActivity,
    DashboardSectionAction,
    DashboardSectionActions,
    DashboardSections,
    DashboardSummary,
    DashboardSystemStatus,
    DashboardTodayFirstAction,
    DashboardWeakKnowledgePoint,
)
from app.services import kp_analytics_service, practice_service

REVIEW_TARGET_ROUTE = "/manage/review"
PRACTICE_TARGET_ROUTE = "/manage/practice"

REVIEW_REASON_DUE = "due_reviews_pending"
REVIEW_REASON_NONE_DUE = "no_due_reviews"
REVIEW_REASON_UNAVAILABLE = "review_data_unavailable"

PRACTICE_REASON_AVAILABLE = "practice_available"
PRACTICE_REASON_NONE_ELIGIBLE = "no_eligible_practice"
PRACTICE_REASON_UNAVAILABLE = "practice_data_unavailable"

FIRST_ACTION_REASON_REVIEW_FIRST = "due_reviews_first"
FIRST_ACTION_REASON_PRACTICE_FIRST = "practice_first_no_due_reviews"
FIRST_ACTION_REASON_NOTHING = "nothing_scheduled"

WEAK_TOP_N = 3
RECENTLY_MASTERED_LIMIT = 4


def map_database_health(learning_status: str, activity_status: str) -> str:
    return "unavailable" if "unavailable" in {learning_status, activity_status} else "ok"


def map_storage_health(storage_status: str) -> str:
    return "unknown" if storage_status == "unknown" else "ok"


def build_review_action(count: int, *, available: bool) -> DashboardSectionAction:
    if not available:
        reason = REVIEW_REASON_UNAVAILABLE
    elif count > 0:
        reason = REVIEW_REASON_DUE
    else:
        reason = REVIEW_REASON_NONE_DUE
    return DashboardSectionAction(
        section="review",
        count=count,
        available=available,
        target_route=REVIEW_TARGET_ROUTE,
        reason=reason,
    )


def build_practice_action(count: int, *, available: bool) -> DashboardSectionAction:
    if not available:
        reason = PRACTICE_REASON_UNAVAILABLE
    elif count > 0:
        reason = PRACTICE_REASON_AVAILABLE
    else:
        reason = PRACTICE_REASON_NONE_ELIGIBLE
    return DashboardSectionAction(
        section="practice",
        count=count,
        available=available,
        target_route=PRACTICE_TARGET_ROUTE,
        reason=reason,
    )


def derive_today_first_action(
    review_action: DashboardSectionAction,
    practice_action: DashboardSectionAction,
) -> DashboardTodayFirstAction:
    """Deterministic fallback only: review first, then practice, else nothing.

    No AI or generated recommendation feeds this value; it is derived purely
    from the canonical review/practice counts above.
    """
    if review_action.count > 0:
        return DashboardTodayFirstAction(
            kind="review",
            count=review_action.count,
            target_route=REVIEW_TARGET_ROUTE,
            reason=FIRST_ACTION_REASON_REVIEW_FIRST,
        )
    if practice_action.count > 0:
        return DashboardTodayFirstAction(
            kind="practice",
            count=practice_action.count,
            target_route=PRACTICE_TARGET_ROUTE,
            reason=FIRST_ACTION_REASON_PRACTICE_FIRST,
        )
    return DashboardTodayFirstAction(
        kind="none",
        count=0,
        target_route=None,
        reason=FIRST_ACTION_REASON_NOTHING,
    )


async def load_weak_top3(
    session: AsyncSession,
    *,
    now: datetime,
) -> list[DashboardWeakKnowledgePoint]:
    """Top-N of the authoritative PR-10 ordering, enriched with KP names."""
    ranked = await kp_analytics_service.get_knowledge_point_analytics(session, now=now)
    top = ranked[:WEAK_TOP_N]
    if not top:
        return []
    ids = [item.knowledge_point_id for item in top]
    name_rows = (
        await session.execute(
            select(KnowledgePoint.id, KnowledgePoint.name).where(KnowledgePoint.id.in_(ids))
        )
    ).all()
    names = {int(row[0]): row[1] for row in name_rows}
    return [
        DashboardWeakKnowledgePoint(
            knowledge_point_id=item.knowledge_point_id,
            name=names.get(item.knowledge_point_id, ""),
            attempt_count=item.attempt_count,
            wrong_rate=item.wrong_rate,
            lapse_count=item.lapse_count,
            due_count=item.due_count,
        )
        for item in top
    ]


async def load_recently_mastered(
    session: AsyncSession,
    *,
    limit: int = RECENTLY_MASTERED_LIMIT,
) -> list[DashboardRecentlyMasteredItem]:
    """Distinct ReviewItems whose latest ReviewRecord set ``new_state=mastered``.

    A ReviewItem qualifies only when its single most recent ReviewRecord is a
    mastery transition (``new_state == 'mastered'``) *and* the item's current
    state is still ``mastered``. Ordering is ``reviewed_at DESC`` then item ID
    ASC, limited to ``limit``.
    """
    latest_record = (
        select(
            ReviewRecord.review_item_id.label("review_item_id"),
            ReviewRecord.reviewed_at.label("reviewed_at"),
            ReviewRecord.new_state.label("new_state"),
            func.row_number()
            .over(
                partition_by=ReviewRecord.review_item_id,
                order_by=(ReviewRecord.reviewed_at.desc(), ReviewRecord.id.desc()),
            )
            .label("rn"),
        )
        .subquery()
    )
    rows = (
        await session.execute(
            select(
                ReviewItem.id,
                ReviewItem.mistake_id,
                Mistake.question_text,
                latest_record.c.reviewed_at,
            )
            .join(latest_record, latest_record.c.review_item_id == ReviewItem.id)
            .join(Mistake, Mistake.id == ReviewItem.mistake_id)
            .where(
                latest_record.c.rn == 1,
                latest_record.c.new_state == "mastered",
                ReviewItem.state == "mastered",
            )
            .order_by(latest_record.c.reviewed_at.desc(), ReviewItem.id)
            .limit(limit)
        )
    ).all()
    return [
        DashboardRecentlyMasteredItem(
            review_item_id=review_item_id,
            mistake_id=mistake_id,
            question_text=question_text,
            mastered_at=reviewed_at,
        )
        for review_item_id, mistake_id, question_text, reviewed_at in rows
    ]


async def get_dashboard_summary(
    session: AsyncSession,
    *,
    upload_root: Path,
    now: datetime | None = None,
) -> DashboardSummary:
    generated_at = now or datetime.now(timezone.utc)
    learning_status = "ready"
    activity_status = "ready"
    storage_status = "ready" if upload_root.is_dir() else "unknown"
    try:
        counts_row = (
            await session.execute(
                select(
                    select(func.count()).select_from(Question).where(Question.status == "active").scalar_subquery().label("questions"),
                    select(func.count()).select_from(Mistake).where(Mistake.status == "active").scalar_subquery().label("mistakes"),
                    select(func.count()).select_from(KnowledgePoint).where(KnowledgePoint.status == "active").scalar_subquery().label("knowledge_points"),
                    select(func.count()).select_from(ReviewItem).where(ReviewItem.state == "active", ReviewItem.next_review_at <= generated_at).scalar_subquery().label("due_reviews"),
                )
            )
        ).one()
        counts = DashboardCounts(**counts_row._mapping, attachments=0)
    except SQLAlchemyError:
        await session.rollback()
        learning_status = "unavailable"
        counts = DashboardCounts(questions=0, mistakes=0, knowledge_points=0, attachments=0, due_reviews=0)

    try:
        attachment_count = await session.scalar(select(func.count()).select_from(Attachment).where(Attachment.status == "active"))
        counts.attachments = int(attachment_count or 0)
        if storage_status == "ready" and counts.attachments == 0:
            storage_status = "empty"
    except SQLAlchemyError:
        await session.rollback()
        storage_status = "unknown"

    questions: list[Question] = []
    mistakes: list[Mistake] = []
    review_rows: list[tuple[ReviewRecord, str]] = []
    try:
        questions = list((await session.execute(select(Question).where(Question.status == "active").order_by(Question.updated_at.desc(), Question.id).limit(5))).scalars().all())
        mistakes = list((await session.execute(select(Mistake).where(Mistake.status == "active").order_by(Mistake.updated_at.desc(), Mistake.id).limit(5))).scalars().all())
        review_rows = (await session.execute(select(ReviewRecord, Mistake.question_text).join(ReviewItem, ReviewItem.id == ReviewRecord.review_item_id).join(Mistake, ReviewItem.target_id == cast(Mistake.id, String)).order_by(ReviewRecord.reviewed_at.desc(), ReviewRecord.id).limit(5))).all()
    except SQLAlchemyError:
        await session.rollback()
        activity_status = "unavailable"

    if learning_status == "ready" and not any((counts.questions, counts.mistakes, counts.knowledge_points, counts.due_reviews)):
        learning_status = "empty"
    if activity_status == "ready" and not (questions or mistakes or review_rows):
        activity_status = "empty"

    review_available = learning_status != "unavailable"
    review_today_count = counts.due_reviews if review_available else 0

    try:
        practice = await practice_service.get_daily_practice(session, now=generated_at)
        practice_available = True
        practice_today_count = len(practice.items)
    except SQLAlchemyError:
        await session.rollback()
        practice_available = False
        practice_today_count = 0

    try:
        weak_top3 = await load_weak_top3(session, now=generated_at)
    except SQLAlchemyError:
        await session.rollback()
        weak_top3 = []

    try:
        recently_mastered_4 = await load_recently_mastered(session)
    except SQLAlchemyError:
        await session.rollback()
        recently_mastered_4 = []

    review_action = build_review_action(review_today_count, available=review_available)
    practice_action = build_practice_action(practice_today_count, available=practice_available)

    return DashboardSummary(
        generated_at=generated_at,
        counts=counts,
        recent_questions=[
            DashboardQuestionActivity(
                id=question.id,
                title=question.title,
                question_text=question.question_text,
                updated_at=question.updated_at,
            )
            for question in questions
        ],
        recent_mistakes=[
            DashboardMistakeActivity(
                id=mistake.id,
                title=mistake.title,
                question_text=mistake.question_text,
                reason_category=mistake.reason_category,
                updated_at=mistake.updated_at,
            )
            for mistake in mistakes
        ],
        recent_reviews=[
            DashboardReviewActivity(
                id=record.id,
                review_item_id=record.review_item_id,
                rating=record.rating,
                reviewed_at=record.reviewed_at,
                question_text=question_text,
            )
            for record, question_text in review_rows
        ],
        sections=DashboardSections(learning=learning_status, activity=activity_status, storage=storage_status),
        system=DashboardSystemStatus(
            service="ok",
            database=map_database_health(learning_status, activity_status),
            storage=map_storage_health(storage_status),
        ),
        review_today_count=review_today_count,
        practice_today_count=practice_today_count,
        weak_top3=weak_top3,
        recently_mastered_4=recently_mastered_4,
        today_first_action=derive_today_first_action(review_action, practice_action),
        section_actions=DashboardSectionActions(review=review_action, practice=practice_action),
    )
