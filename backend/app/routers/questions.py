import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.question import QuestionOut, QuestionUpdate, VersionCommand
from app.services import question_service

router = APIRouter(
    prefix="/api/admin/questions",
    tags=["admin-questions"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: question_service.QuestionError) -> None:
    if isinstance(error, question_service.QuestionNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, question_service.QuestionConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[QuestionOut])
async def list_questions(
    subject_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    return await question_service.list_questions(
        db,
        subject_id=subject_id,
        status=status_filter,
    )


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await question_service.get_question(db, question_id)
    except question_service.QuestionError as error:
        _raise_http(error)


@router.put("/{question_id}", response_model=QuestionOut)
async def update_question(
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await question_service.update_question(db, question_id, payload)
    except question_service.QuestionError as error:
        _raise_http(error)


@router.delete("/{question_id}", response_model=QuestionOut)
async def archive_question(
    question_id: uuid.UUID,
    payload: VersionCommand,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await question_service.archive_question(
            db,
            question_id,
            version=payload.version,
        )
    except question_service.QuestionError as error:
        _raise_http(error)
