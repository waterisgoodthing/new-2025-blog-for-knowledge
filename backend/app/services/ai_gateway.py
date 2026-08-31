"""AI Gateway 最小内核 — 统一调用入口 + 调用日志。

所有 AI 模型调用必须经此模块。Gateway 委托 ai_service 执行 provider
调用与 fallback，并持久化调用记录到 ai_call_logs。

权限校验在路由层，Gateway 不做权限校验。
"""

import logging
import time
import uuid
from dataclasses import dataclass

from app.database import async_session
from app.models.ai_call_log import AiCallLog
from app.models.ai_run import AiRun
from app.services.ai_prompt_registry import get_prompt_template
from app.services.ai_routing_policy import resolve_routing_policy
from app.services.ai_run_service import complete_ai_run, fail_ai_run, start_ai_run
from app.services.ai_service import _call_with_fallback
from app.services.ai_task_types import AiTaskType
from app.services.ai_validator import SCHEMA_MAP, validate_ai_output

logger = logging.getLogger(__name__)

_HUMAN_REVIEW_TASKS = {
    AiTaskType.CAPTURE_DRAFT,
    AiTaskType.MISTAKE_QUESTION_DRAFT,
    AiTaskType.MISTAKE_ERROR_INTERPRETATION,
    AiTaskType.MISTAKE_FINAL_ANALYSIS,
    AiTaskType.DIAGRAM_STRUCTURED,
}


@dataclass
class GatewayCallResult:
    """Gateway 调用结果（含元数据供日志写入）。"""

    data: dict | str | None
    provider_used: str
    model: str
    latency_ms: int
    success: bool
    fallback_used: bool
    attempts: list[dict]  # [{provider, model, success, latency_ms, error}]
    error: str | None = None


def _serialize_attempts(attempts: list) -> list[dict]:
    """将 ProviderAttempt 列表序列化为 JSON 安全的 dict 列表。"""
    return [
        {
            "provider": a.provider,
            "model": a.model,
            "success": a.success,
            "latency_ms": a.latency_ms,
            "error": (a.error or "")[:200],
        }
        for a in attempts
    ]


def _find_model_from_attempts(attempts: list, provider_used: str) -> str:
    """从成功的 attempt 中提取 model。"""
    for a in attempts:
        if a.provider == provider_used and a.success:
            return a.model
    for a in reversed(attempts):
        if a.success:
            return a.model
    return ""


async def _write_call_log(
    task_type: str,
    result: GatewayCallResult,
    input_summary: str | None,
    prompt_version: str | None = None,
) -> None:
    """持久化调用日志到 ai_call_logs。

    使用独立 AsyncSession，写入失败仅 log warning，不阻塞主调用。
    """
    try:
        async with async_session() as session:
            log = AiCallLog(
                task_type=task_type,
                provider_used=result.provider_used,
                model=result.model,
                latency_ms=result.latency_ms,
                success=result.success,
                error=(result.error[:500] if result.error else None),
                fallback_used=result.fallback_used,
                attempts=result.attempts,
                input_summary=(input_summary[:200] if input_summary else None),
                prompt_version=prompt_version,
            )
            session.add(log)
            await session.commit()
    except Exception as e:
        logger.warning("AI call log write failed: %s", e)


async def _start_run_record(
    task_type: str,
    input_summary: str | None,
    prompt_version: str | None,
) -> uuid.UUID | None:
    """Create a business Run for registered tasks; failures remain observable gaps."""

    try:
        typed_task = AiTaskType(task_type)
    except ValueError:
        return None
    try:
        async with async_session() as session:
            run = await start_ai_run(
                session,
                task_type=task_type,
                prompt_version=prompt_version,
                input_summary=input_summary,
                review_required=typed_task in _HUMAN_REVIEW_TASKS,
            )
            await session.commit()
            return run.id
    except Exception as exc:
        logger.warning("AI Run start failed for %s: %s", task_type, exc)
        return None


