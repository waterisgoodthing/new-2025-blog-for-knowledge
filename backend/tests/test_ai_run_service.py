import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.services.ai_run_service import (
    AiRunConflict,
    AiRunReplayUnavailable,
    complete_ai_run,
    decide_ai_run,
    fail_ai_run,
    retry_ai_run,
    start_ai_run,
)


class AiRunServiceTest(unittest.IsolatedAsyncioTestCase):
    async def test_start_ai_run_creates_running_business_record(self):
        db = Mock()
        db.flush = AsyncMock()

        run = await start_ai_run(
            db,
            task_type="capture_draft",
            prompt_version="v2",
            input_summary="safe summary",
            replay_input={"recognized_text": "question", "user_error_reason": "reason"},
            review_required=True,
        )

        self.assertEqual(run.status, "running")
        self.assertEqual(run.validation_status, "pending")
        self.assertEqual(run.review_status, "pending")
        self.assertEqual(
            run.replay_input,
            {"recognized_text": "question", "user_error_reason": "reason"},
        )
        db.add.assert_called_once_with(run)
        db.flush.assert_awaited_once()

    async def test_start_ai_run_rejects_sensitive_replay_input(self):
        db = Mock()
        db.flush = AsyncMock()

        with self.assertRaisesRegex(ValueError, "storage_key"):
            await start_ai_run(
                db,
                task_type="capture_draft",
                replay_input={"storage_key": "private/object"},
            )
        with self.assertRaisesRegex(ValueError, "image"):
            await start_ai_run(
                db,
                task_type="capture_draft",
                replay_input={"image": "data:image/png;base64,secret"},
            )

        db.add.assert_not_called()

    async def test_complete_and_fail_ai_run_finalize_running_record(self):
        db = Mock()
        db.flush = AsyncMock()
        success = await start_ai_run(db, task_type="capture_draft")

        await complete_ai_run(
            db,
            success,
            provider_used="deepseek",
            model="model",
            output_data={"answer": "ok", "api_key": "secret"},
            validation_status="passed",
            latency_ms=120,
        )

        self.assertEqual(success.status, "succeeded")
        self.assertEqual(success.output_data, {"answer": "ok"})
        self.assertIsNotNone(success.finished_at)

        failed = await start_ai_run(db, task_type="capture_draft")
        await fail_ai_run(
            db,
            failed,
            error_code="provider_error",
            error_message_safe="provider unavailable",
            latency_ms=50,
        )
        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.validation_status, "not_applicable")

    async def test_finalized_run_cannot_transition_again(self):
        db = Mock()
        db.flush = AsyncMock()
        run = await start_ai_run(db, task_type="capture_draft")
        await fail_ai_run(
            db,
            run,
            error_code="provider_error",
            error_message_safe="failed",
        )

        with self.assertRaisesRegex(ValueError, "running"):
            await complete_ai_run(
                db,
                run,
                output_data={"answer": "late"},
                validation_status="passed",
            )

    async def test_retry_creates_child_without_changing_parent(self):
        db = Mock()
        db.flush = AsyncMock()
        parent = await start_ai_run(
            db,
            task_type="capture_draft",
            replay_input={"recognized_text": "q", "user_error_reason": "r"},
            review_required=True,
        )
        parent.id = __import__("uuid").uuid4()
        await complete_ai_run(
            db,
            parent,
            output_data={"answer": "old"},
            validation_status="passed",
        )

        child = await retry_ai_run(db, parent)

        self.assertNotEqual(child.id, parent.id)
        self.assertEqual(child.parent_run_id, parent.id)
        self.assertEqual(child.attempt, 2)
        self.assertEqual(child.replay_input, parent.replay_input)
        self.assertEqual(parent.status, "succeeded")

    async def test_retry_never_guesses_from_input_summary(self):
        db = Mock()
        db.flush = AsyncMock()
        parent = await start_ai_run(
            db,
            task_type="capture_draft",
            input_summary="looks replayable but is not",
        )
        parent.id = __import__("uuid").uuid4()
        await fail_ai_run(
            db,
            parent,
            error_code="provider_error",
            error_message_safe="failed",
        )

        with self.assertRaises(AiRunReplayUnavailable):
            await retry_ai_run(db, parent)

    async def test_decision_uses_revision_and_writes_safe_audit(self):
        db = Mock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        run = await start_ai_run(
            db,
            task_type="capture_draft",
            review_required=True,
        )
        run.id = __import__("uuid").uuid4()
        await complete_ai_run(
            db,
            run,
            output_data={"answer": "draft only"},
            validation_status="passed",
        )

        with patch(
            "app.services.ai_run_service.audit_action",
            new_callable=AsyncMock,
        ) as audit:
            decided = await decide_ai_run(
                db,
                run,
                decision="accepted",
                expected_revision=0,
                note="private reviewer note",
            )

        self.assertEqual(decided.review_status, "accepted")
        self.assertEqual(decided.review_revision, 1)
        db.refresh.assert_awaited_once_with(run)
        audit.assert_awaited_once()
        audit_payload = audit.await_args.kwargs
        self.assertEqual(audit_payload["action"], "ai_run.accept")
        self.assertNotIn("private reviewer note", str(audit_payload))
        self.assertNotIn("output_data", str(audit_payload))

    async def test_decision_is_idempotent_but_conflicts_are_rejected(self):
        db = Mock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        run = await start_ai_run(
            db,
            task_type="capture_draft",
            review_required=True,
        )
        run.id = __import__("uuid").uuid4()
        await complete_ai_run(
            db,
            run,
            output_data={"answer": "draft only"},
            validation_status="warning",
        )

        with patch(
            "app.services.ai_run_service.audit_action",
            new_callable=AsyncMock,
        ):
            first = await decide_ai_run(
                db,
                run,
                decision="rejected",
                expected_revision=0,
            )
            same = await decide_ai_run(
                db,
                run,
                decision="rejected",
                expected_revision=0,
            )
            self.assertIs(same, first)
            with self.assertRaises(AiRunConflict):
                await decide_ai_run(
                    db,
                    run,
                    decision="accepted",
                    expected_revision=1,
                )

        pending = await start_ai_run(
            db,
            task_type="capture_draft",
            review_required=True,
        )
        await complete_ai_run(
            db,
            pending,
            output_data={"answer": "draft only"},
            validation_status="passed",
        )
        with self.assertRaises(AiRunConflict):
            await decide_ai_run(
                db,
                pending,
                decision="accepted",
                expected_revision=9,
            )
