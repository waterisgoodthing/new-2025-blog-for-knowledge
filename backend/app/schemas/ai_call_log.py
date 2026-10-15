import uuid
from datetime import date
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AiCallLogOut(BaseModel):
    """调用日志响应。不包含 input_summary（安全考虑）。"""

    id: uuid.UUID
    task_type: str
    provider_used: str
    model: str
    latency_ms: int
    success: bool
    error: str | None = None
    fallback_used: bool
    attempts: list | None = None
    prompt_version: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AiCallLogStatsItem(BaseModel):
    """按 task_type 聚合的统计项。"""

    task_type: str
    total: int
    success_count: int
    avg_latency_ms: float


class AiCallLogStatsResponse(BaseModel):
    """调用日志统计响应。"""

    items: list[AiCallLogStatsItem]


class AiUsageCostStatsItem(BaseModel):
    """Usage / cost observability 聚合项。

    当前 ai_call_logs 尚未持久化 provider token usage，因此 token/cost 字段
    必须为 nullable，并通过 source 字段明确 unknown，避免伪造成本。
    """

    date: date
    task_type: str
    provider: str
    model: str
    call_count: int
    success_count: int
    failure_count: int
    fallback_count: int
    avg_latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost: Decimal | None = None
    currency: str | None = None
    usage_source: str = "unknown"
    cost_source: str = "unknown"


class AiUsageCostStatsResponse(BaseModel):
    """Usage / cost observability 响应。"""

    items: list[AiUsageCostStatsItem]


class AiProviderHealthSnapshotItem(BaseModel):
    """基于 ai_call_logs 的 provider/model health snapshot。

    这是 recent observability snapshot，不是真实 provider probe 结果。
    """

    provider: str
    model: str
    status: str
    call_count: int
    success_count: int
    failure_count: int
    fallback_count: int
    failure_rate: float
    fallback_rate: float
    avg_latency_ms: float
    source: str = "ai_call_logs_recent"
    reason: str


class AiProviderHealthSnapshotResponse(BaseModel):
    """Provider health snapshot 响应。"""

    items: list[AiProviderHealthSnapshotItem]
