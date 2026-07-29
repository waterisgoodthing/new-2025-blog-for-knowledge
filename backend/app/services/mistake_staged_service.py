import json
import uuid

from app.services.ai_gateway import call_text, call_vision
from app.services.ai_prompt_registry import (
    build_text_messages,
    build_vision_messages,
    get_prompt_template,
)
from app.services.ai_task_types import AiTaskType


async def generate_question_draft(images: list[dict], text: str) -> dict:
    """T2-01: Extract question structure from image/text without personal inference."""
    if images:
        content = [{"type": "text", "text": get_prompt_template(AiTaskType.MISTAKE_QUESTION_DRAFT).system_prompt}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{img['mime_type']};base64,{img['base64']}"},
            })
        if text:
            content.append({"type": "text", "text": f"补充文本: {text}"})
        messages = build_vision_messages(
            AiTaskType.MISTAKE_QUESTION_DRAFT,
            content,
        )
        gw = await call_vision(AiTaskType.MISTAKE_QUESTION_DRAFT, messages)
        if not gw.success:
            raise RuntimeError(gw.error or "AI call failed")
        result = gw.data
    else:
        user_content = text
        messages = build_text_messages(AiTaskType.MISTAKE_QUESTION_DRAFT, user_content)
        gw = await call_text(AiTaskType.MISTAKE_QUESTION_DRAFT, messages)
        if not gw.success:
            raise RuntimeError(gw.error or "AI call failed")
        result = gw.data

    return _normalize_question_draft(result)


def _normalize_question_draft(raw: dict) -> dict:
    """Normalize raw AI output to QuestionDraftResponse shape."""
    from app.services.ai_repair_service import _list_of_strings

    options = raw.get("options", [])
    if isinstance(options, str):
        options = [o.strip() for o in options.split("\n") if o.strip()]

    key_conditions = raw.get("key_conditions", [])
    if isinstance(key_conditions, str):
        key_conditions = [c.strip() for c in key_conditions.replace("，", ",").split(",") if c.strip()]

    return {
        "title": str(raw.get("title", ""))[:30],
        "question": raw.get("question", ""),
        "options": options,
        "visual_context": raw.get("visual_context", ""),
        "key_conditions": key_conditions,
        "candidate_answer": raw.get("candidate_answer", ""),
        "knowledge_points": raw.get("knowledge_points", ""),
        "question_type": raw.get("question_type", "other"),
        "subject": raw.get("subject", ""),
        "difficulty": raw.get("difficulty", "medium"),
        "tags": _list_of_strings(raw.get("tags")),
        "image_dependency": raw.get("image_dependency", "none"),
    }


async def generate_error_interpretation(
    question_draft: dict,
    user_error_reason: str,
    rejection_history: list[str] | None = None,
) -> dict:
    """T2-03: Generate AI interpretation of learner's error reason."""
    user_content = f"""题目信息：
{json.dumps(question_draft, ensure_ascii=False, indent=2)}

学生自述错因：
{user_error_reason}"""

    if rejection_history:
        user_content += "\n\n之前的拒绝理由："
        for i, reason in enumerate(rejection_history, 1):
            user_content += f"\n{i}. {reason}"
        user_content += "\n\n请根据以上拒绝理由修正你的解读。"

    messages = build_text_messages(AiTaskType.MISTAKE_ERROR_INTERPRETATION, user_content)

    gw = await call_text(AiTaskType.MISTAKE_ERROR_INTERPRETATION, messages)
    if not gw.success:
        raise RuntimeError(gw.error or "AI call failed")
    result = gw.data

    interpretation_id = str(uuid.uuid4())[:8]
    version = len(rejection_history or []) + 1

    return {
        "interpretation_id": interpretation_id,
        "version": version,
        "summary": result.get("summary", ""),
        "diagnosis": result.get("diagnosis", ""),
        "root_cause": result.get("root_cause", ""),
        "knowledge_gap": result.get("knowledge_gap", ""),
        "suggested_correction": result.get("suggested_correction", ""),
        "reasoning_trace": result.get("reasoning_trace", ""),
    }


async def generate_final_analysis(
    question_draft: dict,
    user_error_reason: str,
    accepted_interpretation: dict,
) -> dict:
    """T2-05: Generate final analysis using accepted interpretation."""
    user_content = f"""已确认题目信息：
{json.dumps(question_draft, ensure_ascii=False, indent=2)}

学生自述错因：
{user_error_reason}

已采纳的错因理解：
{json.dumps(accepted_interpretation, ensure_ascii=False, indent=2)}"""

    messages = build_text_messages(AiTaskType.MISTAKE_FINAL_ANALYSIS, user_content)

    gw = await call_text(AiTaskType.MISTAKE_FINAL_ANALYSIS, messages)
    if not gw.success:
        raise RuntimeError(gw.error or "AI call failed")
    result = gw.data

    from app.services.ai_repair_service import _list_of_strings

    return {
        "analysis": result.get("analysis", ""),
        "error_reason": result.get("error_reason", ""),
        "key_step": result.get("key_step", ""),
        "similar_traps": _list_of_strings(result.get("similar_traps")),
        "generalization": result.get("generalization", ""),
        "review_advice": result.get("review_advice", ""),
        "variant_questions": _list_of_strings(result.get("variant_questions")),
        "accepted_interpretation_id": accepted_interpretation.get("interpretation_id", ""),
        "accepted_interpretation_version": accepted_interpretation.get("version", 1),
    }
