import json

import httpx

from app.config import get_settings


async def call_ocr_model(messages: list[dict], max_tokens: int = 4000) -> dict:
    settings = get_settings()
    api_key = settings.DASHSCOPE_API_KEY or settings.AI_API_KEY
    base_url = settings.DASHSCOPE_BASE_URL
    model = settings.DASHSCOPE_MODEL

    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not configured")

    return await _call_openai_compatible(api_key, base_url, model, messages, max_tokens)


async def call_text_model(messages: list[dict], max_tokens: int = 8000) -> dict:
    settings = get_settings()
    api_key = settings.DEEPSEEK_API_KEY or settings.AI_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    model = settings.DEEPSEEK_MODEL

    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not configured")

    return await _call_openai_compatible(api_key, base_url, model, messages, max_tokens)


async def call_text_model_no_json(messages: list[dict], max_tokens: int = 8000) -> str:
    settings = get_settings()
    api_key = settings.DEEPSEEK_API_KEY or settings.AI_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    model = settings.DEEPSEEK_MODEL

    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not configured")

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
            },
        )

    if response.status_code != 200:
        raise RuntimeError(f"AI API error ({response.status_code}): {response.text}")

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Failed to parse AI response: {e}")


async def _call_openai_compatible(
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict],
    max_tokens: int,
) -> dict:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            },
        )

    if response.status_code != 200:
        raise RuntimeError(f"AI API error ({response.status_code}): {response.text}")

    data = response.json()

    try:
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse AI response: {e}")
