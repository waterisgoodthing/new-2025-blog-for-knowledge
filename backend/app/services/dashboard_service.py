from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import String, cast, func, select
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
    DashboardReviewActivity,
    DashboardSummary,
    DashboardSystemStatus,
)


async def get_dashboard_summary(
    session: AsyncSession,
    *,
    upload_root: Path,
    now: datetime | None = None,
) -> DashboardSummary:
    generated_at = now or datetime.now(timezone.utc)
    counts_row = (
        await session.execute(
            select(
                select(func.count())
                .select_from(Question)
                .where(Question.status == "active")
                .scalar_subquery()
                .label("questions"),
                select(func.count())
                .select_from(Mistake)
                .where(Mistake.status == "active")
                .scalar_subquery()
                .label("mistakes"),
                select(func.count())
                .select_from(KnowledgePoint)
                .where(KnowledgePoint.status == "active")
                .scalar_subquery()
                .label("knowledge_points"),
                select(func.count())
                .select_from(Attachment)
                .where(Attachment.status == "active")
                .scalar_subquery()
                .label("attachments"),
                select(func.count())
                .select_from(ReviewItem)
                .where(
                    ReviewItem.state == "active",
                    ReviewItem.next_review_at <= generated_at,
                )
                .scalar_subquery()
                .label("due_reviews"),
            )
        )
    ).one()

    questions = list(
        (
            await session.execute(
                select(Question)
                .where(Question.status == "active")
                .order_by(Question.updated_at.desc(), Question.id)
                .limit(5)
            )
        )
        .scalars()
        .all()
    )
    mistakes = list(
        (
            await session.execute(
                select(Mistake)
                .where(Mistake.status == "active")
                .order_by(Mistake.updated_at.desc(), Mistake.id)
                .limit(5)
            )
        )
        .scalars()
        .all()
    )
    review_rows = (
        await session.execute(
            select(ReviewRecord, Mistake.question_text)
            .join(ReviewItem, ReviewItem.id == ReviewRecord.review_item_id)
            .join(Mistake, ReviewItem.target_id == cast(Mistake.id, String))
            .order_by(ReviewRecord.reviewed_at.desc(), ReviewRecord.id)
            .limit(5)
        )
    ).all()

    return DashboardSummary(
        generated_at=generated_at,
        counts=DashboardCounts(**counts_row._mapping),
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
        system=DashboardSystemStatus(
            service="ok",
            database="ok",
            storage="ok" if upload_root.is_dir() else "unknown",
        ),
    )
