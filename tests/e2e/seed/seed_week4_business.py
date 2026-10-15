#!/usr/bin/env python3
"""Deterministic, idempotent business seed for Week 4 R22b E2E (F04).

Provisions exactly the entities the R22b business flows need, in a
``astra_week4_*`` scratch database only:

- admin ``ci-admin`` (via ``app.cli.bootstrap_temp_admin``);
- one Subject + KnowledgePoint;
- one active ``short_answer`` Question whose ``answer_data.value`` makes
  verdicts deterministic (correct answer ``3``);
- one converted Mistake (question link) whose ReviewItem is reset to the
  *due* state on every run, so E2E-04 can always re-answer and record.

It is re-runnable: existing rows are reused by stable identity keys, nothing
is duplicated except the MistakeDrafts that E2E-03 itself creates per run.
The script refuses any non-scratch / non-local database before connecting and
prints a single ``E2E_SEED_RESULT={...}`` JSON line on stdout for the
Playwright globalSetup to consume.

Run under the backend interpreter with the backend package importable:

    PYTHONPATH=backend backend/.venv/bin/python tests/e2e/seed/seed_week4_business.py
"""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.cli import bootstrap_temp_admin
from app.config import get_settings
from app.models.mistake import Mistake, MistakeDraft
from app.models.note import Subject
from app.models.question import DraftItem, Question, QuestionKnowledgePoint
from app.models.review_item import ReviewItem
from app.models.taxonomy import KnowledgePoint
from app.schemas.mistake import MistakeDraftCreate
from app.services import mistake_service
from app.utils.scratch_db_safety import require_scratch_database

ADMIN_USERNAME = "ci-admin"
ADMIN_PASSWORD = "ci-test-admin-password"
SUBJECT_NAME = "E2E 业务闭环"
KNOWLEDGE_POINT_NAME = "E2E-04 复习知识点"
QUESTION_TITLE = "E2E-W4-BUSINESS-Q"
# Stable, unique marker the specs discover through the admin API.
QUESTION_TEXT = "E2E-W4-REVIEW-Q 固定间隔复习 v2：连续成功第 1 次应推进到几天？"
CORRECT_ANSWER = "3"
EXPLANATION = "fixed_interval_v2 成功阶梯：1->3, 2->7, 3->14, 4->30。"
SEED_MARKER = "E2E-W4-BUSINESS"


async def _find_or_create_subject(session: AsyncSession) -> Subject:
    subject = (
        await session.execute(select(Subject).where(Subject.name == SUBJECT_NAME))
    ).scalar_one_or_none()
    if subject is None:
        subject = Subject(name=SUBJECT_NAME, status="active", sort_order=0)
        session.add(subject)
        await session.flush()
    return subject


async def _find_or_create_knowledge_point(
    session: AsyncSession, subject: Subject
) -> KnowledgePoint:
    kp = (
        await session.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.subject_id == subject.id,
                KnowledgePoint.name == KNOWLEDGE_POINT_NAME,
                KnowledgePoint.parent_id.is_(None),
            )
        )
    ).scalar_one_or_none()
    if kp is None:
        kp = KnowledgePoint(
            subject_id=subject.id,
            name=KNOWLEDGE_POINT_NAME,
            description=f"{SEED_MARKER} knowledge point",
            status="active",
            sort_order=0,
        )
        session.add(kp)
        await session.flush()
    return kp


