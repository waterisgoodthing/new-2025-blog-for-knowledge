import json
import logging
import time
from dataclasses import dataclass, field

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ProviderAttempt:
    provider: str
    model: str
    success: bool
    latency_ms: int = 0
    error: str = ""
    fallback_used: bool = False


@dataclass
class CallResult:
    data: dict | str
    attempts: list[ProviderAttempt] = field(default_factory=list)
    provider_used: str = ""
    fallback_used: bool = False


def _get_providers() -> list[dict]:
    settings = get_settings()

    providers = []

    if settings.DEEPSEEK_API_KEY:
        providers.append({
            "name": "deepseek",
            "key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "model": settings.DEEPSEEK_MODEL,
            "capabilities": {"text", "json"},
        })

    if settings.DASHSCOPE_API_KEY:
        providers.append({
            "name": "dashscope_vision",
            "key": settings.DASHSCOPE_API_KEY,
            "base_url": settings.DASHSCOPE_BASE_URL,
            "model": settings.DASHSCOPE_MODEL,
            "capabilities": {"vision", "json"},
        })

    if settings.DASHSCOPE_API_KEY:
        general_model = settings.AI_MODEL
        is_dashscope = "dashscope" in settings.DASHSCOPE_BASE_URL
        if is_dashscope and not general_model.startswith("qwen"):
            general_model = "qwen3.7-plus"
        providers.append({
            "name": "qwen_general",
            "key": settings.DASHSCOPE_API_KEY,
            "base_url": settings.DASHSCOPE_BASE_URL,
            "model": general_model,
            "capabilities": {"text", "vision", "json"},
        })
    elif settings.AI_API_KEY:
        providers.append({
            "name": "qwen_general",
            "key": settings.AI_API_KEY,
            "base_url": settings.AI_BASE_URL,
            "model": settings.AI_MODEL,
            "capabilities": {"text", "vision", "json"},
        })

    return providers


def _select_providers(required_caps: set[str], preferred: str | None = None) -> list[dict]:
    providers = _get_providers()
    capable = [p for p in providers if required_caps.issubset(p["capabilities"])]
    if not capable:
        capable = [p for p in providers if "text" in p["capabilities"] or "json" in p["capabilities"]]

    if preferred:
        def sort_key(p):
            return (0 if p["name"] == preferred else 1)
        capable.sort(key=sort_key)

    return capable


_FALLBACK_TRIGGERS = {429, 500, 502, 503, 504}


