from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Tag
from app.routers.auth import get_current_admin
from app.schemas.note import NameCreate, TagOut

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.post("", response_model=TagOut, status_code=status.HTTP_201_CREATED)
async def create_tag(req: NameCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    existing = await db.execute(select(Tag).where(Tag.name == req.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Tag already exists")
    tag = Tag(name=req.name)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    await db.delete(tag)
