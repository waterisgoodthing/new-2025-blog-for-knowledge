import json
import logging
import time
from typing import AsyncGenerator

import httpx
from fastapi import Request

from app.config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPTS = {
    "polish": "你是一个文本润色助手。请优化以下文本的表达，修正语法错误，提升可读性，保持原意不变。直接返回润色后的文本，不要解释。",
    "summarize": "请对以下内容提取核心要点，生成简洁的摘要。用要点列表形式输出。",
    "expand": "请对以下简短内容进行扩写，补充细节、论据和例子，使内容更充实。保持原文风格。",
    "continue": "请根据以下上下文继续写作，保持风格和主题一致。直接续写，不要重复已有内容。",
    "translate_en": "请将以下中文翻译为英文，保持专业术语准确，语言自然流畅。只返回翻译结果。",
    "translate_zh": "请将以下英文翻译为中文，保持专业术语准确，语言自然流畅。只返回翻译结果。",
    "extract_tags": '请从以下内容中提取 3-8 个关键词标签，返回 JSON 数组格式，例如 ["标签1", "标签2"]。不要输出其他内容。',
    "generate_questions": "请根据以下笔记内容，生成 3-5 个复习问题。每个问题一行，以问号结尾。",
}


async def polish_stream(
    text: str,
    action: str,
    context: str | None,
    request: Request,
) -> AsyncGenerator[str, None]:
    settings = get_settings()
    api_key = settings.DEEPSEEK_API_KEY or settings.AI_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    model = settings.DEEPSEEK_MODEL

    if not api_key:
        yield 'data: {"error": "AI 服务未配置"}\n\n'
        yield "data: [DONE]\n\n"
        return

    system_prompt = SYSTEM_PROMPTS.get(action, SYSTEM_PROMPTS["polish"])

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": f"以下是完整笔记上下文:\n{context}"})
    messages.append({"role": "user", "content": text})

    start_time = time.monotonic()
    status = "ok"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 4000,
                    "stream": True,
                },
            ) as response:
                if response.status_code != 200:
                    status = str(response.status_code)
                    yield f'{{"error": "AI 服务错误 ({response.status_code})"}}\n\n'
                    yield "data: [DONE]\n\n"
                    return

                chunk_count = 0
                async for line in response.aiter_lines():
                    if await request.is_disconnected():
                        status = "client_disconnected"
                        break

                    if not line.startswith("data: "):
                        continue

                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            chunk_count += 1
                            yield f'data: {json.dumps({"chunk": content}, ensure_ascii=False)}\n\n'

                            if chunk_count % 3 == 0:
                                if await request.is_disconnected():
                                    status = "client_disconnected"
                                    break
                    except json.JSONDecodeError:
                        continue

    except httpx.TimeoutException:
        status = "timeout"
        yield 'data: {"error": "AI 服务超时，请重试"}\n\n'
    except Exception as e:
        status = "error"
        yield f'data: {{"error": "AI 服务异常"}}\n\n'

    duration_ms = int((time.monotonic() - start_time) * 1000)
    logger.info(
        "ai_polish action=%s text_len=%d context_len=%d duration_ms=%d status=%s",
        action,
        len(text),
        len(context) if context else 0,
        duration_ms,
        status,
    )

    yield "data: [DONE]\n\n"
