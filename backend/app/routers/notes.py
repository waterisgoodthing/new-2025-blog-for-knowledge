from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Optional
import uuid

from app.utils.datetime import utc_now_naive

from fastapi import APIRouter, Cookie, Depends, File, HTTPException, Query, Request, status, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.folder import Folder
from app.models.note import Category, Note, Subject, Tag, User
from app.config import get_settings
from app.routers.auth import get_current_user, get_optional_user, get_current_admin
from app.schemas.note import (
    CategoryOut,
    CategoryUpdate,
    NameCreate,
    NoteCreate,
    NoteListItem,
    NoteListResponse,
    NoteOut,
    NoteStatus,
    NoteType,
    NoteUpdate,
    SubjectOut,
    TagOut,
)

router = APIRouter(prefix="/api/notes", tags=["notes"])


async def _get_or_create_tags(db: AsyncSession, tag_names: list[str]) -> list[Tag]:
    from app.services.tag_canonicalization import canonicalize_tags
    cleaned = canonicalize_tags(tag_names)
    tags = []
    for name in cleaned:
        result = await db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
            await db.flush()
        tags.append(tag)
    return tags


@router.get("", response_model=NoteListResponse)
async def list_notes(
    type: Optional[NoteType] = None,
    tag: Optional[str] = None,
    subject: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    status: Optional[NoteStatus] = None,
    q: Optional[str] = None,
    hidden: Optional[bool] = None,
    folder_id: Optional[str] = None,
    inbox: Optional[bool] = None,
    featured: Optional[bool] = None,
    sort_by: Optional[str] = Query(None, pattern="^(sort_order|updated_at)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    query = select(Note).options(selectinload(Note.tags))

    is_admin = False
    if current_user is not None:
        is_admin = getattr(current_user, "is_admin", False)

    if type:
        query = query.where(Note.type == type.value)

    if not is_admin:
        query = query.where(Note.hidden == False)
        query = query.where(Note.status == "published")
    else:
        if status:
            query = query.where(Note.status == status.value)
        if hidden is not None:
            query = query.where(Note.hidden == hidden)

    if subject:
        query = query.where(Note.subject == subject)
    if category:
        query = query.where(Note.category == category)
    if difficulty:
        query = query.where(Note.difficulty == difficulty)
    if tag:
        query = query.join(Note.tags).where(Tag.name == tag)
    if q:
        query = query.where(
            or_(
                Note.title.ilike(f"%{q}%"),
                Note.content.ilike(f"%{q}%"),
                Note.question.ilike(f"%{q}%"),
            )
        )
    if folder_id is not None:
        import uuid as _uuid
        try:
            query = query.where(Note.folder_id == _uuid.UUID(folder_id))
        except ValueError:
            pass
    if inbox:
        query = query.where(Note.folder_id.is_(None))
    if featured:
        query = query.where(Note.sort_order > 0)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    if sort_by == "sort_order":
        query = query.order_by(Note.sort_order.desc(), Note.updated_at.desc())
    else:
        query = query.order_by(Note.updated_at.desc())
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    notes = result.scalars().all()

    return NoteListResponse(items=notes, total=total, page=page, size=size)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PUBLIC_PICTURES_DIR = PROJECT_ROOT / "public" / "images" / "pictures"
MAX_IMAGE_UPLOAD_BYTES = 10 * 1024 * 1024
UPLOAD_CHUNK_BYTES = 1024 * 1024


def _image_extension_from_header(header: bytes) -> str | None:
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return ".webp"
    return None


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    note_type: Optional[str] = None,
    slug: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    content_type = file.content_type
    if not (content_type and content_type.startswith("image/")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    header = await file.read(12)
    ext = _image_extension_from_header(header)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PNG, JPEG, GIF, or WebP image",
        )

    if len(header) > MAX_IMAGE_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 10MB)",
        )

    if note_type and slug:
        safe_type = note_type.replace("/", "_").replace("..", "")
        safe_slug = slug.replace("/", "_").replace("..", "")
        upload_dir = PUBLIC_PICTURES_DIR / safe_type / safe_slug
        filename = f"{uuid.uuid4().hex[:8]}{ext}"
    else:
        upload_dir = PUBLIC_PICTURES_DIR
        filename = f"{uuid.uuid4().hex}{ext}"

    os.makedirs(upload_dir, exist_ok=True)
    file_path = upload_dir / filename

    total_bytes = len(header)
    try:
        with open(file_path, "wb") as f:
            f.write(header)
            while True:
                chunk = await file.read(UPLOAD_CHUNK_BYTES)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_IMAGE_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File too large (max 10MB)",
                    )
                f.write(chunk)
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    if note_type and slug:
        safe_type = note_type.replace("/", "_").replace("..", "")
        safe_slug = slug.replace("/", "_").replace("..", "")
        return {"url": f"{get_settings().IMAGE_BASE_URL}/images/pictures/{safe_type}/{safe_slug}/{filename}"}
    return {"url": f"{get_settings().IMAGE_BASE_URL}/images/pictures/{filename}"}


