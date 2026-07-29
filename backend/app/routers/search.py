from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.search import SearchRequest, SearchResult
from app.services.knowledge_markdown_service import SearchQuery, search_notes

router = APIRouter(prefix="/api/admin/search", tags=["admin-search"])


@router.post("", response_model=list[SearchResult])
async def search_workspace(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    return await search_notes(db, SearchQuery(query=payload.query, limit=payload.limit))
