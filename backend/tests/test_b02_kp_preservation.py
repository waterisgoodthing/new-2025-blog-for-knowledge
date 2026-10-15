"""B02: KP fact preservation acceptance, cross-transaction on real PostgreSQL.

The reviewer finding was that the previous F02 proof (``test_attempt_service``)
used one session/transaction and only one happy path. This file re-proves the
documented invariants with **independent sessions and commits** per stage so a
cached ORM object can never be mistaken for persisted truth:

- automatic wrong-answer drafts inherit the Question KP snapshot;
- manual explicit ``[]`` and explicit replacement are authoritative;
- editing a Question's KPs later never overwrites a confirmed Mistake;
- repeated conversion is idempotent, a version conflict creates nothing;
- review metrics (review_count / lapse_count / practice attempt exclusion) and
  Dashboard / Practice readbacks stay consistent with the fixture facts.

No product behavior is changed here; only acceptance is added.
"""

from __future__ import annotations

import asyncio
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import delete, func, select

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.models.mistake import Mistake, MistakeDraft
from app.models.note import Subject
from app.models.question import DraftItem, Question, QuestionKnowledgePoint
from app.models.review_item import ReviewItem, ReviewRecord
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.schemas.mistake import MistakeDraftCreate, MistakeDraftUpdate
from app.schemas.question import QuestionCreate, QuestionPatch
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services import attempt_service, mistake_service, question_service
from app.services.dashboard_service import get_dashboard_summary
from app.services.kp_analytics_service import get_knowledge_point_analytics
from app.services.practice_service import get_daily_practice
from app.services.reanswer_service import submit_reanswer_attempt
from app.services.review_item_service import submit_review
from app.services.taxonomy_service import create_knowledge_point, create_subject


async def _cleanup(state: dict) -> None:
    async with async_session() as session:
        if state["review_item_ids"]:
            await session.execute(
                delete(ReviewRecord).where(ReviewRecord.review_item_id.in_(state["review_item_ids"]))
            )
            await session.execute(
                delete(ReviewItem).where(ReviewItem.id.in_(state["review_item_ids"]))
            )
        if state["mistake_ids"]:
            await session.execute(delete(Mistake).where(Mistake.id.in_(state["mistake_ids"])))
        if state["draft_item_ids"]:
            await session.execute(
                delete(MistakeDraft).where(MistakeDraft.draft_item_id.in_(state["draft_item_ids"]))
            )
        if state["attempt_ids"]:
            await session.execute(delete(Attempt).where(Attempt.id.in_(state["attempt_ids"])))
        if state["draft_item_ids"]:
            await session.execute(
                delete(DraftItem).where(DraftItem.id.in_(state["draft_item_ids"]))
            )
        if state["question_ids"]:
            for question_id in state["question_ids"]:
                await session.execute(
                    delete(KnowledgePointLink).where(
                        KnowledgePointLink.target_id == str(question_id)
                    )
                )
        if state["mistake_ids"]:
            for mistake_id in state["mistake_ids"]:
                await session.execute(
                    delete(KnowledgePointLink).where(
                        KnowledgePointLink.target_id == str(mistake_id)
                    )
                )
        if state["draft_ids"]:
            for draft_id in state["draft_ids"]:
                await session.execute(
                    delete(KnowledgePointLink).where(
                        KnowledgePointLink.target_id == str(draft_id)
                    )
                )
        if state["question_ids"]:
            await session.execute(delete(Question).where(Question.id.in_(state["question_ids"])))
        if state["kp_ids"]:
            await session.execute(
                delete(KnowledgePoint).where(KnowledgePoint.id.in_(state["kp_ids"]))
            )
        if state["subject_ids"]:
            await session.execute(delete(Question).where(Question.subject_id.in_(state["subject_ids"])))
            await session.execute(delete(Subject).where(Subject.id.in_(state["subject_ids"])))
        await session.commit()


def _new_state() -> dict:
    return {
        "subject_ids": [],
        "kp_ids": [],
        "question_ids": [],
        "draft_item_ids": [],
        "draft_ids": [],
        "attempt_ids": [],
        "mistake_ids": [],
        "review_item_ids": [],
    }


