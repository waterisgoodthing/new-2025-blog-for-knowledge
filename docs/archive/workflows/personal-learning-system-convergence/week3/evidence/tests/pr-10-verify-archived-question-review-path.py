"""PR-10 verification repro: does the review path exclude archived Questions?

Design D7 says "Archived Question/Mistake and inactive KP do not participate in
v1 statistics". The attempt path filters Question.status='active'; the review
path joins Mistake->ReviewItem->ReviewRecord and only filters Mistake.status.
This script characterises the current behaviour for an ACTIVE mistake whose
Question is ARCHIVED.

Run via the Week 3 guard:

    python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr10_verify \
        -- backend/.venv/bin/python docs/workflows/personal-learning-system-convergence/week3/evidence/tests/pr-10-verify-archived-question-review-path.py
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "backend")

from app.database import async_session, engine  # noqa: E402
from app.models.mistake import Mistake  # noqa: E402
from app.models.question import DraftItem, Question  # noqa: E402
from app.models.review_item import ReviewItem, ReviewRecord  # noqa: E402
from app.models.taxonomy import KnowledgePointLink  # noqa: E402
from app.schemas.question import QuestionDraftCreate  # noqa: E402
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate  # noqa: E402
from app.services.draft_service import (  # noqa: E402
    convert_question_draft,
    create_question_draft,
)
from app.services.kp_analytics_service import (  # noqa: E402
    get_knowledge_point_analytics,
)
from app.services.taxonomy_service import (  # noqa: E402
    create_knowledge_point,
    create_subject,
)

NOW = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)


async def main() -> None:
    await engine.dispose(close=False)
    async with async_session() as session:
        async with session.begin():
            subject = await create_subject(
                session, SubjectCreate(name=f"arch-q-{uuid.uuid4().hex[:8]}")
            )
            kp = await create_knowledge_point(
                session,
                KnowledgePointCreate(subject_id=subject.id, name=f"kp-{uuid.uuid4().hex[:8]}"),
            )
            draft = await create_question_draft(
                session,
                QuestionDraftCreate(
                    subject_id=subject.id,
                    question_text="archived question?",
                    question_type="short_answer",
                    correct_answer="a",
                    knowledge_point_ids=[kp.id],
                ),
            )
            question = await convert_question_draft(session, draft.item.id, version=1)
            stored = await session.get(Question, question.id)
            stored.status = "archived"

            item = DraftItem(
                draft_type="mistake",
                source_type="question",
                source_id=str(question.id),
                status="pending",
            )
            session.add(item)
            await session.flush()
            mistake = Mistake(
                source_draft_item_id=item.id,
                question_id=question.id,
                subject_id=subject.id,
                question_text="active mistake on archived question",
                reason_category="concept",
                status="active",
            )
            session.add(mistake)
            await session.flush()
            session.add(
                KnowledgePointLink(
                    knowledge_point_id=kp.id,
                    target_type="mistake",
                    target_id=str(mistake.id),
                )
            )
            review_item = ReviewItem(
                target_type="mistake",
                target_id=str(mistake.id),
                mistake_id=mistake.id,
                state="active",
                interval_days=0,
                repetitions=0,
                next_review_at=NOW - timedelta(days=1),
            )
            session.add(review_item)
            await session.flush()
            for idx, rating in enumerate((1, 2, 5)):
                session.add(
                    ReviewRecord(
                        review_item_id=review_item.id,
                        rating=rating,
                        reviewed_at=NOW - timedelta(hours=idx + 1),
                        previous_interval_days=0,
                        next_interval_days=1,
                        previous_next_review_at=NOW - timedelta(days=2),
                        next_review_at=NOW + timedelta(days=1),
                    )
                )
            await session.flush()

            rows = await get_knowledge_point_analytics(session, now=NOW)
            row = next(r for r in rows if r.knowledge_point_id == kp.id)
            print(
                "archived-question / active-mistake review path -> "
                f"review_count={row.review_count} due_count={row.due_count} "
                f"lapse_count={row.lapse_count} attempt_count={row.attempt_count}"
            )
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
