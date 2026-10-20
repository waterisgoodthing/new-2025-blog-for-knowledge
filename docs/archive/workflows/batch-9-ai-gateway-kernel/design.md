# Design：Batch 9 AI Gateway 最小内核

> 关联：[README.md](./README.md) | [requirements.md](./requirements.md) | [tasks.md](./tasks.md)

## 一、架构总览

```text
┌─────────────────────────────────────────────────────┐
│ 路由层                                                │
│  ai.py (瘦身 <600行)    ai_polish.py                 │
│  GET /api/ai/call-logs  GET /api/ai/call-logs/stats  │
└──────────┬──────────────────┬───────────────────────┘
           │                  │
           ▼                  ▼
┌─────────────────────────────────────────────────────┐
│ Service 层（从 ai.py 抽离）                           │
│  ai_analyze_service.py   ai_repair_service.py        │
│  (parse_result, context, find_related)               │
│  (LaTeX repair, deterministic repair)                │
└──────────┬──────────────────┬───────────────────────┘
           │                  │
           ▼                  ▼
┌─────────────────────────────────────────────────────┐
│ Gateway 层（新建）                                     │
│  ai_gateway.py                                       │
│  call_text()  call_vision()  call_general()          │
│  call_stream()                                       │
│  + task_type 标识 + 调用日志写入                      │
└──────┬──────────────────┬───────────────────────────┘
       │                  │
       ▼                  ▼
┌──────────────────┐  ┌────────────────────┐
│ ai_service.py    │  │ ai_call_logs (DB)  │
│ (底层, 保留)      │  │ 独立 session 写入   │
│ _call_with_      │  └────────────────────┘
│   fallback()     │
│ provider 选择     │
└──────────────────┘
```

## 二、文件结构

### 新建文件

| 文件 | 职责 |
| --- | --- |
| `backend/app/services/ai_gateway.py` | Gateway 层：统一调用入口 + 调用日志 |
| `backend/app/models/ai_call_log.py` | `AiCallLog` SQLAlchemy 模型 |
| `backend/app/schemas/ai_call_log.py` | 调用日志 Pydantic schema |
| `backend/app/services/ai_analyze_service.py` | analyze 业务逻辑（从 ai.py 抽离） |
| `backend/app/services/ai_repair_service.py` | LaTeX/deterministic repair（从 ai.py 抽离） |
| `backend/alembic/versions/016_add_ai_call_logs.py` | 新建 ai_call_logs 表 |
| `backend/tests/test_ai_gateway.py` | Gateway 单元测试 |

### 修改文件

| 文件 | 改动 |
| --- | --- |
| `backend/app/routers/ai.py` | 瘦身：业务逻辑抽离到 service，调用改 Gateway |
| `backend/app/routers/ai_polish.py` | 调用改 Gateway |
| `backend/app/services/ai_service.py` | 标注为底层 internal，函数加 docstring 说明 |
| `backend/app/services/capture_ai_draft.py` | `call_text_model` → `ai_gateway.call_text` |
| `backend/app/services/diagram_service.py` | 直调 → Gateway |
| `backend/app/models/__init__.py` | 导入 AiCallLog |
| `src/app/manage/(workspace)/ai/page.tsx` | 占位页 → 调用日志展示 |
| `src/lib/api/ai.ts` | 新增 call-logs 查询 API client |

## 三、ai_gateway.py 接口设计

```python
"""AI Gateway 最小内核 — 统一调用入口 + 调用日志。

所有 AI 模型调用必须经此模块。Gateway 委托 ai_service 执行 provider
调用与 fallback，并持久化调用记录到 ai_call_logs。
"""

from dataclasses import dataclass


@dataclass
class GatewayCallResult:
    """Gateway 调用结果（含元数据供日志写入）。"""
    data: dict | str
    provider_used: str
    model: str
    latency_ms: int
    success: bool
    fallback_used: bool
    attempts: list[dict]      # [{provider, model, success, latency_ms, error}]
    error: str | None


async def call_text(
    task_type: str,
    messages: list[dict],
    max_tokens: int = 8000,
    *,
    preferred: str | None = "deepseek",
    json_mode: bool = True,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """文本模型调用（DeepSeek 主路径）。"""
    ...


async def call_vision(
    task_type: str,
    messages: list[dict],
    max_tokens: int = 4000,
    *,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """视觉/OCR 模型调用（DashScope Vision 主路径）。"""
    ...


async def call_general(
    task_type: str,
    messages: list[dict],
    max_tokens: int = 8000,
    *,
    json_mode: bool = True,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """通用模型调用（Qwen General fallback）。"""
    ...


async def call_stream(
    task_type: str,
    messages: list[dict],
    max_tokens: int = 8000,
    *,
    preferred: str | None = None,
    input_summary: str | None = None,
):
    """流式调用，yield text chunks。调用日志在流结束后写入。"""
    ...
```

### Gateway 内部流程