async def _call_provider(
    provider: dict,
    messages: list[dict],
    max_tokens: int,
    response_format: dict | None = None,
) -> dict:
    body: dict = {
        "model": provider["model"],
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if response_format:
        body["response_format"] = response_format

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{provider['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {provider['key']}",
                "Content-Type": "application/json",
            },
            json=body,
        )

    if response.status_code != 200:
        raise RuntimeError(f"AI API error ({response.status_code}): {response.text}")

    return response.json()


def _parse_json_response(data: dict) -> dict:
    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse AI response: {e}")


def _parse_text_response(data: dict) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Failed to parse AI response: {e}")


async def _call_with_fallback(
    required_caps: set[str],
    messages: list[dict],
    max_tokens: int,
    response_format: dict | None = None,
    preferred: str | None = None,
    parse_json: bool = True,
) -> CallResult:
    providers = _select_providers(required_caps, preferred)
    if not providers:
        raise ValueError("No AI provider configured with required capabilities")

    attempts: list[ProviderAttempt] = []
    last_error: Exception | None = None

    for provider in providers:
        start = time.monotonic()
        try:
            data = await _call_provider(provider, messages, max_tokens, response_format)
            latency_ms = int((time.monotonic() - start) * 1000)
            attempts.append(ProviderAttempt(
                provider=provider["name"],
                model=provider["model"],
                success=True,
                latency_ms=latency_ms,
            ))
            parsed = _parse_json_response(data) if parse_json else _parse_text_response(data)
            return CallResult(
                data=parsed,
                attempts=attempts,
                provider_used=provider["name"],
                fallback_used=len(attempts) > 1,
            )
        except RuntimeError as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            err_str = str(e)
            is_retryable = any(code in err_str for code in ["429", "500", "502", "503", "504", "timeout", "ConnectError"])
            attempts.append(ProviderAttempt(
                provider=provider["name"],
                model=provider["model"],
                success=False,
                latency_ms=latency_ms,
                error=err_str[:200],
            ))
            last_error = e
            if not is_retryable and provider == providers[-1]:
                break
            logger.warning("AI provider %s failed (%s), trying next...", provider["name"], err_str[:100])
            continue
        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            attempts.append(ProviderAttempt(
                provider=provider["name"],
                model=provider["model"],
                success=False,
                latency_ms=latency_ms,
                error=str(e)[:200],
            ))
            last_error = e
            continue

    error_trail = "; ".join(f"{a.provider}: {a.error}" for a in attempts if not a.success)
    raise RuntimeError(f"All AI providers failed. Trail: {error_trail}")


async def call_ocr_model(messages: list[dict], max_tokens: int = 4000) -> dict:
    result = await _call_with_fallback(
        required_caps={"vision", "json"},
        messages=messages,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        preferred="dashscope_vision",
        parse_json=True,
    )
    for a in result.attempts:
        logger.info("OCR call: provider=%s model=%s success=%s latency=%dms fallback=%s",
                     a.provider, a.model, a.success, a.latency_ms, a.fallback_used)
    return result.data


async def call_text_model(messages: list[dict], max_tokens: int = 8000) -> dict:
    result = await _call_with_fallback(
        required_caps={"text", "json"},
        messages=messages,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        preferred="deepseek",
        parse_json=True,
    )
    for a in result.attempts:
        logger.info("Text call: provider=%s model=%s success=%s latency=%dms fallback=%s",
                     a.provider, a.model, a.success, a.latency_ms, a.fallback_used)
    return result.data


async def call_text_model_no_json(messages: list[dict], max_tokens: int = 8000) -> str:
    result = await _call_with_fallback(
        required_caps={"text"},
        messages=messages,
        max_tokens=max_tokens,
        preferred="deepseek",
        parse_json=False,
    )
    return result.data


async def call_general_model(messages: list[dict], max_tokens: int = 8000, json_mode: bool = True) -> dict | str:
    settings = get_settings()
    general_key = settings.DASHSCOPE_API_KEY or settings.AI_API_KEY
    if not general_key:
        raise ValueError("No general AI key configured (DASHSCOPE_API_KEY or AI_API_KEY)")

    response_format = {"type": "json_object"} if json_mode else None
    result = await _call_with_fallback(
        required_caps={"text"},
        messages=messages,
        max_tokens=max_tokens,
        response_format=response_format,
        preferred="qwen_general",
        parse_json=json_mode,
    )
    return result.data


async def get_provider_status() -> list[dict]:
    settings = get_settings()
    providers = []

    if settings.DASHSCOPE_API_KEY:
        general_model = settings.AI_MODEL
        if "dashscope" in settings.DASHSCOPE_BASE_URL and not general_model.startswith("qwen"):
            general_model = "qwen3.7-plus"
        providers.append({
            "name": "Qwen3.7 Plus",
            "model": general_model,
            "base_url": settings.DASHSCOPE_BASE_URL,
            "base_url_label": "DashScope",
            "role": "general, fallback",
            "configured": True,
        })
    elif settings.AI_API_KEY:
        providers.append({
            "name": "Qwen3.7 Plus",
            "model": settings.AI_MODEL,
            "base_url": settings.AI_BASE_URL,
            "base_url_label": "Custom",
            "role": "general, fallback",
            "configured": True,
        })
    else:
        providers.append({
            "name": "Qwen3.7 Plus",
            "model": "qwen3.7-plus",
            "base_url": "",
            "base_url_label": "DashScope",
            "role": "general, fallback",
            "configured": False,
        })

    providers.append({
        "name": "DashScope Vision",
        "model": settings.DASHSCOPE_MODEL,
        "base_url": settings.DASHSCOPE_BASE_URL,
        "base_url_label": "DashScope",
        "role": "OCR/vision primary",
        "configured": bool(settings.DASHSCOPE_API_KEY),
    })
    providers.append({
        "name": "DeepSeek",
        "model": settings.DEEPSEEK_MODEL,
        "base_url": settings.DEEPSEEK_BASE_URL,
        "base_url_label": "DeepSeek",
        "role": "text primary",
        "configured": bool(settings.DEEPSEEK_API_KEY),
    })

    return providers
