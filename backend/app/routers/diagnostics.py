from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.diagnostics import DiagnosticsResponse
from app.services.diagnostics_service import get_diagnostics


router = APIRouter(
    prefix="/api/admin/diagnostics",
    tags=["admin-diagnostics"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=DiagnosticsResponse)
async def diagnostics(db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    auth_bypass_active = (
        settings.AUTH_BYPASS.lower() == "true"
        and settings.AUTH_BYPASS_ALLOW.lower() == "true"
    )
    return await get_diagnostics(
        db,
        upload_root=Path(settings.UPLOAD_ROOT),
        auth_bypass_active=auth_bypass_active,
    )
