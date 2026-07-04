import hashlib
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.attachment import Attachment, AttachmentLink
from app.models.mistake import Mistake
from app.models.question import Question, QuestionDraft
from app.schemas.attachment import ALLOWED_MIME_TYPES, AttachmentLinkCreate


class AttachmentError(Exception):
    pass


class AttachmentNotFound(AttachmentError):
    pass


class AttachmentConflict(AttachmentError):
    pass


class AttachmentValidationError(AttachmentError):
    pass


def _upload_root(root: Path | str | None = None) -> Path:
    return Path(root if root is not None else get_settings().UPLOAD_ROOT).resolve()


def _storage_key(original_name: str) -> str:
    suffix = Path(original_name).suffix.lower()
    item_id = uuid.uuid4()
    return f"{item_id.hex[:2]}/{item_id}{suffix}"


def _safe_original_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned or "/" in cleaned or "\\" in cleaned or cleaned in {".", ".."}:
        raise AttachmentValidationError("Invalid file name")
    return cleaned


def _safe_content_path(root: Path, storage_key: str) -> Path:
    candidate = (root / storage_key).resolve()
    if candidate != root and root not in candidate.parents:
        raise AttachmentValidationError("Invalid storage key")
    return candidate


def _validate_mime(mime_type: str) -> str:
    cleaned = mime_type.strip().lower()
    if cleaned not in ALLOWED_MIME_TYPES:
        raise AttachmentValidationError("Unsupported attachment type")
    return cleaned


async def create_attachment_from_bytes(
    session: AsyncSession,
    *,
    original_name: str,
    content: bytes,
    mime_type: str,
    upload_root: Path | str | None = None,
    created_by=None,
) -> Attachment:
    if not content:
        raise AttachmentValidationError("Attachment must not be empty")
    settings = get_settings()
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise AttachmentValidationError("Attachment is too large")

    clean_name = _safe_original_name(original_name)
    clean_mime = _validate_mime(mime_type)
    root = _upload_root(upload_root)
    root.mkdir(parents=True, exist_ok=True)

    checksum = hashlib.sha256(content).hexdigest()
    storage_key = _storage_key(clean_name)
    destination = _safe_content_path(root, storage_key)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")

    try:
        temporary.write_bytes(content)
        temporary.replace(destination)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        raise

    attachment = Attachment(
        original_name=clean_name,
        storage_provider="local",
        storage_key=storage_key,
        mime_type=clean_mime,
        size_bytes=len(content),
        checksum_sha256=checksum,
        visibility="private",
        status="active",
        created_by=created_by,
    )
    session.add(attachment)
    try:
        await session.flush()
    except Exception:
        if destination.exists():
            destination.unlink()
        raise
    await session.refresh(attachment)
    return attachment


async def list_attachments(
    session: AsyncSession,
    *,
    status: str | None = None,
) -> list[Attachment]:
    statement = select(Attachment)
    if status is not None:
        statement = statement.where(Attachment.status == status)
    result = await session.execute(statement.order_by(Attachment.created_at.desc()))
    return list(result.scalars().all())


async def get_attachment(session: AsyncSession, attachment_id: uuid.UUID) -> Attachment:
    attachment = await session.get(Attachment, attachment_id)
    if attachment is None:
        raise AttachmentNotFound("Attachment not found")
    return attachment


async def get_attachment_content_path(
    session: AsyncSession,
    attachment_id: uuid.UUID,
    *,
    upload_root: Path | str | None = None,
) -> Path:
    attachment = await get_attachment(session, attachment_id)
    if attachment.status == "deleted":
        raise AttachmentNotFound("Attachment not found")
    root = _upload_root(upload_root)
    path = _safe_content_path(root, attachment.storage_key)
    if not path.exists():
        attachment.status = "missing"
        await session.flush()
        raise AttachmentNotFound("Attachment file missing")
    return path


async def delete_attachment(
    session: AsyncSession,
    attachment_id: uuid.UUID,
    *,
    upload_root: Path | str | None = None,
) -> Attachment:
    attachment = await get_attachment(session, attachment_id)
    if attachment.status == "deleted":
        return attachment
    attachment.status = "deleted"
    await session.flush()
    await session.refresh(attachment)
    return attachment


async def _target_exists(
    session: AsyncSession,
    target_type: str,
    target_id: uuid.UUID,
) -> bool:
    model = {
        "question_draft": QuestionDraft,
        "question": Question,
        "mistake": Mistake,
    }.get(target_type)
    if model is None:
        raise AttachmentValidationError("Unsupported attachment target type")
    return await session.get(model, target_id) is not None


async def create_attachment_link(
    session: AsyncSession,
    payload: AttachmentLinkCreate,
) -> AttachmentLink:
    attachment = await get_attachment(session, payload.attachment_id)
    if attachment.status != "active":
        raise AttachmentConflict("Attachment is not active")
    if not await _target_exists(session, payload.target_type, payload.target_id):
        raise AttachmentNotFound("Attachment target not found")
    duplicate = await session.scalar(
        select(AttachmentLink).where(
            AttachmentLink.attachment_id == payload.attachment_id,
            AttachmentLink.target_type == payload.target_type,
            AttachmentLink.target_id == str(payload.target_id),
            AttachmentLink.purpose == payload.purpose,
        )
    )
    if duplicate is not None:
        raise AttachmentConflict("Attachment link already exists")

    link = AttachmentLink(
        attachment_id=payload.attachment_id,
        target_type=payload.target_type,
        target_id=str(payload.target_id),
        purpose=payload.purpose,
        sort_order=payload.sort_order,
    )
    session.add(link)
    try:
        await session.flush()
    except IntegrityError as error:
        raise AttachmentConflict("Attachment link already exists") from error
    await session.refresh(link)
    return link


async def list_attachment_links(
    session: AsyncSession,
    *,
    target_type: str | None = None,
    target_id: uuid.UUID | str | None = None,
    attachment_id: uuid.UUID | None = None,
) -> list[AttachmentLink]:
    statement = select(AttachmentLink)
    if target_type is not None:
        statement = statement.where(AttachmentLink.target_type == target_type)
    if target_id is not None:
        statement = statement.where(AttachmentLink.target_id == str(target_id))
    if attachment_id is not None:
        statement = statement.where(AttachmentLink.attachment_id == attachment_id)
    result = await session.execute(statement.order_by(AttachmentLink.sort_order, AttachmentLink.created_at))
    return list(result.scalars().all())


async def delete_attachment_link(
    session: AsyncSession,
    link_id: uuid.UUID,
) -> None:
    link = await session.get(AttachmentLink, link_id)
    if link is None:
        raise AttachmentNotFound("Attachment link not found")
    await session.delete(link)
    await session.flush()
