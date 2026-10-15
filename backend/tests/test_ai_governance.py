"""Week 4 PR-19 — AI Run target linkage governance tests.

Covers:
- (a) gateway call with target_type/target_id persists them on the AiRun row
- (b) capture recognition with capture_id links the run to the Capture
- (c) creation-type backfill via the real `backfill_ai_run_target` helper;
  abandoned suggestions keep NULL without a write or error
- (d) polish streaming path creates no persisted target-linked run (exemption)
- (e) retry_ai_run copies the parent's target

AI provider calls are mocked so no network is used. The gateway writes its
AiRun rows in its own committed session, so linkage assertions read them back
through a fresh session and purge them afterwards.
"""

import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import delete, func, or_, select

from app.database import async_session, engine
from app.models.ai_run import AiRun
from app.services.ai_gateway import call_text
from app.services.ai_run_service import (
    backfill_ai_run_target,
    get_ai_run_for_update,
    retry_ai_run,
    start_ai_run,
)
from app.services.ai_service import CallResult, ProviderAttempt
from app.services.ai_task_types import AiTaskType
from app.services.capture_recognition import recognize_image

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)


class _TargetLinkageBase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        self.addAsyncCleanup(self._purge_committed_runs)
        await self.session.begin()
        self.target_id = str(uuid.uuid4())
        self._purged_run_ids: set[uuid.UUID] = set()
        self._purged_target_ids: set[str] = {self.target_id}

    async def _purge_committed_runs(self):
        # Release any in-flight row locks held by the test session before the
        # purge DELETE; otherwise the cleanup itself deadlocks.
        await self.session.rollback()
        clauses = []
        if self._purged_run_ids:
            clauses.append(AiRun.id.in_(list(self._purged_run_ids)))
        if self._purged_target_ids:
            clauses.append(AiRun.target_id.in_(list(self._purged_target_ids)))
        if not clauses:
            return
        async with async_session() as session:
            await session.execute(delete(AiRun).where(or_(*clauses)))
            await session.commit()

    async def _fetch_by_target(self, task_type: str) -> AiRun | None:
        async with async_session() as session:
            result = await session.execute(
                select(AiRun).where(
                    AiRun.task_type == task_type,
                    AiRun.target_id == self.target_id,
                )
            )
            return result.scalars().first()

    async def _fetch_by_id(self, run_id: uuid.UUID) -> AiRun | None:
        async with async_session() as session:
            return await session.get(AiRun, run_id)

    async def _count_runs(self) -> int:
        async with async_session() as session:
            return int(
                await session.scalar(select(func.count()).select_from(AiRun))
            )


class GatewayTargetLinkageTest(_TargetLinkageBase):
    async def test_call_text_writes_target_type_and_id(self):
        mock_result = CallResult(
            data={"question_text": "q"},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
        ):
            gw = await call_text(
                AiTaskType.CAPTURE_DRAFT,
                [{"role": "user", "content": "hi"}],
                input_summary="safe",
                target_type="Capture",
                target_id=self.target_id,
            )

        self.assertTrue(gw.success)
        run = await self._fetch_by_target(AiTaskType.CAPTURE_DRAFT.value)
        self.assertIsNotNone(run)
        self.assertEqual(run.target_type, "Capture")
        self.assertEqual(run.target_id, self.target_id)

    async def test_call_without_target_records_null_target(self):
        mock_result = CallResult(
            data={"question_text": "q"},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value=None,
            ) as start_run,
        ):
            gw = await call_text(
                AiTaskType.CAPTURE_DRAFT,
                [{"role": "user", "content": "hi"}],
            )

        self.assertTrue(gw.success)
        self.assertEqual(
            start_run.await_args.kwargs,
            {
                "target_type": None,
                "target_id": None,
                "creation_context": None,
                "created_by": None,
            },
        )


class RecognitionTargetLinkageTest(_TargetLinkageBase):
    async def test_recognize_image_links_capture(self):
        mock_result = CallResult(
            data={"text": "recognized text"},
            attempts=[
                ProviderAttempt(provider="dashscope_vision", model="m1", success=True)
            ],
            provider_used="dashscope_vision",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
        ):
            result = await recognize_image(
                MINIMAL_PNG,
                "image/png",
                capture_id=self.target_id,
            )

        self.assertTrue(result.success)
        self.assertEqual(result.recognized_text, "recognized text")
        run = await self._fetch_by_target(AiTaskType.CAPTURE_RECOGNITION.value)
        self.assertIsNotNone(run)
        self.assertEqual(run.target_type, "Capture")
        self.assertEqual(run.target_id, self.target_id)

    async def test_recognize_image_without_capture_id_has_no_target(self):
        mock_result = CallResult(
            data={"text": "recognized text"},
            attempts=[
                ProviderAttempt(provider="dashscope_vision", model="m1", success=True)
            ],
            provider_used="dashscope_vision",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value=None,
            ) as start_run,
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertTrue(result.success)
        self.assertEqual(
            start_run.await_args.kwargs,
            {"target_type": None, "target_id": None},
        )


