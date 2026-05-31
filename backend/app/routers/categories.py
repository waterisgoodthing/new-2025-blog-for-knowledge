from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Category
from app.routers.auth import get_current_admin
from app.schemas.note import CategoryOut, CategoryUpdate, NameCreate

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).order_by(Category.sort_order, Category.name))
    return result.scalars().all()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(req: NameCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    existing = await db.execute(select(Category).where(Category.name == req.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Category already exists")
    category = Category(name=req.name)
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    req: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    if req.name is not None:
        category.name = req.name
    if req.sort_order is not None:
        category.sort_order = req.sort_order
    await db.flush()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
