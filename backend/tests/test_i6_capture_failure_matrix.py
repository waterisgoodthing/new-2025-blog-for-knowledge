import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from sqlalchemy import func, select

from app.config import get_settings
from app.database import async_session, engine
from app.models.capture import CaptureItem
from app.models.mistake import Mistake, MistakeDraft
from app.models.question import DraftItem
from app.models.review_item import ReviewItem
from app.schemas.attachment import AttachmentLinkCreate
from app.schemas.capture import CaptureCreate
from app.schemas.capture import CaptureDraftInput
from app.services.ai_gateway import GatewayCallResult
from app.services.attachment_service import create_attachment_from_bytes
from app.services.capture_ai_draft import draft_mistake
from app.services.capture_recognition import recognize_image
from app.services.capture_service import create_capture, trigger_draft, trigger_recognition


MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)


class CaptureFailureMatrixTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.attachment = await create_attachment_from_bytes(
            self.session,
            original_name="i6-failure.png",
            content=MINIMAL_PNG,
            mime_type="image/png",
        )
        self.upload_root = Path(get_settings().UPLOAD_ROOT)
        self.addCleanup(self._cleanup_attachment_file)

    def _cleanup_attachment_file(self):
        path = self.upload_root / self.attachment.storage_key
        path.unlink(missing_ok=True)

    async def _capture(self) -> CaptureItem:
        return await create_capture(
            self.session,
            CaptureCreate(attachment_id=self.attachment.id),
        )

    async def _count(self, model) -> int:
        return await self.session.scalar(select(func.count()).select_from(model))

    async def test_missing_attachment_stays_failed_without_downstream_objects(self):
        capture = await self._capture()
        (self.upload_root / self.attachment.storage_key).unlink()

        before = {
            model.__name__: await self._count(model)
            for model in (DraftItem, MistakeDraft, Mistake, ReviewItem)
        }

        updated = await trigger_recognition(self.session, capture.id)

        self.assertEqual(updated.status, "failed")
        self.assertEqual(updated.error_code, "attachment_missing")
        for model in (DraftItem, MistakeDraft, Mistake, ReviewItem):
            self.assertEqual(await self._count(model), before[model.__name__])

    async def test_empty_recognized_text_stays_failed_without_draft(self):
        capture = await self._capture()
        capture.status = "recognized"
        capture.recognized_text = ""
        await self.session.flush()

        before = await self._count(DraftItem)
        updated = await trigger_draft(self.session, capture.id)

        self.assertEqual(updated.status, "failed")
        self.assertEqual(updated.error_code, "empty_input")
        self.assertEqual(await self._count(DraftItem), before)


class RecognitionAdapterFailureTest(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_is_mapped_to_safe_error(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(side_effect=RuntimeError("provider timeout")),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "timeout")
        self.assertEqual(result.error_message_safe, "Recognition timed out")

    async def test_provider_failure_result_is_mapped_without_raw_error(self):
        with patch(
            "app.services.capture_recognition.call_vision",
            new=AsyncMock(
                return_value=GatewayCallResult(
                    data=None,
                    provider_used="",
                    model="",
                    latency_ms=1,
                    success=False,
                    fallback_used=False,
                    attempts=[],
                    error="secret provider endpoint and token",
                )
            ),
        ):
            result = await recognize_image(MINIMAL_PNG, "image/png")

        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "provider_error")
        self.assertEqual(result.error_message_safe, "AI provider error")
        self.assertNotIn("secret", result.error_message_safe or "")

    async def test_draft_schema_failure_does_not_become_empty_success(self):
        with patch(
            "app.services.capture_ai_draft.call_text",
            new=AsyncMock(
                return_value=GatewayCallResult(
                    data={"unexpected": "shape"},
                    provider_used="fake",
                    model="fake",
                    latency_ms=1,
                    success=True,
                    fallback_used=False,
                    attempts=[],
                )
            ),
        ):
            result = await draft_mistake(
                CaptureDraftInput(recognized_text="题目文字"),
            )

        self.assertFalse(result.success)
        self.assertIsNone(result.suggestion)
        self.assertEqual(result.error_code, "schema_error")