class CreationTypeBackfillTest(_TargetLinkageBase):
    async def _create_gateway_null_run(self) -> uuid.UUID:
        """Create a real committed AiRun through the gateway with no target."""
        marker = f"pr19-backfill-{uuid.uuid4()}"
        mock_result = CallResult(
            data={"question_text": "q"},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
        ):
            gw = await call_text(
                AiTaskType.CAPTURE_DRAFT,
                [{"role": "user", "content": "hi"}],
                input_summary=marker,
            )
        self.assertTrue(gw.success)

        async with async_session() as session:
            result = await session.execute(
                select(AiRun).where(AiRun.input_summary == marker)
            )
            run = result.scalars().one()
            self._purged_run_ids.add(run.id)
            return run.id

    async def test_backfill_helper_links_existing_run(self):
        run_id = await self._create_gateway_null_run()
        before = await self._fetch_by_id(run_id)
        self.assertIsNotNone(before)
        self.assertIsNone(before.target_type)
        self.assertIsNone(before.target_id)

        async with async_session() as session:
            updated = await backfill_ai_run_target(
                session,
                run_id,
                self.target_id,
                target_type="Mistake",
            )
            await session.commit()

        self.assertTrue(updated)
        after = await self._fetch_by_id(run_id)
        self.assertEqual(after.target_type, "Mistake")
        self.assertEqual(after.target_id, self.target_id)

    async def test_backfill_helper_returns_false_for_missing_run(self):
        async with async_session() as session:
            updated = await backfill_ai_run_target(
                session,
                uuid.uuid4(),
                self.target_id,
                target_type="Mistake",
            )
        self.assertFalse(updated)

    async def test_abandoned_suggestion_keeps_null_without_error(self):
        run_id = await self._create_gateway_null_run()

        row = await self._fetch_by_id(run_id)
        self.assertIsNotNone(row)
        self.assertIsNone(row.target_type)
        self.assertIsNone(row.target_id)
        self.assertEqual(row.status, "succeeded")


class GatewayRunIdTest(_TargetLinkageBase):
    async def test_call_text_returns_run_id(self):
        marker = f"f05-runid-{uuid.uuid4()}"
        mock_result = CallResult(
            data={"question_text": "q"},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway._write_call_log", new_callable=AsyncMock),
        ):
            gw = await call_text(
                AiTaskType.CAPTURE_DRAFT,
                [{"role": "user", "content": "hi"}],
                input_summary=marker,
            )

        self.assertTrue(gw.success)
        self.assertIsNotNone(gw.run_id)
        async with async_session() as session:
            run = (
                await session.execute(select(AiRun).where(AiRun.id == gw.run_id))
            ).scalars().one()
            self._purged_run_ids.add(run.id)
            self.assertEqual(run.status, "succeeded")