@router.get("/{slug}", response_model=NoteOut)
async def get_note(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    result = await db.execute(select(Note).options(selectinload(Note.tags)).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    is_admin = False
    if current_user is not None:
        is_admin = getattr(current_user, "is_admin", False)

    if not is_admin:
        if note.hidden or note.status != "published":
            raise HTTPException(status_code=404, detail="Note not found")

    return note


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    req: NoteCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    existing = await db.execute(select(Note).where(Note.slug == req.slug))
    if existing.scalar_one_or_none() is not None:
        from app.utils.slug import ensure_unique_slug
        req.slug = await ensure_unique_slug(db, req.slug)

    if req.folder_id is not None:
        folder = await db.get(Folder, req.folder_id)
        if folder is None:
            raise HTTPException(status_code=404, detail="Folder not found")

    tags = await _get_or_create_tags(db, req.tags)

    note = Note(
        slug=req.slug,
        title=req.title,
        content=req.content,
        type=req.type.value,
        status=req.status.value,
        hidden=req.hidden,
        summary=req.summary,
        cover=req.cover,
        category=req.category,
        subject=req.subject,
        difficulty=req.difficulty.value if req.difficulty else None,
        question=req.question,
        my_answer=req.my_answer,
        correct_answer=req.correct_answer,
        analysis=req.analysis,
        knowledge_points=req.knowledge_points,
        images=req.images,
        ai_metadata=req.ai_metadata,
        folder_id=req.folder_id,
        sort_order=req.sort_order,
        tags=tags,
    )

    if req.type == NoteType.mistake:
        from datetime import date

        note.next_review = date.today()

    db.add(note)
    await db.flush()
    await db.refresh(note)

    from app.services.audit_service import audit_action
    await audit_action(
        db,
        action="create",
        session_token=session_token,
        request=request,
        entity_type=note.type,
        entity_id=str(note.id),
        after={"slug": note.slug, "title": note.title, "folder_id": str(note.folder_id) if note.folder_id else None},
    )

    return note


@router.put("/{slug}", response_model=NoteOut)
async def update_note(
    slug: str,
    req: NoteUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    result = await db.execute(select(Note).options(selectinload(Note.tags)).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = req.model_dump(exclude_unset=True)
    tags_data = update_data.pop("tags", None)

    if tags_data is not None:
        note.tags = await _get_or_create_tags(db, tags_data)

    for key, value in update_data.items():
        if key == "difficulty" and value is not None:
            value = value.value if hasattr(value, "value") else value
        if key == "type" and value is not None:
            value = value.value if hasattr(value, "value") else value
        setattr(note, key, value)

    note.updated_at = utc_now_naive()
    await db.flush()
    await db.refresh(note)

    from app.services.audit_service import audit_action
    await audit_action(
        db,
        action="update",
        session_token=session_token,
        request=request,
        entity_type=note.type,
        entity_id=str(note.id),
        after={"slug": note.slug, "title": note.title},
    )

    return note


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    result = await db.execute(select(Note).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    from app.services.audit_service import audit_action
    await audit_action(
        db,
        action="delete",
        session_token=session_token,
        request=request,
        entity_type=note.type,
        entity_id=str(note.id),
        before={"slug": note.slug, "title": note.title},
    )

    await db.delete(note)


@router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_notes(slugs: list[str], db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Note).where(Note.slug.in_(slugs)))
    notes = result.scalars().all()
    for note in notes:
        await db.delete(note)


@router.post("/{slug}/promote", response_model=NoteOut)
async def promote_note(
    slug: str,
    new_type: NoteType,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(Note).options(selectinload(Note.tags)).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    note.type = new_type.value
    if new_type == NoteType.mistake and note.next_review is None:
        from datetime import date

        note.next_review = date.today()
    note.updated_at = utc_now_naive()
    await db.flush()
    await db.refresh(note)
    return note
