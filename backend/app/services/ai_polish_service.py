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
    "title": "根据以下内容生成一个简洁准确的标题。只返回标题文本，不要解释。不超过 30 个字。",
    "outline": "根据以下内容生成 Markdown 目录结构。使用 ## 和 ### 标题层级。只返回目录，不要其他内容。",
    "tags": "从以下内容中推荐 3-5 个关键词标签。返回 JSON 数组格式，例如 [\"标签1\", \"标签2\"]。不要输出其他内容。",
    "diagram": "将以下文本描述的流程或关系转换为 Mermaid graph TD 流程图语法。只返回 Mermaid 代码块，不要其他内容。",
    "compare": "根据以下内容生成一个对比分析。使用 Markdown 表格或左右列表形式，每侧 3-5 个要点。只返回对比内容。",
    "mindmap": "将以下内容整理为 Markmap 思维导图的 Markdown 层级格式。使用 # 作为中心主题，## 作为一级分支，### 作为二级分支，以此类推。只返回 Markdown 层级文本，不要包含 ```markmap 代码块标记。",
    "data_chart": "分析以下数据或文本中的量化信息，生成 ECharts 图表配置。返回 JSON 格式，包含 type (bar/line/pie/radar)、title、xAxis/categories、series。只返回 JSON，不要解释。",
}


async def polish_stream(
    text: str,
    action: str,
    context: str | None,
    request: Request,
    title: str | None = None,
    note_type: str | None = None,
    existing_tags: list[str] | None = None,
    custom_prompt: str | None = None,
) -> AsyncGenerator[str, None]:
    settings = get_settings()
    api_key = settings.DEEPSEEK_API_KEY or settings.AI_API_KEY
    base_url = settings.DEEPSEEK_BASE_URL
    model = settings.DEEPSEEK_MODEL

    if not api_key:
        yield 'data: {"error": "AI 服务未配置"}\n\n'
        yield "data: [DONE]\n\n"
        return

    system_prompt = custom_prompt if action == "custom" and custom_prompt else SYSTEM_PROMPTS.get(action, SYSTEM_PROMPTS["polish"])

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": f"以下是完整笔记上下文:\n{context}"})

    extra_prefix = ""
    if action == "tags" and existing_tags:
        extra_prefix = f"已有标签: {', '.join(existing_tags)}\n"
    if action == "title" and title:
        extra_prefix = f"当前标题（可参考）: {title}\n"
    if note_type:
        extra_prefix += f"笔记类型: {note_type}\n"

    user_content = (extra_prefix + text) if extra_prefix else text
    messages.append({"role": "user", "content": user_content})

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
                    yield f'data: {json.dumps({"error": f"AI 服务错误 ({response.status_code})"}, ensure_ascii=False)}\n\n'
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