```python
async def call_text(task_type, messages, ...):
    start = time.monotonic()
    try:
        # 委托 ai_service 底层调用
        result = await ai_service._call_with_fallback(
            required_caps={"text", "json"} if json_mode else {"text"},
            messages=messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if json_mode else None,
            preferred=preferred,
            parse_json=json_mode,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = GatewayCallResult(
            data=result.data,
            provider_used=result.provider_used,
            model=...,  # 从 attempts 取
            latency_ms=latency_ms,
            success=True,
            fallback_used=result.fallback_used,
            attempts=[...],
            error=None,
        )
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = GatewayCallResult(
            data=None, provider_used="", model="",
            latency_ms=latency_ms, success=False,
            fallback_used=False, attempts=[],
            error=str(e)[:500],
        )

    # 持久化日志（独立 session，不阻塞主调用）
    await _write_call_log(task_type, gw_result, input_summary)
    return gw_result
```

### 日志写入（独立 session）

```python
async def _write_call_log(
    task_type: str,
    result: GatewayCallResult,
    input_summary: str | None,
):
    try:
        async with AsyncSessionLocal() as session:
            log = AiCallLog(
                task_type=task_type,
                provider_used=result.provider_used,
                model=result.model,
                latency_ms=result.latency_ms,
                success=result.success,
                error=result.error,
                fallback_used=result.fallback_used,
                attempts=[...],
                input_summary=(input_summary or "")[:200],
            )
            session.add(log)
            await session.commit()
    except Exception as e:
        logger.warning("AI call log write failed: %s", e)
```

## 四、AiCallLog 模型

```python
# backend/app/models/ai_call_log.py
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AiCallLog(Base):
    __tablename__ = "ai_call_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_used: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    fallback_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    attempts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_ai_call_logs_created_at", "created_at"),
        Index("idx_ai_call_logs_task_type", "task_type"),
        Index("idx_ai_call_logs_success", "success"),
    )
```

## 五、ai.py 瘦身方案

### 抽离到 `ai_repair_service.py`

| 函数 | 原位置 | 目标 |
| --- | --- | --- |
| `_repair_latex_in_text(text)` | ai.py L510 | ai_repair_service.py |
| `_repair_latex_in_result(result)` | ai.py L569 | ai_repair_service.py |
| `_check_deterministic_fields(result)` | ai.py L450 | ai_repair_service.py |
| `_repair_deterministic_result(...)` | ai.py L462 | ai_repair_service.py |
| `_list_of_strings(value)` | ai.py L435 | ai_repair_service.py |

### 抽离到 `ai_analyze_service.py`

| 函数 | 原位置 | 目标 |
| --- | --- | --- |
| `_parse_result(...)` | ai.py L598 | ai_analyze_service.py |
| `_build_personal_context(...)` | ai.py L415 | ai_analyze_service.py |
| `_find_related_notes(db, ...)` | ai.py L651 | ai_analyze_service.py |
| `_check_rate_limit(key)` | ai.py L106 | ai_analyze_service.py |

### ai.py 瘦身后保留

- 路由定义（`@router.post/get`）
- 请求/响应 schema 导入
- 参数校验
- 调用 service 层 / Gateway
- 返回响应
- 流式 SSE 封装

### 调用迁移

```python
# 瘦身前
from app.services.ai_service import call_ocr_model, call_text_model
raw = await call_text_model(messages)

# 瘦身后
from app.services.ai_gateway import call_text
result = await call_text("analyze_mistake", messages, input_summary=...)
raw = result.data
```

## 六、调用日志查询端点

```python
# ai.py 新增
@router.get("/call-logs")
async def list_call_logs(
    page: int = 1, size: int = 20,
    task_type: str | None = None,
    success: bool | None = None,
    provider: str | None = None,
    _admin=Depends(get_current_admin),
    db=Depends(get_db),
):
    ...

@router.get("/call-logs/stats")
async def get_call_log_stats(
    _admin=Depends(get_current_admin),
    db=Depends(get_db),
):
    # 按 task_type 聚合：总数、成功率、平均延迟
    ...
```

## 七、前端 /manage/ai 页面

- 从占位页改为调用日志列表 + 统计卡片。
- 展示：task_type、provider、model、latency、success/fail、时间。
- 支持按 task_type / success 过滤。
- 不展示 input_summary（可能含用户数据摘要，仅 admin 可见但不在列表展示）。
- 复用既有 `ai-tab.tsx` 的 Provider Status 卡片。

## 八、流式调用处理

- `call_stream` 在流结束后写入日志（记录总 latency、success、provider）。
- 流式过程中不写中间日志。
- 流式失败也记录日志。
- 现有 `analyze_mistake_stream` / `analyze_text_stream` 迁移到 `ai_gateway.call_stream`。

## 九、与 Batch 8 的关系

- `capture_ai_draft.py` 迁移到 Gateway，但 Batch 8 的窄调用边界不变（AI 输出仍只进 capture 草稿）。
- Gateway 不改变 AI 输出的安全边界（不直接写 mistakes）。
- Gateway 的 task_type 复用 Batch 8 的调用场景标识。
