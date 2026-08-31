from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.attempt import AttemptCreate, AttemptOut
from app.services import attempt_service

router = APIRouter(prefix="/api/admin/attempts", tags=["admin-attempts"], dependencies=[Depends(get_current_admin)])


@router.post("", response_model=AttemptOut, status_code=status.HTTP_201_CREATED)
async def submit_attempt(payload: AttemptCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        return await attempt_service.submit_attempt(db, payload.question_id, submitted_answer=payload.submitted_answer, created_by=admin.id)
    except attempt_service.AttemptNotFound as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except attempt_service.AttemptConflict as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
