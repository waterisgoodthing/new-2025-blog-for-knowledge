import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import select

from app.database import async_session, engine
from app.models.attachment import Attachment
from app.models.audit import AuditLog
from app.services.attachment_service import create_attachment_from_bytes
from app.services.file_workspace_service import (
    FileWorkspaceConflict,
    move_attachment,
    rename_attachment,
    restore_attachment,
    trash_attachment,
)


class FileWorkspaceServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.addAsyncCleanup(self.session.rollback)
        await self.session.begin()
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    async def test_rename_trash_restore_and_audit_keep_stable_resource(self):
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="source.txt",
            content=b"hello",
            mime_type="text/plain",
            upload_root=self.root,
        )
        resource_id = attachment.id

        renamed = await rename_attachment(self.session, attachment.id, "renamed.txt")
        self.assertEqual(renamed.id, resource_id)
        self.assertEqual(renamed.display_name, "renamed.txt")

        trashed = await trash_attachment(self.session, attachment.id)
        self.assertEqual(trashed.status, "trashed")
        self.assertTrue((self.root / attachment.storage_key).exists())

        restored = await restore_attachment(self.session, attachment.id)
        self.assertEqual(restored.id, resource_id)
        self.assertEqual(restored.status, "active")

        actions = list(
            (
                await self.session.scalars(
                    select(AuditLog).where(AuditLog.entity_id == str(resource_id))
                )
            ).all()
        )
        self.assertEqual(
            [item.action for item in actions],
            ["file.rename", "file.trash", "file.restore"],
        )

    async def test_rename_conflict_is_rejected_without_mutating_target(self):
        first = await create_attachment_from_bytes(
            self.session,
            original_name="first.txt",
            content=b"one",
            mime_type="text/plain",
            upload_root=self.root,
        )
        second = await create_attachment_from_bytes(
            self.session,
            original_name="second.txt",
            content=b"two",
            mime_type="text/plain",
            upload_root=self.root,
        )
        first.display_name = "same.txt"
        await self.session.flush()

        with self.assertRaises(FileWorkspaceConflict):
            await rename_attachment(self.session, second.id, "same.txt")
        self.assertEqual(second.display_name, "second.txt")

    async def test_move_rejects_trashed_attachment(self):
        attachment = await create_attachment_from_bytes(
            self.session,
            original_name="source.txt",
            content=b"hello",
            mime_type="text/plain",
            upload_root=self.root,
        )
        await trash_attachment(self.session, attachment.id)
        with self.assertRaises(FileWorkspaceConflict):
            await move_attachment(self.session, attachment.id, None)
