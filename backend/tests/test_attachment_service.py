import unittest
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import ValidationError
from sqlalchemy import select

from app.database import async_session, engine
from app.models.attachment import Attachment
from app.models.question import Question
from app.schemas.attachment import (
    AttachmentLinkCreate,
    AttachmentUploadCreate,
)
from app.services.attachment_service import (
    AttachmentConflict,
    AttachmentNotFound,
    AttachmentValidationError,
    create_attachment_link,
    create_attachment_from_bytes,
    delete_attachment,
    delete_attachment_link,
    get_attachment_content_path,
    list_attachment_links,
)
from app.schemas.question import QuestionDraftCreate
from app.schemas.taxonomy import SubjectCreate
from app.services.draft_service import convert_question_draft, create_question_draft
from app.services.taxonomy_service import create_subject


class AttachmentSchemaTest(unittest.TestCase):
    def test_upload_contract_cleans_name_and_keeps_storage_private(self):
        payload = AttachmentUploadCreate(
            original_name="  screenshot.png  ",
            mime_type="image/png",
            size_bytes=12,
            checksum_sha256="a" * 64,
        )

        self.assertEqual(payload.original_name, "screenshot.png")
        self.assertEqual(payload.storage_provider, "local")
        self.assertEqual(payload.visibility, "private")

        with self.assertRaises(ValidationError):
            AttachmentUploadCreate(
                original_name="../secret.png",
                mime_type="image/png",
                size_bytes=12,
                checksum_sha256="a" * 64,
            )

        with self.assertRaises(ValidationError):
            AttachmentUploadCreate(
                original_name="script.sh",
                mime_type="application/x-sh",
                size_bytes=12,
                checksum_sha256="a" * 64,
            )

    def test_link_contract_allows_only_learning_targets(self):
        attachment_id = uuid.uuid4()
        target_id = uuid.uuid4()
        payload = AttachmentLinkCreate(
            attachment_id=attachment_id,
            target_type="question",
            target_id=target_id,
            purpose="source",
        )

        self.assertEqual(payload.attachment_id, attachment_id)
        self.assertEqual(payload.target_type, "question")
        self.assertEqual(str(payload.target_id), str(target_id))

        with self.assertRaises(ValidationError):
            AttachmentLinkCreate(
                attachment_id=attachment_id,
                target_type="note",
                target_id=target_id,
                purpose="source",
            )

        with self.assertRaises(ValidationError):
            AttachmentLinkCreate(
                attachment_id=attachment_id,
                target_type="question",
                target_id=target_id,
                purpose="avatar",
            )


class AttachmentServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        await self.session.begin()
        self.tmp = TemporaryDirectory()
        self.upload_root = Path(self.tmp.name)

    async def asyncTearDown(self):
        await self.session.rollback()
        await self.session.close()
        await engine.dispose()
        self.tmp.cleanup()

    async def test_upload_persists_private_metadata_without_absolute_path(self):
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="proof.png",
            content=b"png-bytes",
            mime_type="image/png",
            upload_root=self.upload_root,
        )

        self.assertEqual(attachment.original_name, "proof.png")
        self.assertEqual(attachment.storage_provider, "local")
        self.assertEqual(attachment.visibility, "private")
        self.assertEqual(attachment.status, "active")
        self.assertNotIn(str(self.upload_root), attachment.storage_key)
        self.assertFalse(Path(attachment.storage_key).is_absolute())

        stored = self.upload_root / attachment.storage_key
        self.assertTrue(stored.exists())
        self.assertEqual(stored.read_bytes(), b"png-bytes")

        row = await self.session.scalar(select(Attachment).where(Attachment.id == attachment.id))
        self.assertEqual(row.storage_key, attachment.storage_key)

    async def test_content_path_is_resolved_from_storage_key_only(self):
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="source.txt",
            content=b"hello",
            mime_type="text/plain",
            upload_root=self.upload_root,
        )

        resolved = await get_attachment_content_path(
            self.session,
            attachment.id,
            upload_root=self.upload_root,
        )
        self.assertEqual(resolved.read_bytes(), b"hello")

        attachment.storage_key = "../escape.txt"
        await self.session.flush()
        with self.assertRaises(AttachmentValidationError):
            await get_attachment_content_path(
                self.session,
                attachment.id,
                upload_root=self.upload_root,
            )

    async def test_missing_and_deleted_files_are_reported_without_path_leak(self):
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="source.txt",
            content=b"hello",
            mime_type="text/plain",
            upload_root=self.upload_root,
        )
        (self.upload_root / attachment.storage_key).unlink()

        with self.assertRaises(AttachmentNotFound) as missing:
            await get_attachment_content_path(
                self.session,
                attachment.id,
                upload_root=self.upload_root,
            )
        self.assertNotIn(str(self.upload_root), str(missing.exception))
        self.assertEqual(attachment.status, "missing")

        deleted = await delete_attachment(
            self.session,
            attachment.id,
            upload_root=self.upload_root,
        )
        self.assertEqual(deleted.status, "deleted")
        with self.assertRaises(AttachmentNotFound):
            await get_attachment_content_path(
                self.session,
                attachment.id,
                upload_root=self.upload_root,
            )

    async def _question(self):
        subject = await create_subject(
            self.session,
            SubjectCreate(name="Attachment Subject"),
        )
        draft = await create_question_draft(
            self.session,
            QuestionDraftCreate(
                subject_id=subject.id,
                question_text="Attachment question?",
                question_type="short_answer",
            ),
        )
        question = await convert_question_draft(self.session, draft.item.id, version=1)
        return draft, question

    async def test_attachment_links_validate_target_and_prevent_duplicates(self):
        _draft, question = await self._question()
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="proof.png",
            content=b"png-bytes",
            mime_type="image/png",
            upload_root=self.upload_root,
        )

        link = await create_attachment_link(
            self.session,
            AttachmentLinkCreate(
                attachment_id=attachment.id,
                target_type="question",
                target_id=question.id,
                purpose="source",
            ),
        )
        self.assertEqual(link.target_type, "question")
        self.assertEqual(link.target_id, str(question.id))

        links = await list_attachment_links(
            self.session,
            target_type="question",
            target_id=question.id,
        )
        self.assertEqual([item.id for item in links], [link.id])

        with self.assertRaises(AttachmentConflict):
            await create_attachment_link(
                self.session,
                AttachmentLinkCreate(
                    attachment_id=attachment.id,
                    target_type="question",
                    target_id=question.id,
                    purpose="source",
                ),
            )

        await delete_attachment_link(self.session, link.id)
        self.assertEqual(
            await list_attachment_links(
                self.session,
                target_type="question",
                target_id=question.id,
            ),
            [],
        )

    async def test_attachment_links_reject_missing_targets_and_deleted_attachments(self):
        _draft, question = await self._question()
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="proof.png",
            content=b"png-bytes",
            mime_type="image/png",
            upload_root=self.upload_root,
        )

        with self.assertRaises(AttachmentNotFound):
            await create_attachment_link(
                self.session,
                AttachmentLinkCreate(
                    attachment_id=attachment.id,
                    target_type="question",
                    target_id=uuid.uuid4(),
                    purpose="source",
                ),
            )

        await delete_attachment(self.session, attachment.id, upload_root=self.upload_root)
        with self.assertRaises(AttachmentConflict):
            await create_attachment_link(
                self.session,
                AttachmentLinkCreate(
                    attachment_id=attachment.id,
                    target_type="question",
                    target_id=question.id,
                    purpose="source",
                ),
            )