async def _finish_run_record(
    run_id: uuid.UUID | None,
    task_type: str,
    result: GatewayCallResult,
) -> None:
    if run_id is None:
        return
    try:
        async with async_session() as session:
            run = await session.get(AiRun, run_id)
            if run is None:
                logger.warning("AI Run missing during finalize: %s", run_id)
                return
            if not result.success:
                await fail_ai_run(
                    session,
                    run,
                    error_code="provider_error",
                    error_message_safe=result.error or "AI provider call failed",
                    provider_used=result.provider_used,
                    model=result.model,
                    latency_ms=result.latency_ms,
                )
            else:
                typed_task = AiTaskType(task_type)
                if SCHEMA_MAP.get(typed_task) is None:
                    validation_status = "not_applicable"
                else:
                    validation = validate_ai_output(typed_task, result.data)
                    validation_status = "passed" if validation.success else "failed"
                    if not validation.success:
                        run.review_status = "not_required"
                await complete_ai_run(
                    session,
                    run,
                    provider_used=result.provider_used,
                    model=result.model,
                    output_data=result.data,
                    validation_status=validation_status,
                    latency_ms=result.latency_ms,
                )
            await session.commit()
    except Exception as exc:
        logger.warning("AI Run finalize failed for %s: %s", run_id, exc)


def _build_success_result(result, latency_ms: int) -> GatewayCallResult:
    """从 ai_service.CallResult 构建成功的 GatewayCallResult。"""
    return GatewayCallResult(
        data=result.data,
        provider_used=result.provider_used,
        model=_find_model_from_attempts(result.attempts, result.provider_used),
        latency_ms=latency_ms,
        success=True,
        fallback_used=result.fallback_used,
        attempts=_serialize_attempts(result.attempts),
        error=None,
    )


def _build_failure_result(exc: Exception, latency_ms: int) -> GatewayCallResult:
    """从异常构建失败的 GatewayCallResult。"""
    return GatewayCallResult(
        data=None,
        provider_used="",
        model="",
        latency_ms=latency_ms,
        success=False,
        fallback_used=False,
        attempts=[],
        error=str(exc)[:500],
    )


def _resolve_registry_defaults(
    task_type: str | AiTaskType,
    max_tokens: int | None,
    preferred: str | None,
    json_mode: bool | None,
    fallback_preferred: str,
) -> tuple[int, str | None, bool, str | None, tuple[str, ...] | None]:
    """从 registry 读取默认值，显式传参优先。

    Returns: (max_tokens, preferred, json_mode, prompt_version, fallback_chain)
    """
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type
    prompt_version: str | None = None
    explicit_preferred = preferred is not None

    try:
        tt = AiTaskType(task_type_str) if isinstance(task_type, str) else task_type
        template = get_prompt_template(tt)
        if max_tokens is None:
            max_tokens = template.max_tokens
        if preferred is None:
            preferred = template.preferred_provider
        if json_mode is None:
            json_mode = template.json_mode
        prompt_version = template.version
    except (ValueError, KeyError):
        pass  # 未知 task_type，使用 fallback

    if max_tokens is None:
        max_tokens = 8000
    if json_mode is None:
        json_mode = True

    fallback_chain: tuple[str, ...] | None = None
    if explicit_preferred:
        fallback_chain = (preferred,) if preferred else None
    else:
        policy = resolve_routing_policy(task_type_str)
        preferred = policy.primary_provider or preferred or fallback_preferred
        fallback_chain = policy.fallback_chain

    if preferred is None:
        preferred = fallback_preferred

    return max_tokens, preferred, json_mode, prompt_version, fallback_chain


