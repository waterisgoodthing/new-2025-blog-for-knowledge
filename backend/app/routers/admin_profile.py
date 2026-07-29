from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.admin_profile import AdminProfileOut, AdminProfileUpdate
from app.services import admin_profile_service

router = APIRouter(prefix="/api/admin/profile", tags=["admin-profile"])


@router.get("", response_model=AdminProfileOut)
async def get_admin_profile(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return await admin_profile_service.get_or_create_profile(db, admin.id)
    except admin_profile_service.AdminProfileNotFound as error:
        raise HTTPException(status_code=404, detail="Admin profile owner not found") from error


@router.put("", response_model=AdminProfileOut)
async def put_admin_profile(
    payload: AdminProfileUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        return await admin_profile_service.update_profile(db, admin.id, payload)
    except admin_profile_service.AdminProfileNotFound as error:
        raise HTTPException(status_code=404, detail="Admin profile owner not found") from error
