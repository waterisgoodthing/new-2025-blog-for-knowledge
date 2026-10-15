import unittest
from pathlib import Path

from sqlalchemy import select

from app.config import get_settings
from app.database import async_session, engine
from app.models.attachment import AttachmentLink
from app.models.mistake import MistakeDraft
from app.models.question import DraftItem
from app.schemas.capture import CaptureConvert, CaptureCreate
from app.schemas.taxonomy import KnowledgePointCreate, SubjectCreate
from app.services.attachment_service import create_attachment_from_bytes
from app.services.capture_service import (
    convert_capture,
    create_capture,
    trigger_draft,
    trigger_recognition,
)
from app.services.taxonomy_service import create_knowledge_point, create_subject


MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)


class CaptureDraftChainTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.subject = await create_subject(
            self.session,
            SubjectCreate(name="I6 Chain Subject"),
        )
        self.knowledge_point = await create_knowledge_point(
            self.session,
            KnowledgePointCreate(subject_id=self.subject.id, name="I6 Chain Point"),
        )
        self.attachment = await create_attachment_from_bytes(
            self.session,
            original_name="i6-chain.png",
            content=MINIMAL_PNG,
            mime_type="image/png",
        )
        self.upload_root = Path(get_settings().UPLOAD_ROOT)
        self.addCleanup(self._cleanup_attachment_file)

    def _cleanup_attachment_file(self):
        (self.upload_root / self.attachment.storage_key).unlink(missing_ok=True)

    async def test_capture_draft_chain_preserves_source_and_target_links(self):
        capture = await create_capture(
            self.session,
            CaptureCreate(attachment_id=self.attachment.id),
        )
        await trigger_recognition(
            self.session,
            capture.id,
            use_fake=True,
            fake_text="I6 source question",
        )
        await trigger_draft(self.session, capture.id, use_fake=True)

        result = await convert_capture(
            self.session,
            capture.id,
            CaptureConvert(
                subject_id=self.subject.id,
                question_text="I6 confirmed question",
                knowledge_point_ids=[self.knowledge_point.id],
            ),
        )

        draft_item = await self.session.get(DraftItem, result.mistake_draft_item_id)
        self.assertIsNotNone(draft_item)
        self.assertEqual(draft_item.status, "pending")
        self.assertEqual(draft_item.target_id, None)

        mistake_draft = await self.session.scalar(
            select(MistakeDraft).where(
                MistakeDraft.draft_item_id == result.mistake_draft_item_id
            )
        )
        self.assertIsNotNone(mistake_draft)
        self.assertEqual(mistake_draft.question_draft_id, result.question_draft_id)

        source_link = await self.session.scalar(
            select(AttachmentLink).where(
                AttachmentLink.attachment_id == self.attachment.id,
                AttachmentLink.target_type == "question_draft",
                AttachmentLink.target_id == str(result.question_draft_id),
                AttachmentLink.purpose == "source",
            )
        )
        self.assertIsNotNone(source_link)
        self.assertEqual(capture.mistake_draft_item_id, result.mistake_draft_item_id)
