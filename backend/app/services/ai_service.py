import json
import logging
import time
from dataclasses import dataclass, field

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# Stable provider-failure categories. Kept in sync with
# capture_failure_taxonomy.categorize_provider_category so the category can
# travel across layers without re-sniffing provider text.
ALLOWED_ERROR_CATEGORIES = frozenset({
    "provider_auth",
    "provider_timeout",
    "invalid_model",
    "invalid_response",
    "provider_error",
    "no_provider",
})

_AUTH_STATUS_CODES = frozenset({401, 403, 429})


class AIProviderError(RuntimeError):
    """Typed AI provider failure carrying a stable ``category``.

    The message never embeds the raw provider response body; only the
    category and a short status/reason are preserved. This keeps provider
    bodies and credentials out of logs, ``ai_call_logs`` and ``ai_runs``.

    ``attempts`` is an internal, sanitized trail (``ProviderAttempt`` objects
    whose ``error`` is a category only). It is not persisted by the gateway.
    """

    def __init__(self, category: str, message: str, attempts=None):
        super().__init__(message)
        self.category = category
        self.attempts = list(attempts) if attempts else []


def _classify_status(status_code: int) -> str:
    if status_code in _AUTH_STATUS_CODES:
        return "provider_auth"
    if status_code == 404:
        return "invalid_model"
    if 500 <= status_code <= 599:
        return "provider_error"
    return "provider_error"


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


def _select_providers(
    required_caps: set[str],
    preferred: str | None = None,
    fallback_chain: tuple[str, ...] | list[str] | None = None,
) -> list[dict]:
    providers = _get_providers()
    capable = [p for p in providers if required_caps.issubset(p["capabilities"])]
    if not capable:
        capable = [p for p in providers if "text" in p["capabilities"] or "json" in p["capabilities"]]

    if fallback_chain:
        by_name = {p["name"]: p for p in capable}
        ordered = [by_name[name] for name in dict.fromkeys(fallback_chain) if name in by_name]
        if ordered:
            return ordered

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
        try:
            response = await client.post(
                f"{provider['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {provider['key']}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            raise AIProviderError("provider_timeout", "AI provider timeout") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError("provider_error", "AI provider transport error") from exc

    if response.status_code != 200:
        category = _classify_status(response.status_code)
        raise AIProviderError(category, f"AI API error ({response.status_code})")

    try:
        return response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise AIProviderError("invalid_response", "Failed to parse AI response") from exc


def _parse_json_response(data: dict) -> dict:
    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
        raise AIProviderError("invalid_response", "Failed to parse AI response") from e


def _parse_text_response(data: dict) -> str:
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise AIProviderError("invalid_response", "Failed to parse AI response") from e


async def _call_with_fallback(
    required_caps: set[str],
    messages: list[dict],
    max_tokens: int,
    response_format: dict | None = None,
    preferred: str | None = None,
    fallback_chain: tuple[str, ...] | list[str] | None = None,
    parse_json: bool = True,
) -> CallResult:
    providers = _select_providers(required_caps, preferred, fallback_chain)
    if not providers:
        # Kept as ValueError for backward compatibility: the capture adapter
        # maps this to the stable `no_provider` error_code contract.
        raise ValueError("No AI provider configured with required capabilities")

    attempts: list[ProviderAttempt] = []
    last_error: Exception | None = None
    last_index = len(providers) - 1

    for index, provider in enumerate(providers):
        is_last = index == last_index
        start = time.monotonic()
        try:
            data = await _call_provider(provider, messages, max_tokens, response_format)
            parsed = _parse_json_response(data) if parse_json else _parse_text_response(data)
            latency_ms = int((time.monotonic() - start) * 1000)
            attempts.append(ProviderAttempt(
                provider=provider["name"],
                model=provider["model"],
                success=True,
                latency_ms=latency_ms,
            ))
            return CallResult(
                data=parsed,
                attempts=attempts,
                provider_used=provider["name"],
                fallback_used=len(attempts) > 1,
            )
        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            category = getattr(e, "category", None)
            if category not in ALLOWED_ERROR_CATEGORIES:
                category = "provider_error"
            attempts.append(ProviderAttempt(
                provider=provider["name"],
                model=provider["model"],
                success=False,
                latency_ms=latency_ms,
                error=category,
            ))
            last_error = e
            if is_last:
                break
            logger.warning(
                "AI provider %s failed (category=%s), trying next...",
                provider["name"],
                category,
            )
            continue

    last_category = getattr(last_error, "category", None)
    if last_category not in ALLOWED_ERROR_CATEGORIES:
        last_category = "provider_error"
    raise AIProviderError(
        category=last_category,
        message="All AI providers failed",
        attempts=attempts,
    )


async def call_ocr_model(messages: list[dict], max_tokens: int = 4000) -> dict:
    """Internal — use ai_gateway.call_vision."""
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
    """Internal — use ai_gateway.call_text."""
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
    """Internal — use ai_gateway.call_text with json_mode=False."""
    result = await _call_with_fallback(
        required_caps={"text"},
        messages=messages,
        max_tokens=max_tokens,
        preferred="deepseek",
        parse_json=False,
    )
    return result.data


async def call_general_model(messages: list[dict], max_tokens: int = 8000, json_mode: bool = True) -> dict | str:
    """Internal — use ai_gateway.call_general."""
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
        "name": "Qwen3.7 Plus Vision",
        "model": settings.DASHSCOPE_MODEL,
        "base_url": settings.DASHSCOPE_BASE_URL,
        "base_url_label": "DashScope",
        "role": "OCR/vision primary, general model",
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
