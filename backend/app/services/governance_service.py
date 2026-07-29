from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_profile import AdminProfile
from app.models.ai_call_log import AiCallLog
from app.models.ai_run import AiRun
from app.models.attempt import Attempt
from app.models.audit import AuditLog
from app.models.mistake import Mistake
from app.models.question import Question
from app.models.review_item import ReviewItem
from app.schemas.governance import GovernanceSection, GovernanceSummary


async def _count(session: AsyncSession, model) -> int:
    return int(await session.scalar(select(func.count()).select_from(model)) or 0)


async def get_governance_summary(session: AsyncSession) -> GovernanceSummary:
    ai_runs = await _count(session, AiRun)
    ai_logs = await _count(session, AiCallLog)
    attempts = await _count(session, Attempt)
    questions = await _count(session, Question)
    mistakes = await _count(session, Mistake)
    review_items = await _count(session, ReviewItem)
    audit_logs = await _count(session, AuditLog)
    profiles = await _count(session, AdminProfile)
    return GovernanceSummary(
        generated_at=datetime.now(UTC),
        ai=GovernanceSection(status="ready" if ai_runs or ai_logs else "empty", source="ai_runs + ai_call_logs", count=ai_runs + ai_logs, detail=f"runs={ai_runs}, call_logs={ai_logs}"),
        tasks=GovernanceSection(status="unavailable", source="no persistent task store", count=None, detail="后台任务队列尚未建模；不展示模拟任务。"),
        statistics=GovernanceSection(status="ready" if questions or mistakes or review_items or attempts else "empty", source="questions + mistakes + review_items + attempts", count=questions + mistakes + review_items + attempts, detail=f"questions={questions}, mistakes={mistakes}, review_items={review_items}, attempts={attempts}"),
        report=GovernanceSection(status="ready" if audit_logs else "empty", source="audit_logs", count=audit_logs, detail="审计报告仅汇总已持久化的审计事件。"),
        settings=GovernanceSection(status="ready" if profiles else "empty", source="admin_profiles", count=profiles, detail="管理员偏好由 admin_profiles 提供。"),
    )
