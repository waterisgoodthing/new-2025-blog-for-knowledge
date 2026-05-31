from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.recommendation import DailyRecommendation
from app.routers.auth import get_current_admin
from app.schemas.recommendation import DailyRecommendationOut, RecommendationHistoryItem
from app.services.recommendation import get_or_create_today_recommendation

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/today", response_model=DailyRecommendationOut)
async def get_today_recommendation(db: AsyncSession = Depends(get_db)):
    return await get_or_create_today_recommendation(db)


@router.delete("/today")
async def delete_today_recommendation(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    today = date.today()
    result = await db.execute(select(DailyRecommendation).where(DailyRecommendation.date == today))
    rec = result.scalar_one_or_none()
    if rec is None:
        raise HTTPException(status_code=404, detail="No recommendation for today")
    await db.delete(rec)
    return {"ok": True}


@router.get("/history", response_model=list[RecommendationHistoryItem])
async def get_recommendation_history(
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyRecommendation).order_by(DailyRecommendation.date.desc()).limit(limit)
    )
    return result.scalars().all()
