"""AI 分析服务 — prompt 常量 + 业务逻辑。

从 ai.py 抽离的 prompt 常量和分析函数，不含路由/HTTP 层代码。
"""

import time
from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.schemas.ai import AnalyzeResponse, DiagramItem
from app.services.ai_prompt_registry import PROMPT_REGISTRY, get_prompt_template
from app.services.ai_task_types import AiTaskType
from app.services.ai_repair_service import (
    _check_deterministic_fields,
    _list_of_strings,
    _repair_deterministic_result,
    _repair_latex_in_result,
)


# --- Rate limit ---

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60


def check_rate_limit(key: str = "global") -> None:
    now = time.time()
    timestamps = _rate_limit_store[key]
    _rate_limit_store[key] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s.")
    _rate_limit_store[key].append(now)


# --- Prompt constants (migrated to ai_prompts.py — Batch 10 P0-04) ---


PROMPT_TEMPLATES = {
    "mistake": {
        "ocr": {
            "name": "错题 OCR 识别",
            "description": "从图片中提取题目信息，必要时解题",
            "prompt": (get_prompt_template(AiTaskType.ANALYZE_MISTAKE).user_content_template or "")[:500] + "...",
            "route": "OCR/vision",
            "full_prompt": get_prompt_template(AiTaskType.ANALYZE_MISTAKE).user_content_template or "",
        },
        "text_analysis": {
            "name": "错题文本分析",
            "description": "分析文本题目，给出答案和解析",
            "prompt": get_prompt_template(AiTaskType.ANALYZE_TEXT).system_prompt[:500] + "...",
            "route": "text JSON",
            "full_prompt": get_prompt_template(AiTaskType.ANALYZE_TEXT).system_prompt,
        },
        "variant": {
            "name": "变式题生成",
            "description": "根据知识点生成变式练习题",
            "prompt": get_prompt_template(AiTaskType.GENERATE_VARIANT).system_prompt,
            "route": "text JSON",
        },
        "knowledge_card": {
            "name": "知识卡片生成",
            "description": "生成结构化知识卡片",
            "prompt": get_prompt_template(AiTaskType.GENERATE_KNOWLEDGE_CARD).system_prompt,
            "route": "text JSON",
        },
        "question_draft": {
            "name": "题目识别(分阶段)",
            "description": "从图片/文本中提取题目信息，不推断错因",
            "prompt": "只提取题目信息，不推断学生错误原因...",
            "route": "OCR/vision or text JSON",
            "full_prompt": "见 mistake_staged_service.py QUESTION_DRAFT_SYSTEM_PROMPT",
        },
        "error_interpretation": {
            "name": "错因理解(分阶段)",
            "description": "理解学生自述的错因，给出结构化解读",
            "prompt": "以学生自述错因为唯一真相来源...",
            "route": "text JSON",
            "full_prompt": "见 mistake_staged_service.py ERROR_INTERPRETATION_SYSTEM_PROMPT",
        },
        "final_analysis": {
            "name": "最终解析(分阶段)",
            "description": "基于已采纳的错因理解生成最终分析",
            "prompt": "围绕已采纳的错因理解展开分析...",
            "route": "text JSON",
            "full_prompt": "见 mistake_staged_service.py FINAL_ANALYSIS_SYSTEM_PROMPT",
        },
        "diagram_structured": {
            "name": "结构化图解",
            "description": "生成结构化图解数据(JSON节点/边/表格)",
            "prompt": "输出 constrained JSON schema 的图解数据...",
            "route": "text JSON",
            "full_prompt": "见 diagram_service.py DIAGRAM_STRUCTURED_SYSTEM_PROMPT",
        },
    },
    "polish": {
        "polish": {
            "name": "文本润色",
            "description": "优化表达，修正语法",
            "prompt": "你是一个文本润色助手。请优化以下文本的表达，修正语法错误，提升可读性，保持原意不变。直接返回润色后的文本，不要解释。",
            "route": "text stream",
        },
        "summarize": {
            "name": "内容摘要",
            "description": "提取核心要点",
            "prompt": "请对以下内容提取核心要点，生成简洁的摘要。用要点列表形式输出。",
            "route": "text stream",
        },
        "tags": {
            "name": "标签推荐",
            "description": "推荐关键词标签",
            "prompt": '从以下内容中推荐 3-5 个关键词标签。返回 JSON 数组格式，例如 ["标签1", "标签2"]。不要输出其他内容。',
            "route": "text stream",
        },
    },
    "knowledge": {
        "summary": {
            "name": "知识总结",
            "description": "带引用的知识总结",
            "prompt": get_prompt_template(AiTaskType.KNOWLEDGE_SUMMARY).system_prompt[:500] + "...",
            "route": "text JSON",
            "full_prompt": get_prompt_template(AiTaskType.KNOWLEDGE_SUMMARY).system_prompt,
        },
    },
}


