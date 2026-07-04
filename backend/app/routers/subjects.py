from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.taxonomy import SubjectCreate, SubjectOut, SubjectUpdate
from app.services import taxonomy_service

router = APIRouter(
    prefix="/api/subjects",
    tags=["subjects"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: taxonomy_service.TaxonomyError) -> None:
    if isinstance(error, taxonomy_service.TaxonomyNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, taxonomy_service.TaxonomyConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[SubjectOut])
async def list_subjects(
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await taxonomy_service.list_subjects(db, is_active=is_active)


@router.get("/{subject_id}", response_model=SubjectOut)
async def get_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await taxonomy_service.get_subject(db, subject_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.post("", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.create_subject(db, payload)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.put("/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.update_subject(db, subject_id, payload)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await taxonomy_service.delete_subject(db, subject_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
