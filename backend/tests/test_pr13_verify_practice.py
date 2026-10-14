"""PR-13 independent verification suite (agent PR-13-verify, senior-qa-sdet).

Independent reproduction of the PR-13 acceptance criteria. Does not import or
reuse the implementer test helpers; fixtures are built directly from ORM models.

Coverage:

A. candidate-count matrix 0/1/2/3/>10 -> 0/1/2/3/3 + honest Empty metadata
B. filters/ordering: weak-KP, stable tie, archived, window, review-context,
   mastered, no-KP fallback, selection_reason / Empty metadata completeness
C. read-only: no rows created in attempts/review_items/review_records
D. contract/permission: anonymous 401/403, admin 200, three-way DTO agreement,
   forbidden answer fields absent (JSON + OpenAPI)
E. source checks: PR-10 sort-key reuse, no AI/ML, no legacy Note source

Run from ``backend/`` via the Week 3 guard:

    python3 ../scripts/week3-scratch-guard.py run --db-name astra_week3_pr13_verify \
        -- .venv/bin/python -m pytest tests/test_pr13_verify_practice.py -q
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database import async_session, engine
from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.note import Subject
from app.models.question import DraftItem, Question, QuestionKnowledgePoint
from app.models.review_item import ReviewItem, ReviewRecord
from app.models.taxonomy import KnowledgePoint, KnowledgePointLink
from app.services import practice_service

REPO_ROOT = Path(__file__).resolve().parents[2]
PRACTICE_PATH = "/api/admin/practice/today"

ITEM_FIELDS = {"question_id", "knowledge_point_id", "selection_reason"}
FORBIDDEN_ITEM_FIELDS = {"answer_data", "correct_answer", "analysis", "explanation"}
RESPONSE_FIELDS = {"items", "empty_metadata"}
EMPTY_METADATA_FIELDS = {
    "reason",
    "raw_candidate_count",
    "recent_attempt_excluded_count",
    "mastered_excluded_count",
    "eligible_candidate_count",
    "target_count",
    "returned_count",
    "window_hours",
}
SELECTION_REASONS = {
    "weak_kp_wrong_rate",
    "weak_kp_lapse",
    "weak_kp_due",
    "stable_order_fallback",
}
EMPTY_REASONS = {
    "candidates_returned",
    "no_eligible_candidates",
    "all_candidates_excluded",
}
WINDOW_HOURS = 7 * 24


def _table_counts() -> dict[str, int]:
    async def _run() -> dict[str, int]:
        eng = create_async_engine(os.environ["DATABASE_URL"])
        try:
            async with eng.connect() as conn:
                out: dict[str, int] = {}
                for table in ("attempts", "review_items", "review_records"):
                    out[table] = int(
                        (await conn.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one()
                    )
                return out
        finally:
            await eng.dispose()

    return asyncio.run(_run())


def _assert_metadata_honest(test: unittest.TestCase, md) -> None:
    test.assertIn(md.reason, EMPTY_REASONS)
    test.assertIsInstance(md.window_hours, int)
    test.assertEqual(md.window_hours, WINDOW_HOURS)
    test.assertGreaterEqual(md.raw_candidate_count, 0)
    test.assertGreaterEqual(md.recent_attempt_excluded_count, 0)
    test.assertGreaterEqual(md.mastered_excluded_count, 0)
    test.assertGreaterEqual(md.eligible_candidate_count, 0)
    test.assertEqual(
        md.eligible_candidate_count,
        md.raw_candidate_count
        - md.recent_attempt_excluded_count
        - md.mastered_excluded_count,
        "eligible = raw - recent_excluded - mastered_excluded",
    )
    expected_target = (
        3 if md.eligible_candidate_count >= 3 else md.eligible_candidate_count
    )
    test.assertEqual(md.target_count, expected_target)
    test.assertEqual(md.returned_count, max(0, min(md.target_count, 10)))
    if md.returned_count == 0:
        if md.raw_candidate_count == 0:
            test.assertEqual(md.reason, "no_eligible_candidates")
        else:
            test.assertEqual(md.reason, "all_candidates_excluded")
    else:
        test.assertEqual(md.reason, "candidates_returned")


class PracticeMatrixAndFilterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        await engine.dispose(close=False)
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.now = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)

    async def _subject(self) -> Subject:
        subject = Subject(name=f"V13 {uuid.uuid4().hex[:8]}")
        self.session.add(subject)
        await self.session.flush()
        return subject

    async def _kp(self, subject: Subject, *, status: str = "active") -> KnowledgePoint:
        kp = KnowledgePoint(
            subject_id=subject.id, name=f"KP {uuid.uuid4().hex[:8]}", status=status
        )
        self.session.add(kp)
        await self.session.flush()
        return kp

    async def _question(
        self, subject: Subject, kp_ids=(), *, status: str = "active"
    ) -> Question:
        question = Question(
            subject_id=subject.id,
            question_text=f"Q {uuid.uuid4().hex[:8]}?",
            question_type="short_answer",
            status=status,
        )
        self.session.add(question)
        await self.session.flush()
        for kp_id in kp_ids:
            self.session.add(
                QuestionKnowledgePoint(
                    question_id=question.id, knowledge_point_id=kp_id
                )
            )
        await self.session.flush()
        return question

    async def _attempt(
        self,
        question: Question,
        *,
        is_correct: bool,
        submitted_at: datetime,
        context_type: str = "practice",
    ) -> Attempt:
        attempt = Attempt(
            question_id=question.id,
            submitted_answer="x",
            is_correct=is_correct,
            context_type=context_type,
            submitted_at=submitted_at,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def _mistake(
        self, subject: Subject, question: Question, *, status: str = "active"
    ) -> Mistake:
        item = DraftItem(
            draft_type="mistake",
            source_type="question",
            source_id=str(question.id),
            status="pending",
        )
        self.session.add(item)
        await self.session.flush()
        mistake = Mistake(
            source_draft_item_id=item.id,
            question_id=question.id,
            subject_id=subject.id,
            question_text="verifier mistake",
            reason_category="concept",
            status=status,
        )
        self.session.add(mistake)
        await self.session.flush()
        return mistake

    async def _review_item(
        self, mistake: Mistake, *, state: str, next_review_at: datetime | None = None
    ) -> ReviewItem:
        review_item = ReviewItem(
            target_type="mistake",
            target_id=str(mistake.id),
            mistake_id=mistake.id,
            state=state,
            interval_days=0,
            repetitions=0,
            next_review_at=next_review_at or self.now,
        )
        self.session.add(review_item)
        await self.session.flush()
        return review_item

    async def _link_kp_mistake(self, kp: KnowledgePoint, mistake: Mistake) -> None:
        self.session.add(
            KnowledgePointLink(
                knowledge_point_id=kp.id,
                target_type="mistake",
                target_id=str(mistake.id),
            )
        )
        await self.session.flush()

    async def _review_record(self, review_item: ReviewItem, *, rating: int) -> None:
        self.session.add(
            ReviewRecord(
                review_item_id=review_item.id,
                rating=rating,
                reviewed_at=self.now - timedelta(days=1),
                previous_interval_days=0,
                next_interval_days=1,
                previous_next_review_at=self.now - timedelta(days=2),
                next_review_at=self.now,
            )
        )
        await self.session.flush()

    async def _practice(self):
        return await practice_service.get_daily_practice(self.session, now=self.now)

    async def _counts(self) -> dict[str, int]:
        out = {}
        for table, model in (
            ("attempts", Attempt),
            ("review_items", ReviewItem),
            ("review_records", ReviewRecord),
        ):
            out[table] = int(
                (
                    await self.session.execute(select(func.count()).select_from(model))
                ).scalar_one()
            )
        return out

    # ---- A. candidate matrix -------------------------------------------------

    async def test_a_target_count_function_matrix(self) -> None:
        expected = {0: 0, 1: 1, 2: 2, 3: 3, 10: 3, 11: 3}
        actual = {
            n: practice_service.practice_target_count(n) for n in expected
        }
        print("PR13_VERIFY_MATRIX " + json.dumps({"target_count": actual}, sort_keys=True))
        self.assertEqual(actual, expected)

    async def test_a_service_matrix_0_1_2_3_12(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)

        zero = await self._practice()
        self.assertEqual(len(zero.items), 0)
        _assert_metadata_honest(self, zero.empty_metadata)

        await self._question(subject, [kp.id])
        one = await self._practice()
        self.assertEqual(len(one.items), 1)
        _assert_metadata_honest(self, one.empty_metadata)

        await self._question(subject, [kp.id])
        two = await self._practice()
        self.assertEqual(len(two.items), 2)
        _assert_metadata_honest(self, two.empty_metadata)

        await self._question(subject, [kp.id])
        three = await self._practice()
        self.assertEqual(len(three.items), 3)
        _assert_metadata_honest(self, three.empty_metadata)

        for _ in range(9):
            await self._question(subject, [kp.id])
        twelve = await self._practice()
        self.assertEqual(len(twelve.items), 3)
        self.assertEqual(twelve.empty_metadata.eligible_candidate_count, 12)
        self.assertEqual(twelve.empty_metadata.target_count, 3)
        _assert_metadata_honest(self, twelve.empty_metadata)

    async def test_a_zero_candidates_empty_metadata_is_honest(self) -> None:
        result = await self._practice()
        md = result.empty_metadata
        print(
            "PR13_VERIFY_EMPTY_ZERO "
            + json.dumps(md.model_dump(), sort_keys=True)
        )
        self.assertEqual(result.items, [])
        self.assertEqual(md.reason, "no_eligible_candidates")
        self.assertEqual(md.raw_candidate_count, 0)
        self.assertEqual(md.eligible_candidate_count, 0)
        self.assertEqual(md.returned_count, 0)
        self.assertEqual(md.target_count, 0)
        self.assertEqual(md.window_hours, WINDOW_HOURS)

    async def test_a_all_excluded_empty_metadata_is_honest(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        await self._attempt(
            question, is_correct=False, submitted_at=self.now - timedelta(hours=1)
        )
        result = await self._practice()
        md = result.empty_metadata
        self.assertEqual(result.items, [])
        self.assertEqual(md.reason, "all_candidates_excluded")
        self.assertEqual(md.raw_candidate_count, 1)
        self.assertEqual(md.recent_attempt_excluded_count, 1)
        self.assertEqual(md.eligible_candidate_count, 0)
        _assert_metadata_honest(self, md)

    async def test_a_more_than_ten_is_deterministic_and_sorted(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        questions = [await self._question(subject, [kp.id]) for _ in range(12)]
        first = await self._practice()
        second = await self._practice()
        ids = [item.question_id for item in first.items]
        expected = sorted(str(q.id) for q in questions)[:3]
        self.assertEqual(ids, expected)
        self.assertEqual(ids, [item.question_id for item in second.items])

    # ---- B. filters / ordering ----------------------------------------------

    async def test_b_weak_kp_priority_consumes_pr10_order(self) -> None:
        subject = await self._subject()
        weak_kp = await self._kp(subject)
        calm_kp = await self._kp(subject)
        weak_question = await self._question(subject, [weak_kp.id])
        calm_question = await self._question(subject, [calm_kp.id])
        await self._attempt(
            weak_question,
            is_correct=False,
            submitted_at=self.now - timedelta(days=8),
        )
        result = await self._practice()
        self.assertEqual(
            [item.knowledge_point_id for item in result.items],
            [weak_kp.id, calm_kp.id],
        )
        self.assertEqual(result.items[0].selection_reason, "weak_kp_wrong_rate")
        self.assertEqual(result.items[1].selection_reason, "stable_order_fallback")
        self.assertEqual(result.items[0].question_id, str(weak_question.id))
        self.assertEqual(result.items[1].question_id, str(calm_question.id))

    async def test_b_multi_kp_question_uses_weakest_linked_kp(self) -> None:
        subject = await self._subject()
        strong_kp = await self._kp(subject)
        calm_kp = await self._kp(subject)
        strong_q = await self._question(subject, [strong_kp.id])
        await self._attempt(
            strong_q, is_correct=False, submitted_at=self.now - timedelta(days=8)
        )
        multi_q = await self._question(subject, [strong_kp.id, calm_kp.id])
        result = await self._practice()
        mapping = {item.question_id: item.knowledge_point_id for item in result.items}
        self.assertEqual(mapping[str(multi_q.id)], strong_kp.id)
        self.assertNotEqual(mapping[str(multi_q.id)], calm_kp.id)

    async def test_b_stable_tie_same_kp_by_question_id(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        late = await self._question(subject, [kp.id])
        early = await self._question(subject, [kp.id])
        result = await self._practice()
        ids = [item.question_id for item in result.items]
        self.assertEqual(ids, sorted([str(late.id), str(early.id)]))

    async def test_b_stable_tie_across_kps_by_kp_id(self) -> None:
        subject = await self._subject()
        first_kp = await self._kp(subject)
        second_kp = await self._kp(subject)
        first_q = await self._question(subject, [first_kp.id])
        second_q = await self._question(subject, [second_kp.id])
        result = await self._practice()
        ordered = [(i.knowledge_point_id, i.question_id) for i in result.items]
        self.assertLess(first_kp.id, second_kp.id)
        self.assertEqual(
            ordered,
            [(first_kp.id, str(first_q.id)), (second_kp.id, str(second_q.id))],
        )

    async def test_b_lapse_and_due_reasons_flow_from_pr10(self) -> None:
        subject = await self._subject()
        weak_kp = await self._kp(subject)
        lapse_kp = await self._kp(subject)
        due_kp = await self._kp(subject)

        weak_q = await self._question(subject, [weak_kp.id])
        await self._attempt(
            weak_q, is_correct=False, submitted_at=self.now - timedelta(days=8)
        )

        lapse_q = await self._question(subject, [lapse_kp.id])
        lapse_mistake = await self._mistake(subject, lapse_q)
        lapse_item = await self._review_item(lapse_mistake, state="active")
        await self._link_kp_mistake(lapse_kp, lapse_mistake)
        await self._review_record(lapse_item, rating=1)

        due_q = await self._question(subject, [due_kp.id])
        due_mistake = await self._mistake(subject, due_q)
        await self._review_item(
            due_mistake, state="active", next_review_at=self.now - timedelta(days=1)
        )
        await self._link_kp_mistake(due_kp, due_mistake)

        result = await self._practice()
        reasons = {item.knowledge_point_id: item.selection_reason for item in result.items}
        print("PR13_VERIFY_REASONS " + json.dumps(reasons, sort_keys=True))
        self.assertEqual(reasons[weak_kp.id], "weak_kp_wrong_rate")
        self.assertEqual(reasons[lapse_kp.id], "weak_kp_lapse")
        self.assertEqual(reasons[due_kp.id], "weak_kp_due")

    async def test_b_archived_question_excluded(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id], status="archived")
        result = await self._practice()
        self.assertEqual(result.items, [])
        self.assertEqual(result.empty_metadata.raw_candidate_count, 0)
        self.assertEqual(result.empty_metadata.reason, "no_eligible_candidates")

    async def test_b_window_boundary_and_review_context(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        inside = await self._question(subject, [kp.id])
        boundary = await self._question(subject, [kp.id])
        outside = await self._question(subject, [kp.id])
        review_ctx = await self._question(subject, [kp.id])
        await self._attempt(
            inside, is_correct=True, submitted_at=self.now - timedelta(hours=1)
        )
        await self._attempt(
            boundary,
            is_correct=True,
            submitted_at=self.now - timedelta(hours=WINDOW_HOURS),
        )
        await self._attempt(
            outside,
            is_correct=True,
            submitted_at=self.now - timedelta(hours=WINDOW_HOURS, seconds=1),
        )
        await self._attempt(
            review_ctx,
            is_correct=True,
            submitted_at=self.now - timedelta(hours=1),
            context_type="review",
        )
        result = await self._practice()
        returned = {item.question_id for item in result.items}
        self.assertNotIn(str(inside.id), returned)
        self.assertNotIn(str(boundary.id), returned, "window_start is inclusive")
        self.assertIn(str(outside.id), returned)
        self.assertIn(str(review_ctx.id), returned, "review-context attempt is not practice")
        self.assertEqual(result.empty_metadata.recent_attempt_excluded_count, 2)

    async def test_b_mastered_linked_mistake_excluded(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        mastered_q = await self._question(subject, [kp.id])
        active_q = await self._question(subject, [kp.id])
        mastered_mistake = await self._mistake(subject, mastered_q)
        await self._review_item(mastered_mistake, state="mastered")
        active_mistake = await self._mistake(subject, active_q)
        await self._review_item(active_mistake, state="active")
        result = await self._practice()
        returned = {item.question_id for item in result.items}
        self.assertNotIn(str(mastered_q.id), returned)
        self.assertIn(str(active_q.id), returned)
        self.assertEqual(result.empty_metadata.mastered_excluded_count, 1)

    async def test_b_mastered_archived_mistake_still_excludes_observation(self) -> None:
        # Task text says "any linked canonical Mistake" without a status
        # qualifier; this records the current (unfiltered) behaviour explicitly.
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        mistake = await self._mistake(subject, question, status="archived")
        await self._review_item(mistake, state="mastered")
        result = await self._practice()
        self.assertEqual(result.items, [])
        self.assertEqual(result.empty_metadata.mastered_excluded_count, 1)

    async def test_b_question_without_kp_is_not_a_candidate(self) -> None:
        subject = await self._subject()
        no_kp = await self._question(subject, [])
        first = await self._practice()
        second = await self._practice()
        self.assertEqual(first.items, [])
        self.assertEqual(first.empty_metadata.raw_candidate_count, 0)
        self.assertEqual(first.empty_metadata.reason, "no_eligible_candidates")
        self.assertEqual(
            first.model_dump() if hasattr(first, "model_dump") else first.items,
            second.model_dump() if hasattr(second, "model_dump") else second.items,
        )
        self.assertNotEqual(str(no_kp.id), "")

        kp = await self._kp(subject)
        kept = await self._question(subject, [kp.id])
        third = await self._practice()
        self.assertEqual(
            [item.question_id for item in third.items], [str(kept.id)]
        )
        self.assertEqual(third.empty_metadata.raw_candidate_count, 1)

    async def test_b_selection_reason_and_empty_reason_catalogs_locked(self) -> None:
        self.assertEqual(
            {
                practice_service.SELECTION_REASON_WRONG_RATE,
                practice_service.SELECTION_REASON_LAPSE,
                practice_service.SELECTION_REASON_DUE,
                practice_service.SELECTION_REASON_STABLE_FALLBACK,
            },
            SELECTION_REASONS,
        )
        self.assertEqual(
            {
                practice_service.EMPTY_REASON_RETURNED,
                practice_service.EMPTY_REASON_NO_CANDIDATES,
                practice_service.EMPTY_REASON_ALL_EXCLUDED,
            },
            EMPTY_REASONS,
        )
        subject = await self._subject()
        kp = await self._kp(subject)
        question = await self._question(subject, [kp.id])
        result = await self._practice()
        self.assertIn(result.items[0].selection_reason, SELECTION_REASONS)
        _assert_metadata_honest(self, result.empty_metadata)
        self.assertNotEqual(result.items[0].selection_reason, "")
        self.assertEqual(result.items[0].question_id, str(question.id))

    # ---- C. read-only -------------------------------------------------------

    async def test_c_service_call_creates_no_rows(self) -> None:
        subject = await self._subject()
        kp = await self._kp(subject)
        await self._question(subject, [kp.id])
        before = await self._counts()
        await self._practice()
        await self._practice()
        after = await self._counts()
        print(
            "PR13_VERIFY_READONLY_SERVICE "
            + json.dumps({"before": before, "after": after}, sort_keys=True)
        )
        self.assertEqual(before, after)


class PracticeHttpContractTests(unittest.TestCase):
    @staticmethod
    def _seed_admin(username: str, password: str) -> None:
        from app.utils.auth import hash_password

        async def _run() -> None:
            eng = create_async_engine(os.environ["DATABASE_URL"])
            try:
                async with AsyncSession(eng) as session:
                    await session.execute(
                        text(
                            "INSERT INTO public.users (id,username,password_hash,is_admin) "
                            "VALUES (:id,:username,:password,true)"
                        ),
                        {
                            "id": uuid.uuid4(),
                            "username": username,
                            "password": hash_password(password),
                        },
                    )
                    await session.commit()
            finally:
                await eng.dispose()

        asyncio.run(_run())

    @staticmethod
    def _seed_candidate() -> int:
        async def _run() -> int:
            eng = create_async_engine(os.environ["DATABASE_URL"])
            try:
                async with AsyncSession(eng) as session:
                    subject = Subject(name=f"V13HTTP {uuid.uuid4().hex[:8]}")
                    session.add(subject)
                    await session.flush()
                    kp = KnowledgePoint(
                        subject_id=subject.id, name=f"KP {uuid.uuid4().hex[:8]}"
                    )
                    session.add(kp)
                    await session.flush()
                    question = Question(
                        subject_id=subject.id,
                        question_text="V13 http question",
                        question_type="short_answer",
                    )
                    session.add(question)
                    await session.flush()
                    session.add(
                        QuestionKnowledgePoint(
                            question_id=question.id, knowledge_point_id=kp.id
                        )
                    )
                    sid = int(subject.id)
                    await session.commit()
                    return sid
            finally:
                await eng.dispose()

        return asyncio.run(_run())

    @staticmethod
    def _cleanup_subject(subject_id: int) -> None:
        async def _run() -> None:
            eng = create_async_engine(os.environ["DATABASE_URL"])
            try:
                async with eng.begin() as conn:
                    await conn.execute(
                        text("DELETE FROM questions WHERE subject_id = :sid"),
                        {"sid": subject_id},
                    )
                    await conn.execute(
                        text("DELETE FROM knowledge_points WHERE subject_id = :sid"),
                        {"sid": subject_id},
                    )
                    await conn.execute(
                        text("DELETE FROM subjects WHERE id = :sid"),
                        {"sid": subject_id},
                    )
            finally:
                await eng.dispose()

        asyncio.run(_run())

    def test_d1_anonymous_forbidden_admin_allowed(self) -> None:
        from fastapi.testclient import TestClient

        import main

        with TestClient(main.app) as client:
            anon = client.get(PRACTICE_PATH)
            self.assertIn(anon.status_code, (401, 403))

            username = f"pr13v-{uuid.uuid4().hex[:8]}"
            password = "pr13v-pass-123"
            self._seed_admin(username, password)
            login = client.post(
                "/api/auth/login", json={"username": username, "password": password}
            )
            self.assertEqual(login.status_code, 200, login.text)
            admin = client.get(PRACTICE_PATH)
            self.assertEqual(admin.status_code, 200, admin.text)
            print(
                "PR13_VERIFY_AUTH "
                + json.dumps({"anonymous": anon.status_code, "admin": admin.status_code})
            )

    def test_d2_dto_three_way_agreement(self) -> None:
        from app.schemas import practice as practice_schema
        from week3_contracts_support import (
            PRACTICE_FORBIDDEN_ITEM_FIELDS,
            PRACTICE_REQUIRED_ITEM_FIELDS,
            PRACTICE_RESPONSE_FIELDS,
        )

        def model_fields(model) -> set[str]:
            if hasattr(model, "model_fields"):
                return set(model.model_fields.keys())
            return set(model.__fields__.keys())

        ts_source = (REPO_ROOT / "src" / "lib" / "api" / "practice.ts").read_text(
            encoding="utf-8"
        )

        def ts_interface_fields(name: str) -> set[str]:
            match = re.search(
                rf"export interface {name} \{{(.*?)\n\}}", ts_source, re.S
            )
            self.assertIsNotNone(match, f"interface {name} not found in practice.ts")
            return set(re.findall(r"^\s*(\w+)\s*[?]?:", match.group(1), re.M))

        schema_item = model_fields(practice_schema.PracticeItem)
        schema_meta = model_fields(practice_schema.PracticeEmptyMetadata)
        schema_response = model_fields(practice_schema.PracticeTodayResponse)
        ts_item = ts_interface_fields("PracticeItem")
        ts_meta = ts_interface_fields("PracticeEmptyMetadata")
        ts_response = ts_interface_fields("PracticeTodayResponse")

        print(
            "PR13_VERIFY_DTO_THREEWAY "
            + json.dumps(
                {
                    "schema_item": sorted(schema_item),
                    "ts_item": sorted(ts_item),
                    "schema_meta": sorted(schema_meta),
                    "ts_meta": sorted(ts_meta),
                },
                sort_keys=True,
            )
        )
        self.assertEqual(schema_item, ITEM_FIELDS)
        self.assertEqual(schema_item, set(PRACTICE_REQUIRED_ITEM_FIELDS))
        self.assertEqual(schema_item, ts_item)
        self.assertEqual(schema_meta, EMPTY_METADATA_FIELDS)
        self.assertEqual(schema_meta, ts_meta)
        self.assertEqual(schema_response, RESPONSE_FIELDS)
        self.assertEqual(schema_response, set(PRACTICE_RESPONSE_FIELDS))
        self.assertEqual(schema_response, ts_response)
        self.assertTrue(
            set(PRACTICE_FORBIDDEN_ITEM_FIELDS).isdisjoint(schema_item | ts_item)
        )
        self.assertTrue(FORBIDDEN_ITEM_FIELDS.isdisjoint(schema_item | ts_item))

    def test_d3_forbidden_fields_absent_json_and_openapi(self) -> None:
        from fastapi.testclient import TestClient

        import main

        openapi = main.app.openapi()
        path = openapi["paths"][PRACTICE_PATH]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        ref = path.get("$ref", "")
        self.assertTrue(ref.endswith("PracticeTodayResponse"), ref)
        response_schema = openapi["components"]["schemas"]["PracticeTodayResponse"]
        self.assertEqual(set(response_schema["properties"]), RESPONSE_FIELDS)
        item_schema = openapi["components"]["schemas"]["PracticeItem"]
        self.assertEqual(set(item_schema["properties"]), ITEM_FIELDS)
        self.assertTrue(
            FORBIDDEN_ITEM_FIELDS.isdisjoint(set(item_schema["properties"]))
        )
        self.assertEqual(
            set(openapi["components"]["schemas"]["PracticeEmptyMetadata"]["properties"]),
            EMPTY_METADATA_FIELDS,
        )

        subject_id = None
        before = _table_counts()
        try:
            subject_id = self._seed_candidate()
            before = _table_counts()
            with TestClient(main.app) as client:
                username = f"pr13v-{uuid.uuid4().hex[:8]}"
                password = "pr13v-pass-123"
                self._seed_admin(username, password)
                login = client.post(
                    "/api/auth/login", json={"username": username, "password": password}
                )
                self.assertEqual(login.status_code, 200, login.text)
                response = client.get(PRACTICE_PATH)
                self.assertEqual(response.status_code, 200, response.text)
                payload = response.json()
        finally:
            if subject_id is not None:
                self._cleanup_subject(subject_id)

        after = _table_counts()
        print(
            "PR13_VERIFY_READONLY_HTTP "
            + json.dumps({"before": before, "after": after}, sort_keys=True)
        )
        print("PR13_VERIFY_HTTP_PAYLOAD " + json.dumps(payload, sort_keys=True))
        self.assertEqual(before, after)
        self.assertEqual(set(payload), RESPONSE_FIELDS)
        self.assertGreaterEqual(len(payload["items"]), 1)
        self.assertEqual(set(payload["empty_metadata"]), EMPTY_METADATA_FIELDS)
        for item in payload["items"]:
            self.assertEqual(set(item), ITEM_FIELDS)
            self.assertTrue(FORBIDDEN_ITEM_FIELDS.isdisjoint(item))
        self.assertEqual(
            payload["empty_metadata"]["returned_count"], len(payload["items"])
        )
        self.assertEqual(payload["empty_metadata"]["window_hours"], WINDOW_HOURS)


class PracticeSourceContractTests(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (REPO_ROOT / relative).read_text(encoding="utf-8")

    def test_e_reuses_pr10_sort_key_without_second_weighting(self) -> None:
        from app.services import kp_analytics_service
        from week3_contracts_support import KP_ANALYTICS_SORT_KEY

        self.assertEqual(
            kp_analytics_service.KP_ANALYTICS_SORT_KEY, KP_ANALYTICS_SORT_KEY
        )
        service_src = self._read("backend/app/services/practice_service.py")
        self.assertNotIn("KP_ANALYTICS_SORT_KEY", service_src)
        self.assertIn("get_knowledge_point_analytics", service_src)
        self.assertIn("kp_analytics_service", service_src)
        declarations = re.findall(
            r"KP_ANALYTICS_SORT_KEY\s*[:=]", service_src
        )
        self.assertEqual(declarations, [])
        app_decl = []
        for path in (REPO_ROOT / "backend" / "app").rglob("*.py"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if "KP_ANALYTICS_SORT_KEY" in line and "=" in line and "import" not in line:
                    app_decl.append(f"{path.relative_to(REPO_ROOT)}:{line.strip()}")
        print("PR13_VERIFY_SORTKEY_DECL " + json.dumps(app_decl))
        self.assertEqual(len(app_decl), 1)
        self.assertIn("kp_analytics_service.py", app_decl[0])

    def test_e_no_ai_ml_in_practice_vertical(self) -> None:
        files = [
            "backend/app/services/practice_service.py",
            "backend/app/routers/practice.py",
            "backend/app/schemas/practice.py",
            "src/lib/api/practice.ts",
        ]
        token = re.compile(
            r"\b(ai_service|openai|dashscope|deepseek|sklearn|torch|tensorflow|"
            r"embedding|llm|recommendation_model)\b",
            re.IGNORECASE,
        )
        hits = []
        for relative in files:
            for lineno, line in enumerate(self._read(relative).splitlines(), 1):
                if token.search(line):
                    hits.append(f"{relative}:{lineno}:{line.strip()}")
        print("PR13_VERIFY_AI_SCAN " + json.dumps(hits))
        self.assertEqual(hits, [])

    def test_e_no_legacy_note_source(self) -> None:
        files = [
            "backend/app/services/practice_service.py",
            "backend/app/routers/practice.py",
            "backend/app/schemas/practice.py",
            "src/lib/api/practice.ts",
        ]
        token = re.compile(
            r"(legacy_note|app\.models\.note|Note\b|notes\b|type\s*==\s*['\"]mistake['\"])"
        )
        hits = []
        for relative in files:
            for lineno, line in enumerate(self._read(relative).splitlines(), 1):
                if token.search(line):
                    hits.append(f"{relative}:{lineno}:{line.strip()}")
        print("PR13_VERIFY_LEGACY_SCAN " + json.dumps(hits))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
