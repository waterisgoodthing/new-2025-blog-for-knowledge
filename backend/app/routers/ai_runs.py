import uuid

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.ai_run import (
    AiRunDecisionRequest,
    AiRunDetail,
    AiRunListResponse,
    AiRunRetryRequest,
)
from app.services import ai_run_service


router = APIRouter(
    prefix="/api/admin/ai/runs",
    tags=["admin-ai-runs"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: Exception) -> None:
    if isinstance(error, ai_run_service.AiRunNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, ai_run_service.AiRunConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=AiRunListResponse)
async def list_ai_runs(
    task_type: str | None = None,
    status: str | None = None,
    validation_status: str | None = None,
    review_status: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await ai_run_service.query_ai_runs(
        db,
        task_type=task_type,
        status=status,
        validation_status=validation_status,
        review_status=review_status,
        limit=limit,
        offset=offset,
    )
    return AiRunListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{run_id}", response_model=AiRunDetail)
async def get_ai_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ai_run_service.get_ai_run(db, run_id)
    except Exception as error:
        _raise_http(error)


@router.post("/{run_id}/retry", response_model=AiRunDetail)
async def retry_ai_run(
    run_id: uuid.UUID,
    _payload: AiRunRetryRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        parent = await ai_run_service.get_ai_run(db, run_id)
        return await ai_run_service.retry_ai_run(db, parent)
    except Exception as error:
        _raise_http(error)


@router.post("/{run_id}/decision", response_model=AiRunDetail)
async def decide_ai_run(
    run_id: uuid.UUID,
    payload: AiRunDecisionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    try:
        run = await ai_run_service.get_ai_run(db, run_id)
        return await ai_run_service.decide_ai_run(
            db,
            run,
            decision=payload.decision,
            expected_revision=payload.expected_revision,
            note=payload.note,
            session_token=session_token,
            request=request,
        )
    except Exception as error:
        _raise_http(error)
