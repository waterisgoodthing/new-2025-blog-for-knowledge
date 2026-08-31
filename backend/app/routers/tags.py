from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Tag, note_tags
from app.routers.auth import get_current_admin
from app.schemas.note import NameCreate, TagOut

router = APIRouter(prefix="/api/tags", tags=["tags"])


def _canonical_tag_or_400(name: str) -> str:
    from app.services.tag_canonicalization import canonicalize_tag

    canonical_name = canonicalize_tag(name)
    if not canonical_name:
        raise HTTPException(status_code=400, detail="Tag name is too generic or low-value")
    return canonical_name


class TagRenameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class TagMergeRequest(BaseModel):
    target_tag_id: int


@router.get("", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(req: NameCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    canonical_name = _canonical_tag_or_400(req.name)
    existing = await db.execute(select(Tag).where(Tag.name == canonical_name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Tag already exists")
    tag = Tag(name=canonical_name)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=TagOut)
async def rename_tag(
    tag_id: int,
    req: TagRenameRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    canonical_name = _canonical_tag_or_400(req.name)
    existing = await db.execute(select(Tag).where(Tag.name == canonical_name, Tag.id != tag_id))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Tag name already exists. Use merge instead.")

    tag.name = canonical_name
    db.add(tag)
    await db.flush()
    await db.refresh(tag)

    from app.services.audit_service import audit_action
    await audit_action(db, action="rename", session_token=session_token, request=request, entity_type="tag", entity_id=str(tag_id), after={"name": tag.name})

    return tag


@router.post("/{tag_id}/merge", response_model=TagOut)
async def merge_tag(
    tag_id: int,
    req: TagMergeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    if tag_id == req.target_tag_id:
        raise HTTPException(status_code=400, detail="Cannot merge a tag into itself")

    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    source_tag = result.scalar_one_or_none()
    if source_tag is None:
        raise HTTPException(status_code=404, detail="Source tag not found")

    result = await db.execute(select(Tag).where(Tag.id == req.target_tag_id))
    target_tag = result.scalar_one_or_none()
    if target_tag is None:
        raise HTTPException(status_code=404, detail="Target tag not found")

    source_name = source_tag.name
    target_name = target_tag.name

    overlapping = select(note_tags.c.note_id).where(
        note_tags.c.tag_id == req.target_tag_id
    )

    await db.execute(
        note_tags.delete().where(
            note_tags.c.tag_id == tag_id,
            note_tags.c.note_id.in_(overlapping),
        )
    )

    await db.execute(
        note_tags.update()
        .where(note_tags.c.tag_id == tag_id)
        .values(tag_id=req.target_tag_id)
    )

    await db.delete(source_tag)
    await db.flush()
    await db.refresh(target_tag)

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="merge", session_token=session_token, request=request,
        entity_type="tag", entity_id=str(tag_id),
        before={"source": source_name, "target": target_name},
    )

    return target_tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    from app.services.audit_service import audit_action
    await audit_action(db, action="delete", session_token=session_token, request=request, entity_type="tag", entity_id=str(tag_id), before={"name": tag.name})

    await db.delete(tag)
