from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.governance import GovernanceSummary
from app.services.governance_service import get_governance_summary


router = APIRouter(prefix="/api/admin/governance", tags=["admin-governance"], dependencies=[Depends(get_current_admin)])


@router.get("/summary", response_model=GovernanceSummary)
async def governance_summary(db: AsyncSession = Depends(get_db)) -> GovernanceSummary:
    return await get_governance_summary(db)