async def call_text(
    task_type: str | AiTaskType,
    messages: list[dict],
    *,
    max_tokens: int | None = None,
    preferred: str | None = None,
    json_mode: bool | None = None,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """文本模型调用（DeepSeek 主路径）。参数为 None 时从 registry 读取默认值。"""
    max_tokens, preferred, json_mode, prompt_version, fallback_chain = _resolve_registry_defaults(
        task_type, max_tokens, preferred, json_mode, fallback_preferred="deepseek"
    )
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type
    run_id = await _start_run_record(task_type_str, input_summary, prompt_version)

    start = time.monotonic()
    try:
        required_caps = {"text", "json"} if json_mode else {"text"}
        response_format = {"type": "json_object"} if json_mode else None
        result = await _call_with_fallback(
            required_caps=required_caps,
            messages=messages,
            max_tokens=max_tokens,
            response_format=response_format,
            preferred=preferred,
            fallback_chain=fallback_chain,
            parse_json=json_mode,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_success_result(result, latency_ms)
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_failure_result(e, latency_ms)

    await _write_call_log(task_type_str, gw_result, input_summary, prompt_version=prompt_version)
    await _finish_run_record(run_id, task_type_str, gw_result)
    return gw_result


async def call_vision(
    task_type: str | AiTaskType,
    messages: list[dict],
    *,
    max_tokens: int | None = None,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """视觉/OCR 模型调用（DashScope Vision 主路径）。参数为 None 时从 registry 读取默认值。"""
    max_tokens, preferred, _, prompt_version, fallback_chain = _resolve_registry_defaults(
        task_type, max_tokens, None, None, fallback_preferred="dashscope_vision"
    )
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type
    run_id = await _start_run_record(task_type_str, input_summary, prompt_version)

    start = time.monotonic()
    try:
        result = await _call_with_fallback(
            required_caps={"vision", "json"},
            messages=messages,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            preferred=preferred,
            fallback_chain=fallback_chain,
            parse_json=True,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_success_result(result, latency_ms)
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_failure_result(e, latency_ms)

    await _write_call_log(task_type_str, gw_result, input_summary, prompt_version=prompt_version)
    await _finish_run_record(run_id, task_type_str, gw_result)
    return gw_result


async def call_general(
    task_type: str | AiTaskType,
    messages: list[dict],
    *,
    max_tokens: int | None = None,
    json_mode: bool | None = None,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """通用模型调用（Qwen General fallback）。参数为 None 时从 registry 读取默认值。"""
    max_tokens, preferred, json_mode, prompt_version, fallback_chain = _resolve_registry_defaults(
        task_type, max_tokens, None, json_mode, fallback_preferred="qwen_general"
    )
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type
    run_id = await _start_run_record(task_type_str, input_summary, prompt_version)

    start = time.monotonic()
    try:
        response_format = {"type": "json_object"} if json_mode else None
        result = await _call_with_fallback(
            required_caps={"text"},
            messages=messages,
            max_tokens=max_tokens,
            response_format=response_format,
            preferred=preferred,
            fallback_chain=fallback_chain,
            parse_json=json_mode,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_success_result(result, latency_ms)
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_failure_result(e, latency_ms)

    await _write_call_log(task_type_str, gw_result, input_summary, prompt_version=prompt_version)
    await _finish_run_record(run_id, task_type_str, gw_result)
    return gw_result


async def call_stream(
    task_type: str | AiTaskType,
    messages: list[dict],
    *,
    max_tokens: int | None = None,
    preferred: str | None = None,
    json_mode: bool | None = None,
    input_summary: str | None = None,
) -> GatewayCallResult:
    """流式调用入口。参数为 None 时从 registry 读取默认值。

    当前底层 ai_service 不支持真正的逐 token 流式，此方法为非流式
    调用的包装，日志在调用结束后写入。未来底层支持流式时可改为
    async generator 逐 chunk yield。
    """
    max_tokens, preferred, json_mode, prompt_version, fallback_chain = _resolve_registry_defaults(
        task_type, max_tokens, preferred, json_mode, fallback_preferred="deepseek"
    )
    task_type_str = task_type.value if isinstance(task_type, AiTaskType) else task_type
    run_id = await _start_run_record(task_type_str, input_summary, prompt_version)

    start = time.monotonic()
    try:
        required_caps = {"text", "json"} if json_mode else {"text"}
        response_format = {"type": "json_object"} if json_mode else None
        result = await _call_with_fallback(
            required_caps=required_caps,
            messages=messages,
            max_tokens=max_tokens,
            response_format=response_format,
            preferred=preferred,
            fallback_chain=fallback_chain,
            parse_json=json_mode,
        )
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_success_result(result, latency_ms)
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        gw_result = _build_failure_result(e, latency_ms)

    await _write_call_log(task_type_str, gw_result, input_summary, prompt_version=prompt_version)
    await _finish_run_record(run_id, task_type_str, gw_result)
    return gw_result