class CreationTypeSaveBindingTest(CreationTypeBackfillTest):
    """F05: the canonical MistakeDraft save binds the creation-type AiRun."""

    async def _source_question(self):
        from app.schemas.question import QuestionCreate
        from app.schemas.taxonomy import SubjectCreate
        from app.services import question_service
        from app.services.taxonomy_service import create_subject

        subject = await create_subject(
            self.session, SubjectCreate(name=f"F05 Subject {uuid.uuid4().hex[:8]}")
        )
        return await question_service.create_question(
            self.session,
            QuestionCreate(
                subject_id=subject.id,
                stem_md="F05 source question",
                question_type="short_answer",
                answer_data={"kind": "short_answer", "value": "x"},
            ),
        )

    async def test_loose_source_run_id_is_rejected(self):
        """B05b: the retired optional binding must not create a second path."""
        from app.schemas.mistake import MistakeDraftCreate
        from app.services import mistake_service

        run_id = await self._create_gateway_null_run()
        question = await self._source_question()
        with self.assertRaises(mistake_service.MistakeConflict):
            await mistake_service.create_mistake_draft(
                self.session,
                MistakeDraftCreate(question_id=question.id, source_run_id=run_id),
            )

    async def test_missing_run_is_rejected(self):
        from app.schemas.mistake import MistakeDraftCreate
        from app.services import mistake_service

        question = await self._source_question()
        with self.assertRaises(mistake_service.MistakeConflict):
            await mistake_service.create_mistake_draft(
                self.session,
                MistakeDraftCreate(question_id=question.id, source_run_id=uuid.uuid4()),
            )

    async def test_rejected_run_is_rejected(self):
        from app.schemas.mistake import MistakeDraftCreate
        from app.services import mistake_service

        run_id = await self._create_gateway_null_run()
        async with async_session() as session:
            run = await session.get(AiRun, run_id)
            run.review_status = "rejected"
            await session.commit()
        question = await self._source_question()
        with self.assertRaises(mistake_service.MistakeConflict):
            await mistake_service.create_mistake_draft(
                self.session,
                MistakeDraftCreate(question_id=question.id, source_run_id=run_id),
            )

    async def test_already_bound_run_rejects_different_target(self):
        from app.services.ai_run_service import AiRunTargetConflict, bind_run_to_entity

        run_id = await self._create_gateway_null_run()
        await bind_run_to_entity(
            self.session, run_id, entity_type="MistakeDraft", entity_id=uuid.uuid4()
        )
        with self.assertRaises(AiRunTargetConflict):
            await bind_run_to_entity(
                self.session, run_id, entity_type="MistakeDraft", entity_id=uuid.uuid4()
            )

    async def test_same_target_binding_is_idempotent(self):
        from app.services.ai_run_service import bind_run_to_entity

        run_id = await self._create_gateway_null_run()
        entity_id = uuid.uuid4()
        self.assertTrue(
            await bind_run_to_entity(
                self.session, run_id, entity_type="MistakeDraft", entity_id=entity_id
            )
        )
        self.assertTrue(
            await bind_run_to_entity(
                self.session, run_id, entity_type="MistakeDraft", entity_id=entity_id
            )
        )

    async def test_failed_run_is_rejected(self):
        from app.services.ai_run_service import AiRunConflict, bind_run_to_entity

        run_id = await self._create_gateway_null_run()
        async with async_session() as session:
            run = await session.get(AiRun, run_id)
            run.status = "failed"
            await session.commit()
        with self.assertRaises(AiRunConflict):
            await bind_run_to_entity(
                self.session, run_id, entity_type="MistakeDraft", entity_id=uuid.uuid4()
            )

    async def test_non_creation_task_type_is_rejected(self):
        from app.services.ai_run_service import AiRunConflict, bind_run_to_entity

        run = await start_ai_run(self.session, task_type="analyze_text")
        run.status = "succeeded"
        await self.session.flush()
        with self.assertRaises(AiRunConflict):
            await bind_run_to_entity(
                self.session, run.id, entity_type="MistakeDraft", entity_id=uuid.uuid4()
            )


class RetryTargetPropagationTest(_TargetLinkageBase):
    async def test_retry_copies_parent_target(self):
        parent = await start_ai_run(
            self.session,
            task_type="capture_draft",
            target_type="Capture",
            target_id=self.target_id,
            replay_input={"recognized_text": "hello"},
        )
        parent.status = "succeeded"
        await self.session.flush()

        retry = await retry_ai_run(self.session, parent)

        self.assertEqual(retry.target_type, "Capture")
        self.assertEqual(retry.target_id, self.target_id)
        self.assertEqual(retry.parent_run_id, parent.id)
        self.assertEqual(retry.attempt, 2)


class PolishExemptionTest(_TargetLinkageBase):
    async def test_polish_stream_creates_no_persisted_run(self):
        from app.services import ai_polish_service

        before = await self._count_runs()

        with patch.object(ai_polish_service, "_get_stream_providers", return_value=[]):
            chunks = [
                chunk
                async for chunk in ai_polish_service.polish_stream(
                    text="hello",
                    action="polish",
                    context=None,
                    request=MagicMock(),
                )
            ]

        self.assertTrue(any("error" in chunk for chunk in chunks))
        self.assertEqual(chunks[-1], "data: [DONE]\n\n")

        after = await self._count_runs()
        self.assertEqual(after, before)


class AiRunLockTest(_TargetLinkageBase):
    async def test_decision_lock_reads_fresh_row_not_stale_object(self):
        async with async_session() as seeding:
            run = await start_ai_run(
                seeding,
                task_type="analyze_text",
                target_type="note",
                target_id=self.target_id,
                review_required=True,
            )
            run.status = "succeeded"
            run.validation_status = "passed"
            await seeding.commit()
            run_id = run.id
        self._purged_run_ids.add(run_id)

        stale = await self.session.get(AiRun, run_id)
        assert stale is not None
        self.assertEqual(stale.review_status, "pending")

        async with async_session() as other:
            other_run = await other.get(AiRun, run_id)
            other_run.review_status = "accepted"
            other_run.review_revision += 1
            await other.commit()

        # The decision path locks and refreshes, so it must observe the
        # committed decision rather than the stale in-memory object.
        fresh = await get_ai_run_for_update(self.session, run_id)
        self.assertEqual(fresh.review_status, "accepted")
        self.assertEqual(fresh.review_revision, 1)


if __name__ == "__main__":
    unittest.main()
