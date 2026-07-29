from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.taxonomy import (
    KnowledgePointCreate,
    KnowledgePointOut,
    KnowledgePointUpdate,
)
from app.services import taxonomy_service

router = APIRouter(
    prefix="/api/admin/knowledge-points",
    tags=["knowledge-points"],
    dependencies=[Depends(get_current_admin)],
)


def _raise_http(error: taxonomy_service.TaxonomyError) -> None:
    if isinstance(error, taxonomy_service.TaxonomyNotFound):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, taxonomy_service.TaxonomyConflict):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[KnowledgePointOut])
async def list_knowledge_points(
    subject_id: int | None = None,
    parent_id: int | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await taxonomy_service.list_knowledge_points(
        db,
        subject_id=subject_id,
        parent_id=parent_id,
        status=status,
    )


@router.get("/{knowledge_point_id}", response_model=KnowledgePointOut)
async def get_knowledge_point(
    knowledge_point_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.get_knowledge_point(db, knowledge_point_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.post(
    "",
    response_model=KnowledgePointOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_point(
    payload: KnowledgePointCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.create_knowledge_point(db, payload)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.put("/{knowledge_point_id}", response_model=KnowledgePointOut)
async def update_knowledge_point(
    knowledge_point_id: int,
    payload: KnowledgePointUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.update_knowledge_point(
            db,
            knowledge_point_id,
            payload,
        )
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)


@router.delete("/{knowledge_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_point(
    knowledge_point_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        await taxonomy_service.delete_knowledge_point(db, knowledge_point_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{knowledge_point_id}/archive", response_model=KnowledgePointOut)
async def archive_knowledge_point(
    knowledge_point_id: int,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await taxonomy_service.archive_knowledge_point(db, knowledge_point_id)
    except taxonomy_service.TaxonomyError as error:
        _raise_http(error)
