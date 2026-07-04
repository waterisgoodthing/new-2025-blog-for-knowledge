from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.taxonomy import ChapterCreate, ChapterOut, ChapterUpdate
from app.services import taxonomy_service

router = APIRouter(
    prefix="/api/chapters",
    tags=["chapters"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: taxonomy_service.TaxonomyError) -> None:
    if isinstance(error, taxonomy_service.TaxonomyNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, taxonomy_service.TaxonomyConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[ChapterOut])
async def list_chapters(
    subject_id: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await taxonomy_service.list_chapters(
        db,
        subject_id=subject_id,
        is_active=is_active,
    )


@router.get("/{chapter_id}", response_model=ChapterOut)
async def get_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await taxonomy_service.get_chapter(db, chapter_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.post("", response_model=ChapterOut, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    payload: ChapterCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.create_chapter(db, payload)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.put("/{chapter_id}", response_model=ChapterOut)
async def update_chapter(
    chapter_id: int,
    payload: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.update_chapter(db, chapter_id, payload)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(chapter_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await taxonomy_service.delete_chapter(db, chapter_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
