"""AI 调用日志查询服务。

提供调用日志的分页查询和聚合统计，为 /manage/ai 页面提供数据。
不暴露 input_summary（安全考虑）。
"""

from sqlalchemy import cast, func, select
from sqlalchemy.types import Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_call_log import AiCallLog


def _provider_health_status(
    *,
    call_count: int,
    failure_rate: float,
    fallback_rate: float,
) -> tuple[str, str]:
    if call_count <= 0:
        return "unknown", "no recent ai_call_logs samples"
    if failure_rate >= 0.3:
        return "degraded", f"failure_rate={failure_rate:.2f} exceeds threshold 0.30"
    if fallback_rate >= 0.3:
        return "degraded", f"fallback_rate={fallback_rate:.2f} exceeds threshold 0.30"
    return "healthy", "recent ai_call_logs are within thresholds"


async def query_call_logs(
    db: AsyncSession,
    *,
    task_type: str | None = None,
    success: bool | None = None,
    provider: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[AiCallLog]:
    """查询调用日志（按 created_at 降序）。"""
    stmt = select(AiCallLog).order_by(AiCallLog.created_at.desc())
    if task_type:
        stmt = stmt.where(AiCallLog.task_type == task_type)
    if success is not None:
        stmt = stmt.where(AiCallLog.success == success)
    if provider:
        stmt = stmt.where(AiCallLog.provider_used == provider)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def query_call_log_stats(db: AsyncSession) -> list[dict]:
    """按 task_type 聚合统计（总数/成功数/平均延迟）。"""
    stmt = (
        select(
            AiCallLog.task_type,
            func.count().label("total"),
            func.count().filter(AiCallLog.success == True).label("success_count"),  # noqa: E712
            func.avg(AiCallLog.latency_ms).label("avg_latency_ms"),
        )
        .group_by(AiCallLog.task_type)
        .order_by(AiCallLog.task_type)
    )
    result = await db.execute(stmt)
    return [
        {
            "task_type": row.task_type,
            "total": row.total,
            "success_count": row.success_count,
            "avg_latency_ms": round(row.avg_latency_ms or 0, 1),
        }
        for row in result
    ]


async def query_usage_cost_stats(db: AsyncSession) -> list[dict]:
    """按日期/task/provider/model 聚合 usage/cost 可观测性。

    当前 `ai_call_logs` 没有 token usage/cost 字段，因此 token/cost 只能
    返回 None，并明确标记 source=unknown。不得用字符数或请求数伪造。
    """
    day_expr = cast(AiCallLog.created_at, Date).label("day")
    stmt = (
        select(
            day_expr,
            AiCallLog.task_type,
            AiCallLog.provider_used,
            AiCallLog.model,
            func.count().label("call_count"),
            func.count().filter(AiCallLog.success == True).label("success_count"),  # noqa: E712
            func.count().filter(AiCallLog.fallback_used == True).label("fallback_count"),  # noqa: E712
            func.avg(AiCallLog.latency_ms).label("avg_latency_ms"),
        )
        .group_by(
            day_expr,
            AiCallLog.task_type,
            AiCallLog.provider_used,
            AiCallLog.model,
        )
        .order_by(
            day_expr.desc(),
            AiCallLog.task_type,
            AiCallLog.provider_used,
            AiCallLog.model,
        )
    )
    result = await db.execute(stmt)
    return [
        {
            "date": (
                row.day.isoformat()
                if hasattr(row.day, "isoformat")
                else str(row.day)
            ),
            "task_type": row.task_type,
            "provider": row.provider_used,
            "model": row.model,
            "call_count": row.call_count,
            "success_count": row.success_count,
            "failure_count": row.call_count - row.success_count,
            "fallback_count": row.fallback_count,
            "avg_latency_ms": round(row.avg_latency_ms or 0, 1),
            "input_tokens": None,
            "output_tokens": None,
            "estimated_cost": None,
            "currency": None,
            "usage_source": "unknown",
            "cost_source": "unknown",
        }
        for row in result
    ]


async def query_provider_health_snapshot(db: AsyncSession) -> list[dict]:
    """基于 ai_call_logs 聚合 provider/model recent health snapshot。

    该函数不执行 provider probe，不持久化 health event，也不读取 ai_runs。
    """
    stmt = (
        select(
            AiCallLog.provider_used,
            AiCallLog.model,
            func.count().label("call_count"),
            func.count().filter(AiCallLog.success == True).label("success_count"),  # noqa: E712
            func.count().filter(AiCallLog.fallback_used == True).label("fallback_count"),  # noqa: E712
            func.avg(AiCallLog.latency_ms).label("avg_latency_ms"),
        )
        .group_by(AiCallLog.provider_used, AiCallLog.model)
        .order_by(AiCallLog.provider_used, AiCallLog.model)
    )
    result = await db.execute(stmt)
    items = []
    for row in result:
        call_count = row.call_count
        success_count = row.success_count
        failure_count = call_count - success_count
        fallback_count = row.fallback_count
        failure_rate = round(failure_count / call_count, 3) if call_count else 0.0
        fallback_rate = round(fallback_count / call_count, 3) if call_count else 0.0
        status, reason = _provider_health_status(
            call_count=call_count,
            failure_rate=failure_rate,
            fallback_rate=fallback_rate,
        )
        items.append(
            {
                "provider": row.provider_used,
                "model": row.model,
                "status": status,
                "call_count": call_count,
                "success_count": success_count,
                "failure_count": failure_count,
                "fallback_count": fallback_count,
                "failure_rate": failure_rate,
                "fallback_rate": fallback_rate,
                "avg_latency_ms": round(row.avg_latency_ms or 0, 1),
                "source": "ai_call_logs_recent",
                "reason": reason,
            }
        )
    return items
