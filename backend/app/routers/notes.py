from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, status, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.note import Category, Note, Subject, Tag, User
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
    tags = []
    for name in tag_names:
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
        # 非管理员只能查看公开的已发布笔记
        query = query.where(Note.hidden == False)
        query = query.where(Note.status == "published")
    else:
        # 管理员可以自由过滤草稿或隐藏内容
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

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Note.updated_at.desc()).offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    notes = result.scalars().all()

    return NoteListResponse(items=notes, total=total, page=page, size=size)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PUBLIC_PICTURES_DIR = PROJECT_ROOT / "public" / "images" / "pictures"


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    content_type = file.content_type
    if not (content_type and content_type.startswith("image/")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    os.makedirs(PUBLIC_PICTURES_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = PUBLIC_PICTURES_DIR / filename

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 10MB)",
        )
    with open(file_path, "wb") as f:
        f.write(contents)

    return {"url": f"/images/pictures/{filename}"}


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
        if note.hidden or note.status == "draft":
            raise HTTPException(status_code=404, detail="Note not found")

    return note


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    req: NoteCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    existing = await db.execute(select(Note).where(Note.slug == req.slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Slug already exists")

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
        tags=tags,
    )

    if req.type == NoteType.mistake:
        from datetime import date

        note.next_review = date.today()

    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


@router.put("/{slug}", response_model=NoteOut)
async def update_note(
    slug: str,
    req: NoteUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
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

    note.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(note)
    return note


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(slug: str, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Note).where(Note.slug == slug))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
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
    note.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(note)
    return note
