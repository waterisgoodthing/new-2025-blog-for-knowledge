import json
import uuid

from app.services.ai_service import call_ocr_model, call_text_model


QUESTION_DRAFT_SYSTEM_PROMPT = r"""你是一个严谨的错题图片识别助手。你的唯一任务是从图片或文本中提取题目信息。

重要规则：
- 只提取和结构化题目信息
- 不要推断学生的错误原因
- 不要给出个性化诊断
- 不要猜测学生为什么做错

输出严格合法 JSON，格式如下：

{
  "title": "简短题目标题，不超过30字",
  "question": "完整题目内容，包括题干、条件、选项",
  "options": ["选项A文本", "选项B文本"],
  "visual_context": "图片中与解题相关的视觉元素描述，如图表、网络拓扑、几何图形等；纯文字题目填写空字符串",
  "key_conditions": ["关键条件1", "关键条件2"],
  "candidate_answer": "如果能从题目信息推导出正确答案则填写；否则空字符串",
  "knowledge_points": "涉及的知识点，逗号分隔",
  "question_type": "题目类型：network_topology|ip_fragmentation|algorithm|math|physics|chemistry|biology|other",
  "subject": "学科名称",
  "difficulty": "easy|medium|hard",
  "tags": ["标签1", "标签2"],
  "image_dependency": "none|partial|full"
}

字段要求：
- title: 简短具体，体现核心考点
- question: 完整保留题干、条件、选项
- options: 选择题的选项列表，非选择题为空数组
- visual_context: 描述图片中的图表、拓扑、几何等视觉元素
- key_conditions: 题目的关键约束条件
- candidate_answer: 仅当题目信息足够推导时填写
- knowledge_points: 逗号分隔的知识点
- question_type: 必须是给定枚举值之一
- tags: 1-6个标签
- image_dependency: 题目对图片的依赖程度

数学公式用 LaTeX：行内 $...$，块级 $$...$$。

输出必须是严格合法 JSON，不要输出其他内容。"""

ERROR_INTERPRETATION_SYSTEM_PROMPT = r"""你是一个错因理解助手。你的任务是理解学生自己描述的错误原因，并给出结构化的解读。

核心规则：
1. 学生写的错因是唯一真相来源
2. 你可以澄清、结构化、补充逻辑链，但不能替换学生的原意
3. 不要用选项猜测替代学生的自我反思
4. 如果学生说"没有结合 cost 来看"，你的解读必须围绕 cost，不能转到 TTL 等其他因素

输出严格合法 JSON，格式如下：

{
  "summary": "一句话概括学生的错误本质",
  "diagnosis": "对学生错误的详细诊断，引用学生原话",
  "root_cause": "根本原因分析",
  "knowledge_gap": "暴露的知识缺口",
  "suggested_correction": "建议的纠正方向",
  "reasoning_trace": "从学生原话到诊断的推理链"
}

如果提供了 rejection_history，你必须：
1. 阅读每条拒绝理由
2. 在新解读中明确回应被拒绝的点
3. 修正之前解读的偏差

输出必须是严格合法 JSON，不要输出其他内容。"""

FINAL_ANALYSIS_SYSTEM_PROMPT = r"""你是一个错题解析助手。基于已确认的题目信息和已采纳的错因理解，生成最终的错题分析。

输入包含：
- question_draft: 已确认的题目信息
- user_error_reason: 学生自述的错因
- accepted_interpretation: 已采纳的 AI 错因理解

核心规则：
1. 分析必须围绕已采纳的错因理解展开
2. 不要推翻或淡化学生自述的错因
3. 给出确定性结论，不使用模糊词

输出严格合法 JSON，格式如下：

{
  "analysis": "详细解析，分步骤说明",
  "error_reason": "结合采纳的错因理解，说明错误本质",
  "key_step": "下次做题时最关键的一步",
  "similar_traps": ["相似陷阱1", "相似陷阱2"],
  "generalization": "同类题通法",
  "review_advice": "复习建议，含当天、3天后、7天后安排",
  "variant_questions": ["变式题1"]
}

数学公式用 LaTeX：行内 $...$，块级 $$...$$。

输出必须是严格合法 JSON，不要输出其他内容。"""


async def generate_question_draft(images: list[dict], text: str) -> dict:
    """T2-01: Extract question structure from image/text without personal inference."""
    if images:
        content = [{"type": "text", "text": QUESTION_DRAFT_SYSTEM_PROMPT}]
        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{img['mime_type']};base64,{img['base64']}"},
            })
        if text:
            content.append({"type": "text", "text": f"补充文本: {text}"})
        messages = [
            {"role": "system", "content": "你是题目信息提取助手。只提取题目，不推断错因。请始终以 JSON 格式回复。"},
            {"role": "user", "content": content},
        ]
        result = await call_ocr_model(messages)
    else:
        user_content = text
        messages = [
            {"role": "system", "content": QUESTION_DRAFT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        result = await call_text_model(messages)

    return _normalize_question_draft(result)


def _normalize_question_draft(raw: dict) -> dict:
    """Normalize raw AI output to QuestionDraftResponse shape."""
    from app.routers.ai import _list_of_strings

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

    messages = [
        {"role": "system", "content": ERROR_INTERPRETATION_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = await call_text_model(messages)

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

    messages = [
        {"role": "system", "content": FINAL_ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = await call_text_model(messages)

    from app.routers.ai import _list_of_strings

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