async def _scenario() -> None:
    state = _new_state()
    token = uuid.uuid4().hex[:10]
    try:
        # --- Stage 0: create subject + two KPs + question in its own transaction
        async with async_session() as session:
            subject = await create_subject(session, SubjectCreate(name=f"B02 Subject {token}"))
            kp_a = await create_knowledge_point(
                session, KnowledgePointCreate(subject_id=subject.id, name=f"B02 A {token}")
            )
            kp_b = await create_knowledge_point(
                session, KnowledgePointCreate(subject_id=subject.id, name=f"B02 B {token}")
            )
            kp_c = await create_knowledge_point(
                session, KnowledgePointCreate(subject_id=subject.id, name=f"B02 C {token}")
            )
            question = await question_service.create_question(
                session,
                QuestionCreate(
                    subject_id=subject.id,
                    stem_md=f"B02 multiple choice {token}",
                    question_type="multiple_choice",
                    options=[
                        {"key": "A", "text": "a"},
                        {"key": "B", "text": "b"},
                        {"key": "C", "text": "c"},
                    ],
                    answer_data={"kind": "multiple_choice", "value": ["A", "C"]},
                    knowledge_point_links=[
                        {"knowledge_point_id": kp_a.id},
                        {"knowledge_point_id": kp_b.id},
                    ],
                ),
            )
            await session.commit()
            subject_id, question_id = subject.id, question.id
            kp_a_id, kp_b_id, kp_c_id = kp_a.id, kp_b.id, kp_c.id
            state["subject_ids"].append(subject_id)
            state["kp_ids"].extend([kp_a_id, kp_b_id, kp_c_id])
            state["question_ids"].append(question_id)

        # --- Stage 1: automatic wrong practice attempt -> draft inherits [a,b]
        async with async_session() as session:
            attempt = await attempt_service.submit_attempt(
                session, question_id, submitted_answer="A,B"
            )
            await session.commit()
            attempt_id = attempt.id
            draft_item_id = attempt.mistake_draft_item_id
            state["attempt_ids"].append(attempt_id)
            state["draft_item_ids"].append(draft_item_id)

        async with async_session() as session:
            draft = await mistake_service.get_mistake_draft(session, draft_item_id)
            assert draft.knowledge_point_ids == sorted([kp_a_id, kp_b_id]), draft.knowledge_point_ids

        # --- Stage 2: convert -> mistake keeps [a,b] (own transaction)
        async with async_session() as session:
            draft = await mistake_service.get_mistake_draft(session, draft_item_id)
            mistake = await mistake_service.convert_mistake_draft(
                session, draft_item_id, draft.item.version
            )
            await session.commit()
            mistake_id = mistake.id
            review_item_id = mistake.review_item_id
            state["mistake_ids"].append(mistake_id)
            state["draft_ids"].append(draft.id)
            state["review_item_ids"].append(review_item_id)

        async with async_session() as session:
            fresh = await mistake_service.get_mistake(session, mistake_id)
            assert fresh.knowledge_point_ids == sorted([kp_a_id, kp_b_id]), fresh.knowledge_point_ids

        # --- Stage 3: wrong re-answer + rating 0 -> review/lapse metrics
        async with async_session() as session:
            item = await session.get(ReviewItem, review_item_id)
            expected = item.next_review_at
            reattempt, evaluation = await submit_reanswer_attempt(
                session, question_id, submitted_answer="A"
            )
            assert evaluation.verdict == "incorrect"
            _, record = await submit_review(
                session,
                review_item_id,
                rating=0,
                expected_next_review_at=expected,
                attempt_id=reattempt.id,
            )
            await session.commit()
            state["attempt_ids"].append(reattempt.id)
            assert record.attempt_id == reattempt.id

        async with async_session() as session:
            analytics = {
                row.knowledge_point_id: row
                for row in await get_knowledge_point_analytics(session)
            }
            for kp_id in (kp_a_id, kp_b_id):
                row = analytics[kp_id]
                assert row.attempt_count == 1, (kp_id, row.attempt_count)  # practice only
                assert row.wrong_count == 1
                assert row.review_count == 1
                assert row.lapse_count == 1

        # --- Stage 5: controlled clock -> item becomes due again
        async with async_session() as session:
            item = await session.get(ReviewItem, review_item_id)
            item.next_review_at = datetime.now(timezone.utc) - timedelta(seconds=5)
            await session.commit()

        # --- Stage 6: correct re-answer + rating 5 -> second review record
        async with async_session() as session:
            item = await session.get(ReviewItem, review_item_id)
            expected = item.next_review_at
            reattempt, evaluation = await submit_reanswer_attempt(
                session, question_id, submitted_answer="A,C"
            )
            assert evaluation.verdict == "correct"
            _, record = await submit_review(
                session,
                review_item_id,
                rating=5,
                expected_next_review_at=expected,
                attempt_id=reattempt.id,
            )
            await session.commit()
            state["attempt_ids"].append(reattempt.id)
            assert record.attempt_id == reattempt.id

        async with async_session() as session:
            analytics = {
                row.knowledge_point_id: row
                for row in await get_knowledge_point_analytics(session)
            }
            for kp_id in (kp_a_id, kp_b_id):
                row = analytics[kp_id]
                assert row.attempt_count == 1
                assert row.review_count == 2, (kp_id, row.review_count)
                assert row.lapse_count == 1, (kp_id, row.lapse_count)

        # --- Stage 6b: edit the Question KPs to [c]; confirmed mistake is frozen
        async with async_session() as session:
            version = await session.scalar(select(Question.version).where(Question.id == question_id))
            await question_service.update_canonical_question(
                session,
                question_id,
                QuestionPatch(version=version, knowledge_point_links=[{"knowledge_point_id": kp_c_id}]),
            )
            await session.commit()

        async with async_session() as session:
            mistake_row = await mistake_service.get_mistake(session, mistake_id)
            assert mistake_row.knowledge_point_ids == sorted([kp_a_id, kp_b_id]), (
                "confirmed mistake KPs must not follow a later question edit: "
                f"{mistake_row.knowledge_point_ids}"
            )
            q_links = set(
                (
                    await session.execute(
                        select(QuestionKnowledgePoint.knowledge_point_id).where(
                            QuestionKnowledgePoint.question_id == question_id
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert q_links == {kp_c_id}, q_links

        # --- Stage 7: Dashboard / Practice readbacks match the fixture
        async with async_session() as session:
            summary = await get_dashboard_summary(session, upload_root=Path(tempfile.gettempdir()))
            assert summary.counts.mistakes >= 1
            assert any(item.id == mistake_id for item in summary.recent_mistakes)

        async with async_session() as session:
            practice = await get_daily_practice(session)
            assert practice.empty_metadata.returned_count == len(practice.items)
            for item in practice.items:
                assert not hasattr(item, "answer_data")
                assert not hasattr(item, "correct_answer")
            # a recent practice attempt on the question excludes it from practice
            assert all(str(item.question_id) != str(question_id) for item in practice.items)

        # --- Stage 8: manual path — explicit [] is authoritative; replace works
        async with async_session() as session:
            empty_draft = await mistake_service.create_mistake_draft(
                session,
                MistakeDraftCreate(question_id=question_id, knowledge_point_ids=[]),
            )
            await session.commit()
            state["draft_item_ids"].append(empty_draft.item.id)
            state["draft_ids"].append(empty_draft.id)
            assert empty_draft.knowledge_point_ids == []

        async with async_session() as session:
            replaced = await mistake_service.update_mistake_draft(
                session,
                state["draft_item_ids"][-1],
                MistakeDraftUpdate(version=1, knowledge_point_ids=[kp_c_id]),
            )
            await session.commit()
            assert replaced.knowledge_point_ids == [kp_c_id]

        # --- Stage 9: invalid / stale KP rejected without side effects
        async with async_session() as session:
            other_subject = await create_subject(session, SubjectCreate(name=f"B02 Other {token}"))
            other_kp = await create_knowledge_point(
                session, KnowledgePointCreate(subject_id=other_subject.id, name=f"B02 OtherKP {token}")
            )
            await session.commit()
            state["subject_ids"].append(other_subject.id)
            state["kp_ids"].append(other_kp.id)

        async with async_session() as session:
            try:
                await mistake_service.create_mistake_draft(
                    session,
                    MistakeDraftCreate(question_id=question_id, knowledge_point_ids=[other_kp.id]),
                )
            except mistake_service.MistakeValidationError:
                pass
            else:
                raise AssertionError("cross-subject KP must be rejected")
            await session.rollback()

        async with async_session() as session:
            try:
                await mistake_service.create_mistake_draft(
                    session,
                    MistakeDraftCreate(question_id=question_id, knowledge_point_ids=[10**9 + 7]),
                )
            except mistake_service.MistakeNotFound:
                pass
            else:
                raise AssertionError("stale KP id must be rejected")
            await session.rollback()

        # --- Stage 10: repeated conversion is idempotent; version conflict is safe
        async with async_session() as session:
            draft = await mistake_service.get_mistake_draft(session, draft_item_id)
            again = await mistake_service.convert_mistake_draft(session, draft_item_id, draft.item.version)
            await session.commit()
            assert again.id == mistake_id
            count = await session.scalar(
                select(func.count()).select_from(Mistake).where(
                    Mistake.source_draft_item_id == draft_item_id
                )
            )
            assert count == 1, count

        async with async_session() as session:
            conflict_draft = await mistake_service.create_mistake_draft(
                session,
                MistakeDraftCreate(question_id=question_id, knowledge_point_ids=[]),
            )
            await session.flush()
            conflict_item_id = conflict_draft.item.id
            state["draft_item_ids"].append(conflict_item_id)
            state["draft_ids"].append(conflict_draft.id)
            try:
                await mistake_service.convert_mistake_draft(session, conflict_item_id, 99)
            except mistake_service.MistakeConflict:
                await session.rollback()
            else:
                raise AssertionError("stale version must not convert")
            after = await session.scalar(
                select(func.count()).select_from(Mistake).where(
                    Mistake.source_draft_item_id == conflict_item_id
                )
            )
            assert after == 0, after
            await session.rollback()
    finally:
        await _cleanup(state)
        await engine.dispose()


def test_kp_preservation_cross_transaction() -> None:
    asyncio.run(_scenario())
