from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service


router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["admin-dashboard"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    return await dashboard_service.get_dashboard_summary(
        db,
        upload_root=Path(get_settings().UPLOAD_ROOT),
    )