# --- Functions ---

def build_personal_context(my_answer: str | None, correct_answer: str | None, user_error_analysis: str | None) -> str | None:
    if not my_answer and not correct_answer and not user_error_analysis:
        return None
    ctx = "\n\n--- 个人答题上下文 ---"
    if my_answer:
        ctx += f"\n我的错误思路 / 当时答案: {my_answer}"
    if correct_answer:
        ctx += f"\n正确答案: {correct_answer}"
    if user_error_analysis:
        ctx += f"\n我自己判断的错因: {user_error_analysis}"
    ctx += (
        "\n\n请结合以上个人答题上下文："
        "\n1. 在 personalized_diagnosis 字段给出针对该学生具体错误的个性化诊断。"
        "\n2. 在 misread_signal 字段指出学生可能忽略的题目信号。"
        "\n3. 在 next_time_checklist 字段给出下次做题的检查清单。"
        "\n4. 如果学生的错误思路暴露了特定知识点薄弱，在 analysis 中针对性强化。"
    )
    return ctx


def parse_result(
    result: dict,
    related_notes: list[dict] | None = None,
    extra_warnings: list[str] | None = None,
) -> AnalyzeResponse:
    result, latex_warnings = _repair_latex_in_result(result)

    from app.services.tag_canonicalization import canonicalize_tags
    raw_tags = _list_of_strings(result.get("tags"))
    result["tags"] = canonicalize_tags(raw_tags)

    _VALID_DIAGRAM_TYPES = {"flowchart", "timeline", "formula_breakdown", "network_topology", "geometry", "state_machine"}
    raw_diagrams = result.get("diagrams", [])
    diagrams = []
    for d in raw_diagrams:
        if isinstance(d, dict) and d.get("mermaid"):
            mermaid_code = d["mermaid"].strip()
            if len(mermaid_code) < 5:
                continue
            dtype = d.get("type", "flowchart")
            if dtype not in _VALID_DIAGRAM_TYPES:
                dtype = "flowchart"
            diagrams.append(DiagramItem(
                type=dtype,
                title=d.get("title", ""),
                mermaid=mermaid_code,
            ))
    return AnalyzeResponse(
        title=result.get("title", ""),
        question=result.get("question", ""),
        correct_answer=result.get("correct_answer", ""),
        analysis=result.get("analysis", ""),
        knowledge_points=result.get("knowledge_points", ""),
        subject=result.get("subject", ""),
        difficulty=result.get("difficulty", "medium"),
        tags=_list_of_strings(result.get("tags")),
        error_reason=result.get("error_reason", ""),
        key_step=result.get("key_step", ""),
        similar_traps=_list_of_strings(result.get("similar_traps")),
        generalization=result.get("generalization", ""),
        review_advice=result.get("review_advice", ""),
        variant_questions=_list_of_strings(result.get("variant_questions")),
        related_notes=related_notes or [],
        diagrams=diagrams,
        personalized_diagnosis=result.get("personalized_diagnosis", ""),
        misread_signal=result.get("misread_signal", ""),
        next_time_checklist=_list_of_strings(result.get("next_time_checklist")),
        latex_warnings=_list_of_strings(result.get("latex_warnings")) + latex_warnings + _check_deterministic_fields(result) + (extra_warnings or []),
        visual_context=result.get("visual_context", ""),
        image_dependency=result.get("image_dependency", ""),
    )


