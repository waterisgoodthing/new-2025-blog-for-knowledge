from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, and_, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.question import Question, QuestionKnowledgePoint
from app.models.review_item import ReviewItem, ReviewRecord
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.kp_analytics import KnowledgePointAnalyticsItem

KP_ANALYTICS_SORT_KEY: tuple[str, ...] = (
    "-wrong_rate",
    "-lapse_count",
    "-due_count",
    "knowledge_point_id",
)


def compute_attempt_rates(graded_attempts: int, wrong_count: int) -> tuple[float, float]:
    if graded_attempts < 0:
        raise ValueError(f"graded_attempts must be >= 0, got {graded_attempts!r}")
    if not 0 <= wrong_count <= graded_attempts:
        raise ValueError(
            "wrong_count must satisfy 0 <= wrong_count <= graded_attempts, "
            f"got wrong_count={wrong_count!r}, graded_attempts={graded_attempts!r}"
        )
    if graded_attempts == 0:
        return 0.0, 0.0
    return (graded_attempts - wrong_count) / graded_attempts, wrong_count / graded_attempts


def kp_analytics_sort_key(
    item: KnowledgePointAnalyticsItem,
) -> tuple[float, int, int, int]:
    return (
        -item.wrong_rate,
        -item.lapse_count,
        -item.due_count,
        item.knowledge_point_id,
    )


async def get_knowledge_point_analytics(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> list[KnowledgePointAnalyticsItem]:
    generated_at = now or datetime.now(timezone.utc)

    kp_base = (
        select(KnowledgePoint.id.label("knowledge_point_id"))
        .where(KnowledgePoint.status == "active")
        .subquery()
    )

    attempt_agg = (
        select(
            QuestionKnowledgePoint.knowledge_point_id.label("knowledge_point_id"),
            func.count(Attempt.id).label("attempt_count"),
            func.count().filter(Attempt.is_correct.is_(False)).label("wrong_count"),
        )
        .join(Attempt, Attempt.question_id == QuestionKnowledgePoint.question_id)
        .join(Question, Question.id == QuestionKnowledgePoint.question_id)
        .where(Attempt.context_type == "practice", Question.status == "active")
        .group_by(QuestionKnowledgePoint.knowledge_point_id)
        .subquery()
    )

    review_link = (
        select(
            KnowledgePointLink.knowledge_point_id.label("knowledge_point_id"),
            ReviewItem.id.label("review_item_id"),
            ReviewItem.state.label("review_item_state"),
            ReviewItem.next_review_at.label("next_review_at"),
            ReviewRecord.id.label("review_record_id"),
            ReviewRecord.rating.label("rating"),
        )
        .select_from(KnowledgePointLink)
        .join(
            Mistake,
            and_(
                KnowledgePointLink.target_type == "mistake",
                KnowledgePointLink.target_id == cast(Mistake.id, String),
            ),
        )
        .join(ReviewItem, ReviewItem.mistake_id == Mistake.id)
        .join(Question, Question.id == Mistake.question_id)
        .join(ReviewRecord, ReviewRecord.review_item_id == ReviewItem.id, isouter=True)
        .where(Mistake.status == "active", Question.status == "active")
        .cte()
    )

    review_agg = (
        select(
            review_link.c.knowledge_point_id.label("knowledge_point_id"),
            func.count(review_link.c.review_record_id).label("review_count"),
            func.count()
            .filter(
                and_(
                    review_link.c.review_record_id.isnot(None),
                    review_link.c.rating <= 2,
                )
            )
            .label("lapse_count"),
        )
        .group_by(review_link.c.knowledge_point_id)
        .subquery()
    )

    due_agg = (
        select(
            review_link.c.knowledge_point_id.label("knowledge_point_id"),
            func.count(func.distinct(review_link.c.review_item_id)).label("due_count"),
        )
        .where(
            review_link.c.review_item_state == "active",
            review_link.c.next_review_at <= generated_at,
        )
        .group_by(review_link.c.knowledge_point_id)
        .subquery()
    )

    stmt = (
        select(
            kp_base.c.knowledge_point_id,
            func.coalesce(attempt_agg.c.attempt_count, 0).label("attempt_count"),
            func.coalesce(attempt_agg.c.wrong_count, 0).label("wrong_count"),
            func.coalesce(review_agg.c.review_count, 0).label("review_count"),
            func.coalesce(due_agg.c.due_count, 0).label("due_count"),
            func.coalesce(review_agg.c.lapse_count, 0).label("lapse_count"),
        )
        .select_from(kp_base)
        .outerjoin(
            attempt_agg,
            attempt_agg.c.knowledge_point_id == kp_base.c.knowledge_point_id,
        )
        .outerjoin(
            review_agg,
            review_agg.c.knowledge_point_id == kp_base.c.knowledge_point_id,
        )
        .outerjoin(
            due_agg,
            due_agg.c.knowledge_point_id == kp_base.c.knowledge_point_id,
        )
    )

    rows = (await session.execute(stmt)).all()
    items: list[KnowledgePointAnalyticsItem] = []
    for knowledge_point_id, attempt_count, wrong_count, review_count, due_count, lapse_count in rows:
        accuracy, wrong_rate = compute_attempt_rates(int(attempt_count), int(wrong_count))
        items.append(
            KnowledgePointAnalyticsItem(
                knowledge_point_id=int(knowledge_point_id),
                attempt_count=int(attempt_count),
                wrong_count=int(wrong_count),
                review_count=int(review_count),
                due_count=int(due_count),
                accuracy=accuracy,
                wrong_rate=wrong_rate,
                lapse_count=int(lapse_count),
            )
        )
    items.sort(key=kp_analytics_sort_key)
    return items
