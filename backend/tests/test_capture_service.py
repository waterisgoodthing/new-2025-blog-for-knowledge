"""Batch 8 capture service 定向测试。

覆盖：
- fake adapter 成功/失败
- capture → mistake_draft 幂等转换
- 失败零污染
- 人工编辑手动路径
"""

import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from sqlalchemy import func, select

from app.config import get_settings
from app.database import async_session, engine
from app.models.capture import CaptureItem
from app.models.mistake import Mistake, MistakeDraft
from app.models.question import DraftItem, QuestionDraft
from app.models.review_item import ReviewItem
from app.schemas.capture import CaptureConvert, CaptureCreate, CapturePatch
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services.attachment_service import create_attachment_from_bytes
from app.services.capture_ai_draft import DraftResult
from app.services.capture_service import (
    CaptureConflict,
    convert_capture,
    create_capture,
    get_capture,
    list_captures,
    patch_capture,
    trigger_draft,
    trigger_recognition,
)
from app.services.taxonomy_service import create_knowledge_point, create_subject

# Minimal 1x1 RGB PNG
MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x5c\xcd\xff\x69"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class CaptureServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()

        self.subject = await create_subject(
            self.session,
            SubjectCreate(name="Batch8 Capture Subject"),
        )
        self.kp = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(
                subject_id=self.subject.id,
                name="Batch8 Capture KP",
            ),
        )
        self.attachment = await create_attachment_from_bytes(
            self.session,
            original_name="test.png",
            content=MINIMAL_PNG,
            mime_type="image/png",
        )
        self.upload_root = Path(get_settings().UPLOAD_ROOT)

        self.addCleanup(self._cleanup_attachment_file)

    def _cleanup_attachment_file(self):
        if hasattr(self, "attachment") and self.attachment.storage_key:
            file_path = self.upload_root / self.attachment.storage_key
            if file_path.exists():
                file_path.unlink()

    async def _make_capture(self):
        return await create_capture(
            self.session,
            CaptureCreate(attachment_id=self.attachment.id),
        )

    async def _count(self, model):
        return await self.session.scalar(select(func.count()).select_from(model))

    async def test_create_capture_sets_uploaded_status(self):
        capture = await self._make_capture()
        self.assertEqual(capture.status, "uploaded")
        self.assertEqual(capture.source_attachment_id, self.attachment.id)
        self.assertIsNone(capture.recognized_text)

    async def test_get_capture_raises_for_missing_id(self):
        import uuid as uuid_mod

        with self.assertRaises(Exception):
            await get_capture(self.session, uuid_mod.uuid4())

    async def test_list_captures_returns_list(self):
        c1 = await self._make_capture()
        c2 = await self._make_capture()
        captures = await list_captures(self.session)
        ids = {c.id for c in captures}
        self.assertIn(c1.id, ids)
        self.assertIn(c2.id, ids)

    async def test_recognition_with_fake_succeeds(self):
        capture = await self._make_capture()
        updated = await trigger_recognition(
            self.session,
            capture.id,
            use_fake=True,
            fake_text="Test recognized text",
        )
        self.assertEqual(updated.status, "recognized")
        self.assertEqual(updated.recognized_text, "Test recognized text")
        self.assertEqual(updated.last_stage, "recognize")
        self.assertGreaterEqual(updated.attempt_count, 1)

    async def test_draft_with_fake_succeeds(self):
        capture = await self._make_capture()
        await trigger_recognition(
            self.session,
            capture.id,
            use_fake=True,
            fake_text="Test question text",
        )
        updated = await trigger_draft(self.session, capture.id, use_fake=True)
        self.assertEqual(updated.status, "ready")
        self.assertIsNotNone(updated.question_draft_text)
        self.assertIsNotNone(updated.analysis_draft_text)
        self.assertIsNotNone(updated.error_summary_draft)
        self.assertEqual(updated.last_stage, "draft")

    async def test_patch_capture_manual_path(self):
        capture = await self._make_capture()
        updated = await patch_capture(
            self.session,
            capture.id,
            CapturePatch(question_draft_text="Manual question"),
        )
        self.assertEqual(updated.status, "ready")
        self.assertEqual(updated.question_draft_text, "Manual question")

    async def test_patch_capture_clears_failed_status(self):
        capture = await self._make_capture()
        capture.status = "failed"
        capture.error_code = "test_error"
        await self.session.flush()

        updated = await patch_capture(
            self.session,
            capture.id,
            CapturePatch(question_draft_text="Fixed question"),
        )
        self.assertEqual(updated.status, "ready")
        self.assertIsNone(updated.error_code)

    async def test_convert_is_idempotent(self):
        capture = await self._make_capture()
        await trigger_recognition(
            self.session,
            capture.id,
            use_fake=True,
            fake_text="Test question",
        )
        await trigger_draft(self.session, capture.id, use_fake=True)

        payload = CaptureConvert(
            subject_id=self.subject.id,
            question_text="Test question",
            knowledge_point_ids=[self.kp.id],
        )
        result1 = await convert_capture(self.session, capture.id, payload)
        self.assertEqual(result1.capture.status, "converted")
        self.assertIsNotNone(result1.mistake_draft_item_id)
        self.assertIsNotNone(result1.question_draft_id)

        result2 = await convert_capture(self.session, capture.id, payload)
        self.assertEqual(
            result1.mistake_draft_item_id,
            result2.mistake_draft_item_id,
        )

    async def test_convert_requires_ready_status(self):
        capture = await self._make_capture()
        with self.assertRaises(CaptureConflict):
            await convert_capture(
                self.session,
                capture.id,
                CaptureConvert(
                    subject_id=self.subject.id,
                    question_text="Test",
                ),
            )

    async def test_recognition_failure_zero_pollution(self):
        mistakes_before = await self._count(Mistake)
        drafts_before = await self._count(MistakeDraft)
        reviews_before = await self._count(ReviewItem)
        items_before = await self._count(DraftItem)

        capture = await self._make_capture()
        updated = await trigger_recognition(self.session, capture.id)
        self.assertEqual(updated.status, "failed")
        self.assertIsNotNone(updated.error_code)

        self.assertEqual(await self._count(Mistake), mistakes_before)
        self.assertEqual(await self._count(MistakeDraft), drafts_before)
        self.assertEqual(await self._count(ReviewItem), reviews_before)
        self.assertEqual(await self._count(DraftItem), items_before)

    async def test_draft_failure_zero_pollution(self):
        capture = await self._make_capture()
        await trigger_recognition(
            self.session,
            capture.id,
            use_fake=True,
            fake_text="Test text",
        )

        mistakes_before = await self._count(Mistake)
        drafts_before = await self._count(MistakeDraft)
        reviews_before = await self._count(ReviewItem)
        items_before = await self._count(DraftItem)

        # 模拟 AI 草稿生成失败（不依赖真实凭据是否可用）
        with patch(
            "app.services.capture_service.draft_mistake",
            new_callable=AsyncMock,
            return_value=DraftResult(
                suggestion=None,
                success=False,
                error_code="provider_error",
                error_message_safe="Simulated AI failure",
            ),
        ):
            updated = await trigger_draft(self.session, capture.id)
        self.assertEqual(updated.status, "failed")
        self.assertEqual(updated.error_code, "provider_error")

        self.assertEqual(await self._count(Mistake), mistakes_before)
        self.assertEqual(await self._count(MistakeDraft), drafts_before)
        self.assertEqual(await self._count(ReviewItem), reviews_before)
        self.assertEqual(await self._count(DraftItem), items_before)

    async def test_convert_creates_drafts_not_mistakes(self):
        capture = await self._make_capture()
        await trigger_recognition(
            self.session,
            capture.id,
            use_fake=True,
            fake_text="Test",
        )
        await trigger_draft(self.session, capture.id, use_fake=True)

        mistakes_before = await self._count(Mistake)
        reviews_before = await self._count(ReviewItem)

        result = await convert_capture(
            self.session,
            capture.id,
            CaptureConvert(
                subject_id=self.subject.id,
                question_text="Test question",
                knowledge_point_ids=[self.kp.id],
            ),
        )

        self.assertEqual(result.capture.status, "converted")
        self.assertEqual(await self._count(Mistake), mistakes_before)
        self.assertEqual(await self._count(ReviewItem), reviews_before)

        # mistake_draft_item_id 是 DraftItem.id（FK），不是 MistakeDraft 主键
        md_stmt = select(MistakeDraft).where(
            MistakeDraft.draft_item_id == result.mistake_draft_item_id
        )
        mistake_draft = (await self.session.execute(md_stmt)).scalar_one_or_none()
        self.assertIsNotNone(mistake_draft)


if __name__ == "__main__":
    unittest.main()
