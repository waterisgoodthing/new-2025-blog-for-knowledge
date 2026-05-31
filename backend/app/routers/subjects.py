from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Subject
from app.routers.auth import get_current_admin
from app.schemas.note import NameCreate, SubjectOut

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectOut])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subject).order_by(Subject.name))
    return result.scalars().all()


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(req: NameCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    existing = await db.execute(select(Subject).where(Subject.name == req.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Subject already exists")
    subject = Subject(name=req.name)
    db.add(subject)
    await db.flush()
    await db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: int, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    await db.delete(subject)