async def _find_or_create_question(
    session: AsyncSession, subject: Subject, kp: KnowledgePoint
) -> Question:
    question = (
        await session.execute(select(Question).where(Question.title == QUESTION_TITLE))
    ).scalars().first()
    if question is None:
        question = Question(
            subject_id=subject.id,
            title=QUESTION_TITLE,
            stem_md="",
            question_text=QUESTION_TEXT,
            question_type="short_answer",
            options=[],
            answer_data={"kind": "short_answer", "value": CORRECT_ANSWER},
            correct_answer=CORRECT_ANSWER,
            analysis_md=EXPLANATION,
            explanation=EXPLANATION,
            difficulty="easy",
            status="active",
            visibility="private",
            version=1,
        )
        session.add(question)
        await session.flush()
    else:
        # Re-pin canonical fields so a rerun after a test mutation converges.
        question.subject_id = subject.id
        question.question_text = QUESTION_TEXT
        question.question_type = "short_answer"
        question.options = []
        question.answer_data = {"kind": "short_answer", "value": CORRECT_ANSWER}
        question.correct_answer = CORRECT_ANSWER
        question.status = "active"
        await session.flush()

    link = await session.get(QuestionKnowledgePoint, (question.id, kp.id))
    if link is None:
        session.add(
            QuestionKnowledgePoint(
                question_id=question.id,
                knowledge_point_id=kp.id,
                role="primary",
                sort_order=0,
            )
        )
        await session.flush()
    return question


async def _ensure_mistake(
    session: AsyncSession, question: Question, created_by: uuid.UUID
) -> Mistake:
    """Return the canonical Mistake for the seeded question (create if absent)."""
    existing = (
        await session.execute(
            select(MistakeDraft, DraftItem)
            .join(DraftItem, DraftItem.id == MistakeDraft.draft_item_id)
            .where(
                DraftItem.draft_type == "mistake",
                DraftItem.status == "converted",
                MistakeDraft.question_id == question.id,
            )
        )
    ).first()
    if existing is not None:
        draft, item = existing
        mistake = await session.get(Mistake, uuid.UUID(item.target_id)) if item.target_id else None
        if mistake is not None:
            return mistake

    record = await mistake_service.create_mistake_draft(
        session,
        MistakeDraftCreate(
            question_id=question.id,
            my_answer="seed",
            reason_category="unknown",
            mistake_reason=f"{SEED_MARKER} seed mistake",
        ),
        created_by=created_by,
    )
    converted = await mistake_service.convert_mistake_draft(
        session, record.item.id, record.item.version
    )
    mistake = await session.get(Mistake, converted.mistake.id)
    assert mistake is not None
    return mistake


async def _reset_review_item(session: AsyncSession, mistake: Mistake) -> ReviewItem:
    item = (
        await session.execute(
            select(ReviewItem).where(ReviewItem.target_id == str(mistake.id))
        )
    ).scalar_one()
    item.state = "active"
    item.interval_days = 0
    item.repetitions = 0
    item.next_review_at = datetime.now(timezone.utc)
    item.last_reviewed_at = None
    item.last_rating = None
    await session.flush()
    return item


async def _seed() -> dict[str, object]:
    settings = get_settings()
    require_scratch_database(settings.DATABASE_URL)

    engine = create_async_engine(settings.DATABASE_URL)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with factory() as session:
            admin = await bootstrap_temp_admin(
                session, username=ADMIN_USERNAME, password=ADMIN_PASSWORD
            )
            subject = await _find_or_create_subject(session)
            kp = await _find_or_create_knowledge_point(session, subject)
            question = await _find_or_create_question(session, subject, kp)
            mistake = await _ensure_mistake(session, question, admin.user.id)
            review_item = await _reset_review_item(session, mistake)
            await session.commit()
            return {
                "marker": SEED_MARKER,
                "admin_username": ADMIN_USERNAME,
                "subject_id": subject.id,
                "knowledge_point_id": kp.id,
                "question_id": str(question.id),
                "question_title": QUESTION_TITLE,
                "question_text": QUESTION_TEXT,
                "correct_answer": CORRECT_ANSWER,
                "mistake_id": str(mistake.id),
                "review_item_id": str(review_item.id),
            }
    finally:
        await engine.dispose()


def main() -> int:
    try:
        result = asyncio.run(_seed())
    except Exception as error:  # noqa: BLE001 - surface any seed failure to CI
        print(f"E2E_SEED_ERROR={type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print("E2E_SEED_RESULT=" + json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
