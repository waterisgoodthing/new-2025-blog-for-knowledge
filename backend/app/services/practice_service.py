"""Deterministic daily-practice selection (W3-D05, PR-13).

Selection pipeline (read-only, no Attempt is ever created):

1. Rank knowledge points by the authoritative PR-10 weakness ordering
   (:func:`app.services.kp_analytics_service.get_knowledge_point_analytics`);
   this service never defines its own weighting.
2. Build the candidate set from ``active`` Questions linked through
   ``QuestionKnowledgePoint`` to ``active`` KnowledgePoints.
3. Exclude any Question that has a ``practice`` Attempt inside the rolling
   window (previous ``PRACTICE_WINDOW_HOURS`` hours, default 7x24).
4. Exclude any Question whose linked canonical Mistake has a ReviewItem that is
   currently ``mastered``.
5. Order candidates by (weakness rank, knowledge_point_id, question_id) and
   take ``target`` items: 3 when at least 3 eligible candidates exist, otherwise
   the actual eligible count, capped at ``PRACTICE_MAX_ITEMS``.

The DTO never carries ``answer_data``/``correct_answer``/``analysis``/``explanation``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.question import Question, QuestionKnowledgePoint
from app.models.review_item import ReviewItem
from app.models.taxonomy import KnowledgePoint
from app.schemas.kp_analytics import KnowledgePointAnalyticsItem
from app.schemas.practice import PracticeEmptyMetadata, PracticeItem, PracticeTodayResponse
from app.services.kp_analytics_service import get_knowledge_point_analytics

PRACTICE_WINDOW_HOURS: int = 7 * 24
PRACTICE_TARGET_COUNT: int = 3
PRACTICE_MAX_ITEMS: int = 10

SELECTION_REASON_WRONG_RATE = "weak_kp_wrong_rate"
SELECTION_REASON_LAPSE = "weak_kp_lapse"
SELECTION_REASON_DUE = "weak_kp_due"
SELECTION_REASON_STABLE_FALLBACK = "stable_order_fallback"

EMPTY_REASON_RETURNED = "candidates_returned"
EMPTY_REASON_NO_CANDIDATES = "no_eligible_candidates"
EMPTY_REASON_ALL_EXCLUDED = "all_candidates_excluded"


def practice_target_count(eligible_count: int) -> int:
    """Return the number of items to emit for ``eligible_count`` candidates."""
    if eligible_count < 0:
        raise ValueError(f"eligible_count must be >= 0, got {eligible_count!r}")
    if eligible_count >= PRACTICE_TARGET_COUNT:
        return min(PRACTICE_TARGET_COUNT, PRACTICE_MAX_ITEMS)
    return min(eligible_count, PRACTICE_MAX_ITEMS)


def selection_reason_for(item: KnowledgePointAnalyticsItem | None) -> str:
    """Explain deterministically why a knowledge point was prioritised."""
    if item is None:
        return SELECTION_REASON_STABLE_FALLBACK
    if item.wrong_rate > 0:
        return SELECTION_REASON_WRONG_RATE
    if item.lapse_count > 0:
        return SELECTION_REASON_LAPSE
    if item.due_count > 0:
        return SELECTION_REASON_DUE
    return SELECTION_REASON_STABLE_FALLBACK


def _best_knowledge_point(
    knowledge_point_ids: set[int],
    rank_by_kp: dict[int, int],
) -> int:
    """Pick the weakest linked KP: lowest rank, then lowest id (stable tie)."""
    fallback_rank = len(rank_by_kp)
    return min(
        knowledge_point_ids,
        key=lambda kp_id: (rank_by_kp.get(kp_id, fallback_rank + kp_id), kp_id),
    )


async def get_daily_practice(
    session: AsyncSession,
    *,
    now: datetime | None = None,
) -> PracticeTodayResponse:
    generated_at = now or datetime.now(timezone.utc)
    window_start = generated_at - timedelta(hours=PRACTICE_WINDOW_HOURS)

    ranked = await get_knowledge_point_analytics(session, now=generated_at)
    rank_by_kp = {item.knowledge_point_id: index for index, item in enumerate(ranked)}
    metrics_by_kp = {item.knowledge_point_id: item for item in ranked}

    pair_rows = (
        await session.execute(
            select(
                QuestionKnowledgePoint.question_id,
                QuestionKnowledgePoint.knowledge_point_id,
            )
            .join(Question, Question.id == QuestionKnowledgePoint.question_id)
            .join(
                KnowledgePoint,
                KnowledgePoint.id == QuestionKnowledgePoint.knowledge_point_id,
            )
            .where(Question.status == "active", KnowledgePoint.status == "active")
        )
    ).all()
    question_kps: dict[uuid.UUID, set[int]] = {}
    for question_id, knowledge_point_id in pair_rows:
        question_kps.setdefault(question_id, set()).add(int(knowledge_point_id))
    raw_candidate_count = len(question_kps)

    recent_ids = set(
        (
            await session.execute(
                select(Attempt.question_id)
                .where(
                    Attempt.context_type == "practice",
                    Attempt.submitted_at >= window_start,
                    Attempt.submitted_at <= generated_at,
                )
                .distinct()
            )
        )
        .scalars()
        .all()
    )

    mastered_ids = set(
        (
            await session.execute(
                select(Mistake.question_id)
                .join(ReviewItem, ReviewItem.mistake_id == Mistake.id)
                .where(ReviewItem.state == "mastered")
                .distinct()
            )
        )
        .scalars()
        .all()
    )

    recent_excluded_count = sum(1 for q in question_kps if q in recent_ids)
    mastered_excluded_count = sum(
        1 for q in question_kps if q not in recent_ids and q in mastered_ids
    )

    best_kp_by_question: dict[uuid.UUID, int] = {}
    for question_id, kp_ids in question_kps.items():
        if question_id in recent_ids or question_id in mastered_ids:
            continue
        best_kp_by_question[question_id] = _best_knowledge_point(kp_ids, rank_by_kp)

    eligible_count = len(best_kp_by_question)
    fallback_rank = len(rank_by_kp)
    ordered = sorted(
        best_kp_by_question.items(),
        key=lambda pair: (
            rank_by_kp.get(pair[1], fallback_rank + pair[1]),
            pair[1],
            str(pair[0]),
        ),
    )
    target = practice_target_count(eligible_count)
    selected = ordered[:target]

    items = [
        PracticeItem(
            question_id=str(question_id),
            knowledge_point_id=knowledge_point_id,
            selection_reason=selection_reason_for(metrics_by_kp.get(knowledge_point_id)),
        )
        for question_id, knowledge_point_id in selected
    ]

    if items:
        reason = EMPTY_REASON_RETURNED
    elif raw_candidate_count == 0:
        reason = EMPTY_REASON_NO_CANDIDATES
    else:
        reason = EMPTY_REASON_ALL_EXCLUDED

    empty_metadata = PracticeEmptyMetadata(
        reason=reason,
        raw_candidate_count=raw_candidate_count,
        recent_attempt_excluded_count=recent_excluded_count,
        mastered_excluded_count=mastered_excluded_count,
        eligible_candidate_count=eligible_count,
        target_count=target,
        returned_count=len(items),
        window_hours=PRACTICE_WINDOW_HOURS,
    )
    return PracticeTodayResponse(items=items, empty_metadata=empty_metadata)
