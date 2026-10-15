from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.practice import PracticeTodayResponse
from app.services import practice_service

router = APIRouter(
    prefix="/api/admin/practice",
    tags=["practice"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/today", response_model=PracticeTodayResponse)
async def practice_today(
    db: AsyncSession = Depends(get_db),
):
    return await practice_service.get_daily_practice(db)