async def find_related_notes(db: AsyncSession, subject: str | None, knowledge_points: str | None, limit: int = 3) -> list[dict]:
    conditions = []
    if subject:
        conditions.append(Note.subject == subject)
    if knowledge_points:
        keywords = [kw.strip() for kw in knowledge_points.replace("，", ",").replace("、", ",").split(",") if kw.strip()]
        for kw in keywords[:3]:
            conditions.append(Note.knowledge_points.ilike(f"%{kw}%"))
    if not conditions:
        return []
    query = (
        select(Note.slug, Note.title)
        .where(or_(*conditions))
        .where(Note.type == "note")
        .order_by(Note.updated_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return [{"slug": row.slug, "title": row.title} for row in result.all()]


def build_summary_user_content(request_body) -> str:
    """构建 knowledge-summary 的用户内容。"""
    sources = request_body.context_pack.sources
    source_context = []
    for s in sources[:10]:
        source_context.append(
            f"[{s.source_type.value}:{s.source_id}] {s.title} (field: {s.field})\n"
            f"Excerpt: {s.excerpt[:200]}" if s.excerpt else f"[{s.source_type.value}:{s.source_id}] {s.title}"
        )

    related_notes_ctx = ""
    if request_body.context_pack.related_notes:
        related_notes_ctx = "\n相关笔记:\n" + "\n".join(
            f"- {n.title} (subject: {n.subject}, slug: {n.slug})"
            for n in request_body.context_pack.related_notes[:5]
        )

    related_mistakes_ctx = ""
    if request_body.context_pack.related_mistakes:
        related_mistakes_ctx = "\n相关错题:\n" + "\n".join(
            f"- {m.title} (subject: {m.subject}, difficulty: {m.difficulty})"
            for m in request_body.context_pack.related_mistakes[:5]
        )

    stats_ctx = ""
    if request_body.context_pack.stats:
        stats = request_body.context_pack.stats
        stats_ctx = f"\n统计: 错题数={stats.mistake_count}, 笔记数={stats.note_count}"
        if stats.top_error_reasons:
            stats_ctx += f", 高频错误原因: {'、'.join(stats.top_error_reasons)}"

    return (
        f"Mode: {request_body.mode}\n"
        f"Language: {request_body.requirements.get('language', 'zh-CN')}\n"
        f"Style: {request_body.requirements.get('style', 'exam_review')}\n"
        f"Max length: {request_body.requirements.get('max_length', 1200)}\n"
        f"\n--- Source References ---\n"
        + "\n\n".join(source_context)
        + related_notes_ctx
        + related_mistakes_ctx
        + stats_ctx
        + "\n\n请根据以上来源引用生成复习总结。每个事实性结论必须绑定 source_refs。"
    )


def parse_summary_blocks(result: dict, sources: list) -> list:
    """解析 knowledge-summary 的 blocks，验证 source_refs。"""
    from app.schemas.knowledge import CitationBlock, CitationBlockType, SourceRef, SourceType

    source_map = {s.source_id: s for s in sources}

    _MISTAKE_FIELDS = {
        "analysis", "question", "correct_answer", "error_reason",
        "key_step", "generalization", "review_advice",
        "knowledge_points", "content",
    }
    _NOTE_FIELDS = {"content", "summary", "title", "knowledge_points"}

    blocks: list[CitationBlock] = []
    for block in result.get("blocks", []):
        block_type = block.get("type", "ai_inference")
        try:
            validated_type = CitationBlockType(block_type)
        except ValueError:
            validated_type = CitationBlockType.ai_inference

        raw_refs = block.get("source_refs", [])
        validated_refs: list[SourceRef] = []
        for ref in raw_refs:
            ref_source_id = ref.get("source_id", "")
            matched = source_map.get(ref_source_id)
            if not matched:
                continue

            ai_field = ref.get("field", "")
            allowed = _MISTAKE_FIELDS if matched.source_type == SourceType.mistake else _NOTE_FIELDS
            if ai_field and ai_field in allowed:
                locked_field = ai_field
            else:
                locked_field = matched.field

            validated_refs.append(SourceRef(
                source_type=matched.source_type,
                source_id=matched.source_id,
                title=matched.title,
                slug=matched.slug,
                field=locked_field,
                excerpt=matched.excerpt,
                url=matched.url,
                confidence=matched.confidence,
                match_reasons=matched.match_reasons,
            ))

        if validated_type == CitationBlockType.source_backed_claim and not validated_refs:
            validated_type = CitationBlockType.ai_inference

        blocks.append(CitationBlock(
            type=validated_type,
            text=block.get("text", ""),
            source_refs=validated_refs,
        ))

    return blocks


# --- AI config builder ---


def build_ai_config() -> dict:
    """构造 AI 配置信息（providers、image generation 等）。"""
    import os

    from app.config import get_settings

    settings = get_settings()
    general_key = settings.DASHSCOPE_API_KEY or settings.AI_API_KEY
    if settings.DASHSCOPE_API_KEY:
        general_model = settings.AI_MODEL
        if "dashscope" in settings.DASHSCOPE_BASE_URL and not general_model.startswith("qwen"):
            general_model = "qwen3.7-plus"
        general_base_url = settings.DASHSCOPE_BASE_URL
    else:
        general_model = settings.AI_MODEL
        general_base_url = settings.AI_BASE_URL
    return {
        "ai_model": general_model,
        "ai_base_url": general_base_url,
        "dashscope_model": settings.DASHSCOPE_MODEL,
        "deepseek_model": settings.DEEPSEEK_MODEL,
        "has_ai_key": bool(general_key),
        "has_dashscope_key": bool(settings.DASHSCOPE_API_KEY),
        "has_deepseek_key": bool(settings.DEEPSEEK_API_KEY),
        "general_provider": f"{general_model} (DashScope)" if settings.DASHSCOPE_API_KEY else f"{settings.AI_MODEL} (Custom)",
        "providers": [
            {
                "name": "Qwen3.7 Plus",
                "model": general_model,
                "base_url": general_base_url,
                "role": "general, fallback",
                "configured": bool(general_key),
            },
            {
                "name": "Qwen3.7 Plus Vision",
                "model": settings.DASHSCOPE_MODEL,
                "base_url": settings.DASHSCOPE_BASE_URL,
                "role": "OCR/vision primary, general model",
                "configured": bool(settings.DASHSCOPE_API_KEY),
            },
            {
                "name": "DeepSeek",
                "model": settings.DEEPSEEK_MODEL,
                "base_url": settings.DEEPSEEK_BASE_URL,
                "role": "text primary",
                "configured": bool(settings.DEEPSEEK_API_KEY),
            },
        ],
        "image_generation": {
            "model": "qwen-image-2.0-pro",
            "configured": bool(os.environ.get("DASHSCOPE_IMAGE_API_KEY")),
            "status": "configured" if os.environ.get("DASHSCOPE_IMAGE_API_KEY") else "disabled",
        },
    }


# --- SSE stream helper ---


async def stream_analyze_events(messages, gateway_call, task_type, db):
    """通用 SSE 分析事件流生成器。

    gateway_call: ai_gateway.call_vision 或 call_text
    task_type: 主调用 task_type。旧 SSE endpoint 仅作为兼容入口，
        provider 调用必须复用已注册的正式非流式 task_type，避免绕过
        ai_runs / ai_call_logs 记录。
    """
    import asyncio
    import json

    try:
        yield f"data: {json.dumps({'type': 'received', 'label': '收到请求，正在处理...'})}\n\n"
        await asyncio.sleep(0)

        yield f"data: {json.dumps({'type': 'progress', 'step': 'validating_input', 'label': '正在验证输入...'})}\n\n"
        await asyncio.sleep(0)

        yield f"data: {json.dumps({'type': 'progress', 'step': 'calling_model', 'label': '正在调用 AI 模型分析...'})}\n\n"
        await asyncio.sleep(0)

        try:
            gw = await gateway_call(task_type, messages)
            result = gw.data
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            return

        async def _repair_call(msgs, mt):
            r = await gateway_call(AiTaskType.REPAIR_DETERMINISTIC.value, msgs, max_tokens=mt)
            return r.data

        result, deterministic_warnings = await _repair_deterministic_result(result, _repair_call)

        yield f"data: {json.dumps({'type': 'progress', 'step': 'parsing_model_output', 'label': '正在解析AI分析结果...'})}\n\n"
        await asyncio.sleep(0)

        yield f"data: {json.dumps({'type': 'progress', 'step': 'finding_related_notes', 'label': '正在查找相关笔记...'})}\n\n"
        await asyncio.sleep(0)

        related = await find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
        await asyncio.sleep(0)

        parsed = parse_result(result, related, deterministic_warnings)
        yield f"data: {json.dumps({'type': 'result', 'data': parsed.model_dump()})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'label': '分析完成'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


# --- Analyze + parse helper ---


async def analyze_and_parse(result, db, gateway_call, task_type=AiTaskType.REPAIR_DETERMINISTIC.value):
    """analyze/analyze-text 共同尾部：repair + find_related + parse。"""

    async def _repair_call(msgs, mt):
        r = await gateway_call(task_type, msgs, max_tokens=mt)
        return r.data

    result, deterministic_warnings = await _repair_deterministic_result(result, _repair_call)
    related = await find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
    return parse_result(result, related, deterministic_warnings)


# --- Prompts response builder ---


def build_prompts_response() -> dict:
    """从 PROMPT_REGISTRY 动态生成 /api/ai/prompts 响应。

    遍历 PROMPT_REGISTRY，为每个 task_type 生成包含 prompt / full_prompt /
    version / json_mode / preferred_provider / max_tokens / description 的响应。
    保留原有字段（prompt / full_prompt），新增字段不破坏前端。
    """
    prompts = {}
    for task_type, template in PROMPT_REGISTRY.items():
        key = task_type.value
        sp = template.system_prompt or template.user_content_template or ""
        prompts[key] = {
            "prompt": sp[:500] + "..." if len(sp) > 500 else sp,
            "full_prompt": sp,
            "version": template.version,
            "json_mode": template.json_mode,
            "preferred_provider": template.preferred_provider,
            "max_tokens": template.max_tokens,
            "description": template.description,
        }
    return {"prompts": prompts}
