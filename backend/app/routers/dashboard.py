from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.routers.auth import get_current_admin
from app.schemas.dashboard import (
    DashboardCounts,
    DashboardSectionAction,
    DashboardSectionActions,
    DashboardSections,
    DashboardSummary,
    DashboardSystemStatus,
    DashboardTodayFirstAction,
)
from app.services import dashboard_service
from app.services.dashboard_service import (
    FIRST_ACTION_REASON_NOTHING,
    PRACTICE_REASON_UNAVAILABLE,
    PRACTICE_TARGET_ROUTE,
    REVIEW_REASON_UNAVAILABLE,
    REVIEW_TARGET_ROUTE,
)


router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["admin-dashboard"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    try:
        return await dashboard_service.get_dashboard_summary(
            db,
            upload_root=Path(get_settings().UPLOAD_ROOT),
        )
    except SQLAlchemyError:
        await db.rollback()
        return DashboardSummary(
            generated_at=datetime.now(timezone.utc),
            counts=DashboardCounts(questions=0, mistakes=0, knowledge_points=0, attachments=0, due_reviews=0),
            recent_questions=[], recent_mistakes=[], recent_reviews=[],
            sections=DashboardSections(learning="unavailable", activity="unavailable", storage="unknown"),
            system=DashboardSystemStatus(service="ok", database="unavailable", storage="unknown"),
            review_today_count=0,
            practice_today_count=0,
            weak_top3=[],
            recently_mastered_4=[],
            today_first_action=DashboardTodayFirstAction(
                kind="none", count=0, target_route=None, reason=FIRST_ACTION_REASON_NOTHING
            ),
            section_actions=DashboardSectionActions(
                review=DashboardSectionAction(
                    section="review",
                    count=0,
                    available=False,
                    target_route=REVIEW_TARGET_ROUTE,
                    reason=REVIEW_REASON_UNAVAILABLE,
                ),
                practice=DashboardSectionAction(
                    section="practice",
                    count=0,
                    available=False,
                    target_route=PRACTICE_TARGET_ROUTE,
                    reason=PRACTICE_REASON_UNAVAILABLE,
                ),
            ),
        )
