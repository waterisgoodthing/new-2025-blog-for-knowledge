from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.knowledge import (
    ContextPackRequest,
    ContextPackResponse,
    WeakPointsResponse,
)
from app.services.knowledge_retrieval import retrieve_context_pack, retrieve_weak_points
from app.services.knowledge_relations import suggest_relations

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.post("/context-pack", response_model=ContextPackResponse)
async def context_pack(
    request: ContextPackRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ContextPackResponse:
    pack = await retrieve_context_pack(db, request)

    all_briefs = pack.related_notes + pack.related_mistakes
    if len(all_briefs) >= 2:
        relations = await suggest_relations(db, all_briefs, limit=10)
        pack.suggested_relations = relations

    return pack


@router.get("/weak-points", response_model=WeakPointsResponse)
async def weak_points(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> WeakPointsResponse:
    return await retrieve_weak_points(db, days=days)
