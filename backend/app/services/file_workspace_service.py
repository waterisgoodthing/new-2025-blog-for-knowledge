import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.audit import AuditLog
from app.models.folder import Folder


class FileWorkspaceError(Exception):
    pass


class FileWorkspaceNotFound(FileWorkspaceError):
    pass


class FileWorkspaceConflict(FileWorkspaceError):
    pass


async def _get_active(session: AsyncSession, attachment_id: uuid.UUID) -> Attachment:
    attachment = await session.get(Attachment, attachment_id)
    if attachment is None:
        raise FileWorkspaceNotFound("Attachment not found")
    if attachment.status == "trashed":
        raise FileWorkspaceConflict("Trashed attachment must be restored first")
    if attachment.status == "deleted":
        raise FileWorkspaceNotFound("Attachment not found")
    return attachment


async def _assert_folder(session: AsyncSession, folder_id: uuid.UUID | None) -> None:
    if folder_id is not None and await session.get(Folder, folder_id) is None:
        raise FileWorkspaceNotFound("Folder not found")


async def _assert_name_available(
    session: AsyncSession, *, folder_id: uuid.UUID | None, display_name: str, exclude_id: uuid.UUID
) -> None:
    query = select(Attachment.id).where(
        Attachment.id != exclude_id,
        Attachment.display_name == display_name,
        Attachment.status.in_(["active", "missing"]),
    )
    query = query.where(
        Attachment.folder_id.is_(None) if folder_id is None else Attachment.folder_id == folder_id
    )
    if await session.scalar(query) is not None:
        raise FileWorkspaceConflict("A file with this name already exists in the target folder")


async def _audit(session: AsyncSession, action: str, attachment: Attachment, before: dict, after: dict) -> None:
    session.add(
        AuditLog(
            action=action,
            entity_type="attachment",
            entity_id=str(attachment.id),
            before=before,
            after=after,
        )
    )


async def rename_attachment(session: AsyncSession, attachment_id: uuid.UUID, display_name: str) -> Attachment:
    clean_name = display_name.strip()
    if not clean_name or "/" in clean_name or "\\" in clean_name:
        raise FileWorkspaceConflict("Invalid display name")
    attachment = await _get_active(session, attachment_id)
    await _assert_name_available(session, folder_id=attachment.folder_id, display_name=clean_name, exclude_id=attachment.id)
    before = {"display_name": attachment.display_name}
    attachment.display_name = clean_name
    await session.flush()
    await _audit(session, "file.rename", attachment, before, {"display_name": clean_name})
    return attachment


async def move_attachment(session: AsyncSession, attachment_id: uuid.UUID, folder_id: uuid.UUID | None) -> Attachment:
    attachment = await _get_active(session, attachment_id)
    await _assert_folder(session, folder_id)
    await _assert_name_available(session, folder_id=folder_id, display_name=attachment.display_name, exclude_id=attachment.id)
    before = {"folder_id": str(attachment.folder_id) if attachment.folder_id else None}
    attachment.folder_id = folder_id
    await session.flush()
    await _audit(session, "file.move", attachment, before, {"folder_id": str(folder_id) if folder_id else None})
    return attachment


async def trash_attachment(session: AsyncSession, attachment_id: uuid.UUID) -> Attachment:
    attachment = await _get_active(session, attachment_id)
    before = {"status": attachment.status, "folder_id": str(attachment.folder_id) if attachment.folder_id else None}
    attachment.status = "trashed"
    attachment.trashed_at = datetime.now(timezone.utc)
    await session.flush()
    await _audit(session, "file.trash", attachment, before, {"status": "trashed"})
    return attachment


async def restore_attachment(session: AsyncSession, attachment_id: uuid.UUID) -> Attachment:
    attachment = await session.get(Attachment, attachment_id)
    if attachment is None or attachment.status == "deleted":
        raise FileWorkspaceNotFound("Attachment not found")
    if attachment.status != "trashed":
        raise FileWorkspaceConflict("Attachment is not in the recycle bin")
    await _assert_name_available(session, folder_id=attachment.folder_id, display_name=attachment.display_name, exclude_id=attachment.id)
    before = {"status": attachment.status}
    attachment.status = "active"
    attachment.trashed_at = None
    await session.flush()
    await _audit(session, "file.restore", attachment, before, {"status": "active"})
    return attachment
