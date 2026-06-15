import json
import os
import re
import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note
from app.routers.auth import get_current_admin
from app.schemas.ai import (
    AnalyzeRequest,
    AnalyzeResponse,
    DiagramItem,
    DiagramResponse,
    DiagramStrategyRequest,
    ErrorInterpretationRequest,
    ErrorInterpretationResponse,
    FinalAnalysisRequest,
    FinalAnalysisResponse,
    InterpretationRejectionRequest,
    QuestionDraftConfirmRequest,
    QuestionDraftConfirmResponse,
    QuestionDraftRequest,
    QuestionDraftResponse,
    TextAnalyzeRequest,
)
from app.schemas.knowledge import (
    CitationBlock,
    CitationBlockType,
    InsufficientContextResponse,
    KnowledgeSummaryRequest,
    KnowledgeSummaryResponse,
    SourceRef,
    SourceType,
)
from app.services.ai_service import call_ocr_model, call_text_model

router = APIRouter(prefix="/api/ai", tags=["ai"])

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60


@router.get("/config")
async def get_ai_config(
    _admin=Depends(get_current_admin),
):
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


def _check_rate_limit(key: str = "global") -> None:
    now = time.time()
    timestamps = _rate_limit_store[key]
    _rate_limit_store[key] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s.")
    _rate_limit_store[key].append(now)

OCR_SYSTEM_PROMPT = r"""你是一个严谨的错题图片识别与解题助手，负责从用户上传的错题图片中提取题目信息，必要时进行解题，并输出结构化 JSON。

你的核心任务是：

1. 尽可能准确识别图片中的文字、公式、选项、图表信息。
2. 判断题目所属学科、题型、难度和知识点。
3. 提取题目原文，保持题干、条件、选项、公式的完整性。
4. 如果图片中已经包含答案或解析，需要一并提取。
5. 如果图片中没有答案或解析，但题目信息足够完整，你应该进行解题并给出正确答案和详细解析。
6. 如果图片信息不足以解题，明确指出缺失的具体信息，不要编造。
7. 如果识别出题目属于算法、数据结构或编程题，需要在 tags 和 knowledge_points 中体现，但不要强行生成完整代码。完整代码由解题 AI 负责。

请严格遵守以下规则：

* 只根据图片中可见内容进行识别和推断。
* 不要臆造图片中不存在的信息。
* 数学公式尽量使用 LaTeX 表示。
* 选择题需要保留所有选项。
* 多小问题目需要保留小问编号。
* 如果图片模糊、遮挡或无法完整识别，需要在 analysis 中说明识别不确定的位置。
* 输出必须是合法 JSON。
* 不要输出 Markdown。
* 不要使用 ```json 代码块。
* 不要在 JSON 前后添加任何解释性文字。

## 确定性分析规则

* 最终的 correct_answer、analysis、error_reason、key_step 中不得使用"可能""也许""似乎""大概""推测"等模糊词语来推导结论。
* 如果 OCR 识别不确定，可以在专门的 OCR 说明中标注，但不能用模糊词语作为最终推理依据。
* 如果信息不足以确定答案，必须明确说明"信息不足"并列出缺失条件，而不是用"可能"继续推导。
* 对于计算题，中间值必须前后一致。如果出现矛盾，必须指出矛盾而非强行解释。

请按照以下 JSON 格式返回：

{
  "title": "题目标题，若图片中没有明确标题，则根据题目内容概括一个简短标题",
  "question": "完整题目内容，包括题干、条件、选项、公式、图表文字信息等",
  "correct_answer": "正确答案；如果图片中已有答案则提取，如果题目信息足够则求解；信息不足时填写空字符串",
  "analysis": "详细解析；如果图片中已有解析则提取，如果题目信息足够则给出完整解题过程；信息不足时说明缺失内容",
  "knowledge_points": "题目涉及的知识点，多个知识点用中文逗号分隔",
  "subject": "学科名称，例如：数学、英语、计算机、数据结构、算法、物理、化学、政治、未知",
  "difficulty": "easy|medium|hard",
  "tags": ["标签1", "标签2"],
  "error_reason": "如果图片中能看出错误原因则填写；否则填写空字符串",
  "key_step": "本题最关键的解题步骤或判断点；无法判断时填写空字符串",
  "similar_traps": ["相似易错点1", "相似易错点2"],
  "generalization": "这类题可迁移的一般方法；无法判断时填写空字符串",
  "review_advice": "复习建议；无法判断时填写空字符串",
  "variant_questions": ["变式题1", "变式题2"],
  "diagrams": [{"type": "flowchart", "title": "图示标题", "mermaid": "graph TD; A-->B"}],
  "visual_context": "图片中与解题相关的视觉元素描述，如图表、几何图形、网络拓扑、流程图等；纯文字题目填写空字符串",
  "image_dependency": "none|partial|full — 题目是否依赖图片中的视觉元素才能完整理解或解答"
}

字段要求：

1. title
   * 简短、具体。
   * 不超过 30 个中文字符。
   * 不要写成"题目""错题""图片识别结果"这类无信息标题。

2. question
   * 必须尽量完整。
   * 选择题需要包含 A、B、C、D 等选项。
   * 判断题需要保留判断对象。
   * 填空题需要保留空缺位置。
   * 编程题需要保留输入格式、输出格式、样例输入、样例输出和数据范围。

3. correct_answer
   * 如果图片中已有答案，提取之。
   * 如果图片中没有答案但题目信息足够，进行求解。
   * 如果信息不足以求解，填写空字符串。
   * 不得使用模糊词语作为推导依据。

4. analysis
   * 如果图片中已有解析，提取之。
   * 如果图片中没有解析但题目信息足够，给出完整解题过程。
   * 如果 OCR 不确定，需要写明，例如："部分公式识别不确定：第 2 行分母可能为 x+1。"
   * 不得使用"可能因…所以答案是…"这种模糊推导。

5. knowledge_points
   * 根据题目内容提取知识点。
   * 数学题示例：函数、导数、极限、线性代数、概率论。
   * 算法题示例：二分查找、动态规划、贪心、图论、最短路、并查集。

6. subject
   * 只能填写一个主要学科。
   * 如果是算法或编程题，优先填写"算法"或"数据结构"。
   * 如果无法判断，填写"未知"。

7. difficulty
   * 简单题填写 easy。
   * 中等题填写 medium。
   * 较难题填写 hard。
   * 无法判断时默认填写 medium。

8. tags
   * 返回字符串数组。
   * 至少 1 个，最多 6 个。
   * 算法题需要包含"算法"或"编程"。
   * 图片识别不完整时，可以包含"识别不完整"。

9. extended mistake fields
   * error_reason 聚焦"为什么错"，不要重复完整解析。
   * key_step 聚焦"下一次做题时最先抓住哪一步"。
   * similar_traps 返回 0 到 4 条相似陷阱。
   * generalization 总结同类题通法。
   * review_advice 给出当天、3 天后、7 天后的复习建议。
   * variant_questions 返回 0 到 3 道短变式题。

10. visual_context
    * 描述图片中与解题直接相关的视觉元素。
    * 纯文字题目填写空字符串。
    * 包含图表、几何图形、网络拓扑、流程图等时，简要描述其内容和与题目的关系。

11. image_dependency
    * none：题目完全是文字，不依赖图片。
    * partial：图片提供了辅助信息但文字已足够理解。
    * full：题目必须看图才能完整理解或解答。

输出必须是严格合法 JSON。

## 数学公式规范
所有数学公式必须使用 LaTeX 语法：
- 行内公式：$...$ 例如 $E = mc^2$
- 块级公式：$$...$$ 例如 $$\frac{6 \times 8}{100 \times 10^6} = 0.48\mu s$$
- 禁止输出裸 \frac、\sqrt、\int 等命令，必须包裹在 $ 或 $$ 中
- 希腊字母用 LaTeX：$\mu$ 而非 \mu 或 μ
- 单位用 LaTeX：$\mu s$、$m/s^2$

## 图示规范
如果题目涉及以下类型，必须在 diagrams 字段输出对应的 Mermaid 图示：
- 流程/算法题 → type: "flowchart", 用 Mermaid graph TD 语法
- 时间线/事件顺序 → type: "timeline", 用 Mermaid timeline 语法
- 公式推导/数学证明 → type: "formula_breakdown", 用 Mermaid graph 语法展示推导步骤
- 网络拓扑/协议 → type: "network_topology", 用 Mermaid graph 语法
- 几何图形 → type: "geometry", 用 Mermaid 语法描述几何关系
- 状态机/有限自动机 → type: "state_machine", 用 Mermaid stateDiagram 语法
如果题目不需要图示，diagrams 返回空数组 []。
每个 diagram 的 mermaid 字段必须是有效的 Mermaid 语法字符串。"""

TEXT_SYSTEM_PROMPT = r"""你是一个严谨的学习解题助手，负责根据用户提供的题目文本进行完整分析，并输出结构化 JSON。

你的核心任务是：

1. 理解题目内容。
2. 判断题目所属学科、难度和知识点。
3. 给出正确答案。
4. 给出清晰、可核查的解析过程。
5. 如果题目是算法、数据结构或编程题，必须同时给出 Python 和 C 语言参考实现。
6. 如果题目信息不足，必须明确指出缺失条件，不能编造题目条件。

请严格遵守以下规则：

* 输出必须是合法 JSON。
* 不要输出 Markdown。
* 不要使用 ```json 代码块。
* 不要在 JSON 前后添加任何解释性文字。
* 数学公式尽量使用 LaTeX 表示。
* 解析过程需要分步骤说明。
* 不能跳步给结论。
* 不确定的地方必须在 analysis 中说明。
* 不要承诺"必对""一定满分"等绝对化表述。
* 如果题目无法求解，需要说明原因，并给出需要补充的信息。

请按照以下 JSON 格式返回：

{
  "title": "题目标题",
  "question": "整理后的完整题目文本",
  "correct_answer": "正确答案；算法题必须包含 Python 和 C 两种参考实现",
  "analysis": "详细解析；算法题必须包含算法思路、正确性说明、时间复杂度、空间复杂度",
  "knowledge_points": "涉及的知识点，多个知识点用中文逗号分隔",
  "subject": "学科名称，例如：数学、英语、计算机、数据结构、算法、物理、化学、政治、未知",
  "difficulty": "easy|medium|hard",
  "tags": ["标签1", "标签2"],
  "error_reason": "错误原因，说明容易错在哪里",
  "key_step": "关键步骤，说明解这道题最重要的一步",
  "similar_traps": ["相似易错点1", "相似易错点2"],
  "generalization": "举一反三，说明同类题的一般解法",
  "review_advice": "复习建议，包含今天、3 天后、7 天后的安排",
  "variant_questions": ["变式题1", "变式题2"],
  "diagrams": [{"type": "flowchart", "title": "图示标题", "mermaid": "graph TD; A-->B"}]
}

字段要求：

1. title
   * 根据题目内容生成简短标题。
   * 不超过 30 个中文字符。
   * 标题应体现核心考点，例如"二分答案求最小最大值""导数判断函数单调性"。

2. question
   * 保留题目原意。
   * 可以适度整理换行和格式。
   * 不要改变题目条件。
   * 如果原题存在明显缺失，需要在 question 中保留原始缺失状态，并在 analysis 中说明。

3. correct_answer
   * 普通数学题：给出最终答案。
   * 选择题：给出选项和必要结果。
   * 填空题：给出填空结果。
   * 简答题：给出核心结论。
   * 算法题：必须包含以下结构：

   【Python 实现】
   （Python 代码）

   【C 语言实现】
   （C 语言代码）

   算法题代码要求：
   * Python 代码优先使用标准输入输出。
   * C 语言代码使用 scanf/printf 或 fgets 等标准输入输出。
   * 代码应尽量完整可运行。
   * 不要依赖第三方库。
   * 变量命名清晰。
   * 如果题目没有明确输入输出格式，需要给出核心函数实现，并说明假设。

4. analysis
   * 普通题需要包含：题意分析、解题步骤、关键公式或关键推理、最终结论。
   * 数学题需要：写出关键公式、说明变形依据、避免只给答案。
   * 概率题需要：明确样本空间、事件、条件概率或独立性假设、写出计算过程。
   * 线性代数题需要：明确矩阵、向量、秩、特征值、线性相关性等核心对象、给出必要的行变换或理论依据。
   * 算法题必须包含：题意抽象、暴力思路、优化思路、核心算法、正确性说明、时间复杂度、空间复杂度、易错点。

   算法题复杂度格式示例：
   时间复杂度：O(n log n)
   空间复杂度：O(n)

5. knowledge_points
   * 提取核心知识点。
   * 多个知识点用中文逗号分隔。
   * 算法题示例：二分答案、贪心、动态规划、前缀和、图论、最短路、并查集、栈、队列、哈希表。
   * 数学题示例：导数、极限、定积分、矩阵秩、特征值、条件概率、全概率公式、贝叶斯公式。

6. subject
   * 只能填写一个主要学科。
   * 算法或编程题优先填写"算法"。
   * 数据结构题优先填写"数据结构"。
   * 如果无法判断，填写"未知"。

7. difficulty
   * easy：直接套公式、基础概念题、简单模拟题。
   * medium：需要两步以上推理、常规算法题、综合题。
   * hard：需要复杂证明、多知识点结合、较高算法设计难度。
   * 无法判断时默认填写 medium。

8. tags
   * 返回字符串数组。
   * 至少 1 个，最多 8 个。
   * 应包含题型、知识点或能力标签。
   * 算法题必须包含"算法"或"编程"。

9. extended mistake fields
   * error_reason 必须指出用户最可能犯错的位置。
   * key_step 必须写出解题过程中最关键的一步。
   * similar_traps 返回 2 到 4 条相似陷阱。
   * generalization 总结同类题通法和识别信号。
   * review_advice 给出清晰复习安排，至少包含当天、3 天后、7 天后。
   * variant_questions 返回 1 到 3 道短变式题，不要过长。

算法题识别规则：

只要题目满足以下任一条件，就视为算法或编程题：

* 出现"输入""输出""样例输入""样例输出""数据范围"
* 要求"编写程序""设计算法""输出结果"
* 涉及数组、字符串、图、树、栈、队列、链表、排序、搜索、动态规划、贪心、二分、最短路、并查集等
* 题目来自蓝桥杯、ACM、LeetCode、洛谷、牛客、Codeforces 等编程训练场景
* 要求分析时间复杂度或空间复杂度

如果检测到算法题，correct_answer 中必须包含 Python 和 C 语言代码，analysis 中必须包含复杂度分析。

如果不是算法题，不要强行生成代码。

再次强调：

输出必须是严格合法 JSON。
不要输出 JSON 以外的任何内容。

## 数学公式规范
所有数学公式必须使用 LaTeX 语法：
- 行内公式：$...$ 例如 $E = mc^2$
- 块级公式：$$...$$ 例如 $$\frac{6 \times 8}{100 \times 10^6} = 0.48\mu s$$
- 禁止输出裸 \frac、\sqrt、\int 等命令，必须包裹在 $ 或 $$ 中
- 希腊字母用 LaTeX：$\mu$ 而非 \mu 或 μ
- 单位用 LaTeX：$\mu s$、$m/s^2$

## 图示规范
如果题目涉及以下类型，必须在 diagrams 字段输出对应的 Mermaid 图示：
- 流程/算法题 → type: "flowchart", 用 Mermaid graph TD 语法
- 时间线/事件顺序 → type: "timeline", 用 Mermaid timeline 语法
- 公式推导/数学证明 → type: "formula_breakdown", 用 Mermaid graph 语法展示推导步骤
- 网络拓扑/协议 → type: "network_topology", 用 Mermaid graph 语法
- 几何图形 → type: "geometry", 用 Mermaid 语法描述几何关系
- 状态机/有限自动机 → type: "state_machine", 用 Mermaid stateDiagram 语法
如果题目不需要图示，diagrams 返回空数组 []。
每个 diagram 的 mermaid 字段必须是有效的 Mermaid 语法字符串。"""


def _build_personal_context(my_answer: str | None, correct_answer: str | None, user_error_analysis: str | None) -> str | None:
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


def _list_of_strings(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        normalized = value.replace("，", ",").replace("、", ",").replace("\n", ",")
        return [item.strip() for item in normalized.split(",") if item.strip()]
    return [str(value)]


_HEDGE_WORDS = re.compile(r'(?:可能|也许|似乎|大概|推测)')
_HEDGE_ALLOWED_CONTEXT = re.compile(r'(?:识别不确定|OCR|信息不足|缺失|无法确定|不确定|模糊|遮挡)')


def _check_deterministic_fields(result: dict) -> list[str]:
    warnings = []
    strict_fields = ['correct_answer', 'analysis', 'error_reason', 'key_step']
    for field in strict_fields:
        value = result.get(field, '')
        if not isinstance(value, str) or not value:
            continue
        if _HEDGE_WORDS.search(value) and not _HEDGE_ALLOWED_CONTEXT.search(value):
            warnings.append(f"{field} 包含模糊表述，可能影响结论确定性")
    return warnings


async def _repair_deterministic_result(
    result: dict,
    model_call: Callable[[list[dict], int], Awaitable[dict]],
) -> tuple[dict, list[str]]:
    warnings = _check_deterministic_fields(result)
    if not warnings:
        return result, []

    repair_messages = [
        {
            "role": "system",
            "content": (
                "你是错题分析结果的确定性校对器。你会收到上一轮 AI 输出的 JSON。"
                "请只返回修正后的完整 JSON，不要添加解释文字。"
                "必须修复以下问题："
                "1. correct_answer、analysis、error_reason、key_step 中不得使用“可能”“也许”“似乎”“大概”“推测”等模糊词来形成最终结论；"
                "2. correct_answer 必须与 analysis 的推导结论一致；"
                "3. 如果题目信息足够，必须给出唯一确定结论；"
                "4. 如果题目信息不足，correct_answer 留空，analysis 明确写“信息不足”并列出缺失条件；"
                "5. 不要讨论教材预期、其他理解、也不要保留互相矛盾的答案。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(result, ensure_ascii=False),
        },
    ]

    try:
        repaired = await model_call(repair_messages, 4000)
    except Exception as e:
        return result, warnings + [f"确定性修复调用失败: {str(e)[:120]}"]

    repaired_warnings = _check_deterministic_fields(repaired)
    if repaired_warnings:
        return repaired, repaired_warnings
    return repaired, []


_LATEX_COMMANDS = re.compile(r'\\(?:frac|sqrt|int|sum|prod|lim|log|ln|sin|cos|tan|sec|csc|cot|arcsin|arccos|arctan|alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Phi|Psi|Omega|infty|partial|nabla|pm|mp|times|div|cdot|leq|geq|neq|approx|equiv|subset|supset|subseteq|supseteq|cup|cap|emptyset|forall|exists|in|notin|rightarrow|leftarrow|Rightarrow|Leftarrow|ldots|cdots|vdots|ddots|quad|qquad|text|mathrm|mathbf|mathit|overline|underline|hat|bar|vec|tilde|dot|ddot)')
_FORMULA_LINE = re.compile(r'(?:[\^_{}\[\]]|[a-zA-Z]\s*[=<>≤≥≠]\s*|\\[a-zA-Z]+|\d+\s*[-+*/=]\s*\d+)')
_UNIT_PATTERN = re.compile(r'\b\d+\.?\d*\s*(?:μs|ms|ns|km|m|cm|mm|kg|g|mg|A|V|Ω|Hz|kHz|MHz|GHz|dB|Pa|kPa|MPa|J|kJ|W|kW|eV|mol|rad|sr|°C|°F|K)\b')
_GREEK_LETTERS = re.compile(r'[αβγδεζηθικλμνξπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΠΡΣΤΥΦΧΨΩ]')
_CODE_LIKE_LINE = re.compile(r'\b(?:def|return|if|else|elif|for|while|int|float|double|char|void|printf|scanf|include|import|class|const|let|var)\b|[;:]|==|!=|<=|>=|\+\+|--|&&|\|\|')
_PLAIN_IDENTIFIER_ASSIGNMENT = re.compile(r'^[A-Za-z]+\s*=\s*[A-Za-z]+$')
_CHOICE_OPTION_LINE = re.compile(r'^[A-Ha-h][\.、．\)]\s*')


def _repair_latex_in_text(text: str) -> tuple[str, list[str]]:
    if not text:
        return text, []

    warnings = []

    lines = text.split('\n')
    repaired_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            repaired_lines.append(line)
            continue

        if '$' in stripped:
            repaired_lines.append(line)
            continue

        has_latex_cmd = bool(_LATEX_COMMANDS.search(stripped))
        has_operators = bool(re.search(r'[=^_{}]', stripped))
        has_greek = bool(_GREEK_LETTERS.search(stripped))
        has_unit = bool(_UNIT_PATTERN.search(stripped))
        looks_formula = bool(_FORMULA_LINE.search(stripped))
        looks_code = (
            bool(_CODE_LIKE_LINE.search(stripped))
            or bool(_PLAIN_IDENTIFIER_ASSIGNMENT.fullmatch(stripped))
            or bool(_CHOICE_OPTION_LINE.match(stripped))
            or bool(re.search(r'^\s{2,}', line))
        )
        is_short = len(stripped) < 120
        has_prose_words = bool(re.search(r'\b(?:the|is|and|or|of|in|to|that|this|with|for|are|was|were|be|been|has|have|had|do|does|did|will|would|could|should|may|might|can|shall|not|but|if|then|else|when|where|how|what|which|who|whom|why)\b', stripped, re.IGNORECASE))
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', stripped))

        should_wrap = False
        if has_latex_cmd and is_short and not has_prose_words and not has_chinese:
            should_wrap = True
        elif (
            (looks_formula or has_operators or has_greek or has_unit)
            and is_short
            and not has_prose_words
            and not has_chinese
            and not has_latex_cmd
            and not looks_code
            and not re.search(r'(?<!\\)[a-zA-Z]{4,}', stripped)
        ):
            should_wrap = True

        if should_wrap:
            if stripped.startswith('$$'):
                repaired_lines.append(line)
            else:
                repaired_lines.append(f'$${stripped}$$')
                warnings.append(f'auto-wrapped bare LaTeX: {stripped[:60]}')
        else:
            repaired_lines.append(line)

    return '\n'.join(repaired_lines), warnings


def _repair_latex_in_result(result: dict) -> tuple[dict, list[str]]:
    all_warnings = []
    fields_to_check = ['question', 'correct_answer', 'analysis', 'knowledge_points',
                       'error_reason', 'key_step', 'generalization', 'review_advice']

    for field in fields_to_check:
        value = result.get(field, '')
        if isinstance(value, str) and value:
            repaired, warns = _repair_latex_in_text(value)
            if repaired != value:
                result[field] = repaired
                all_warnings.extend(warns)

    for field in ['variant_questions', 'similar_traps']:
        items = result.get(field, [])
        if isinstance(items, list):
            repaired_items = []
            for item in items:
                if isinstance(item, str):
                    repaired, warns = _repair_latex_in_text(item)
                    repaired_items.append(repaired)
                    all_warnings.extend(warns)
                else:
                    repaired_items.append(item)
            result[field] = repaired_items

    return result, all_warnings


def _parse_result(
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


async def _find_related_notes(db: AsyncSession, subject: str | None, knowledge_points: str | None, limit: int = 3) -> list[dict]:
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


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_mistake(
    req: AnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    if not req.images:
        raise HTTPException(status_code=400, detail="At least one image is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze", after={"image_count": len(req.images)},
    )

    content = [{"type": "text", "text": OCR_SYSTEM_PROMPT}]

    for img in req.images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{img.mime_type};base64,{img.base64}"},
            }
        )

    personal_ctx = _build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
    if personal_ctx:
        content.append({"type": "text", "text": personal_ctx})

    messages = [
        {"role": "system", "content": "你是一个严谨的错题图片识别与解题助手。请始终以 JSON 格式回复。"},
        {"role": "user", "content": content},
    ]

    try:
        result = await call_ocr_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    result, deterministic_warnings = await _repair_deterministic_result(result, call_ocr_model)
    related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
    return _parse_result(result, related, deterministic_warnings)


@router.post("/analyze-text", response_model=AnalyzeResponse)
async def analyze_text(
    req: TextAnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze_text", after={"text_length": len(req.text)},
    )

    user_content = req.text
    personal_ctx = _build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
    if personal_ctx:
        user_content += personal_ctx

    messages = [
        {"role": "system", "content": TEXT_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        result = await call_text_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    result, deterministic_warnings = await _repair_deterministic_result(result, call_text_model)
    related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
    return _parse_result(result, related, deterministic_warnings)


@router.post("/analyze-stream")
async def analyze_mistake_stream(
    req: AnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze_stream", after={"image_count": len(req.images)},
    )

    async def event_stream():
        import asyncio
        try:
            yield f"data: {json.dumps({'type': 'received', 'label': '收到请求，正在处理...'})}\n\n"
            await asyncio.sleep(0)

            if not req.images:
                yield f"data: {json.dumps({'type': 'error', 'message': '至少需要一张图片'})}\n\n"
                return

            yield f"data: {json.dumps({'type': 'progress', 'step': 'validating_input', 'label': '正在验证输入...'})}\n\n"
            await asyncio.sleep(0)

            content = [{"type": "text", "text": OCR_SYSTEM_PROMPT}]
            for img in req.images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{img.mime_type};base64,{img.base64}"},
                })

            personal_ctx = _build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
            if personal_ctx:
                content.append({"type": "text", "text": personal_ctx})

            messages = [
                {"role": "system", "content": "你是一个严谨的错题图片识别与解题助手。请始终以 JSON 格式回复。"},
                {"role": "user", "content": content},
            ]

            yield f"data: {json.dumps({'type': 'progress', 'step': 'calling_model', 'label': '正在调用 AI 模型分析图片...'})}\n\n"
            await asyncio.sleep(0)

            try:
                result = await call_ocr_model(messages)
            except ValueError as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return
            except RuntimeError as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return

            result, deterministic_warnings = await _repair_deterministic_result(result, call_ocr_model)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'parsing_model_output', 'label': '正在解析AI分析结果...'})}\n\n"
            await asyncio.sleep(0)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'finding_related_notes', 'label': '正在查找相关笔记...'})}\n\n"
            await asyncio.sleep(0)

            related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
            await asyncio.sleep(0)

            parsed = _parse_result(result, related, deterministic_warnings)
            yield f"data: {json.dumps({'type': 'result', 'data': parsed.model_dump()})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'label': '分析完成'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    })


@router.post("/analyze-text-stream")
async def analyze_text_stream(
    req: TextAnalyzeRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_analyze_text_stream", after={"text_length": len(req.text)},
    )

    async def event_stream():
        import asyncio
        try:
            yield f"data: {json.dumps({'type': 'received', 'label': '收到请求，正在处理...'})}\n\n"
            await asyncio.sleep(0)

            if not req.text.strip():
                yield f"data: {json.dumps({'type': 'error', 'message': '请输入题目文本'})}\n\n"
                return

            yield f"data: {json.dumps({'type': 'progress', 'step': 'validating_input', 'label': '正在验证输入...'})}\n\n"
            await asyncio.sleep(0)

            user_content = req.text
            personal_ctx = _build_personal_context(req.my_answer, req.correct_answer, req.user_error_analysis)
            if personal_ctx:
                user_content += personal_ctx

            messages = [
                {"role": "system", "content": TEXT_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ]

            yield f"data: {json.dumps({'type': 'progress', 'step': 'calling_model', 'label': '正在调用 AI 模型分析题目...'})}\n\n"
            await asyncio.sleep(0)

            try:
                result = await call_text_model(messages)
            except ValueError as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return
            except RuntimeError as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return

            result, deterministic_warnings = await _repair_deterministic_result(result, call_text_model)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'parsing_model_output', 'label': '正在解析AI分析结果...'})}\n\n"
            await asyncio.sleep(0)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'finding_related_notes', 'label': '正在查找相关笔记...'})}\n\n"
            await asyncio.sleep(0)

            related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
            await asyncio.sleep(0)

            parsed = _parse_result(result, related, deterministic_warnings)
            yield f"data: {json.dumps({'type': 'result', 'data': parsed.model_dump()})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'label': '分析完成'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    })


VARIANT_SYSTEM_PROMPT = """你是一个严谨的出题助手。根据给定的知识点和学科，生成一道变式练习题。

要求：
- 题目应考查相同知识点，但题干、数值或场景与原题不同
- 难度适中
- 必须给出正确答案和简要解析
- 输出严格合法 JSON

输出格式：
{
  "question": "完整题目文本",
  "correct_answer": "正确答案",
  "analysis": "简要解析，分步骤说明",
  "difficulty": "easy|medium|hard",
  "knowledge_points": "涉及的知识点"
}

不要输出 JSON 以外的任何内容。"""


@router.post("/generate-variant")
async def generate_variant(
    req: dict,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    knowledge_point = req.get("knowledge_point", "").strip()
    subject = req.get("subject", "").strip()
    if not knowledge_point:
        raise HTTPException(status_code=400, detail="knowledge_point is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_generate_variant", after={"knowledge_point": knowledge_point},
    )

    user_content = f"知识点: {knowledge_point}"
    if subject:
        user_content += f"\n学科: {subject}"

    messages = [
        {"role": "system", "content": VARIANT_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        result = await call_text_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "question": result.get("question", ""),
        "correct_answer": result.get("correct_answer", ""),
        "analysis": result.get("analysis", ""),
        "difficulty": result.get("difficulty", "medium"),
        "knowledge_points": result.get("knowledge_points", knowledge_point),
        "subject": subject,
    }


KNOWLEDGE_CARD_SYSTEM_PROMPT = """你是一个严谨的学习助手。根据给定的知识点和学科，生成一张结构化的知识卡片。

要求：
- 涵盖知识点的核心概念、公式/定理、典型应用、常见易错点
- 内容准确、条理清晰
- 适合作为复习提纲使用
- 输出严格合法 JSON

输出格式：
{
  "title": "知识卡片标题",
  "content": "知识卡片的完整 Markdown 内容，包含：核心概念、关键公式/定理、典型例题思路、易错点提醒",
  "knowledge_points": "涉及的知识点",
  "subject": "学科"
}

不要输出 JSON 以外的任何内容。"""


@router.post("/generate-knowledge-card")
async def generate_knowledge_card(
    req: dict,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    knowledge_point = req.get("knowledge_point", "").strip()
    subject = req.get("subject", "").strip()
    if not knowledge_point:
        raise HTTPException(status_code=400, detail="knowledge_point is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_generate_knowledge_card", after={"knowledge_point": knowledge_point},
    )

    user_content = f"知识点: {knowledge_point}"
    if subject:
        user_content += f"\n学科: {subject}"

    messages = [
        {"role": "system", "content": KNOWLEDGE_CARD_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        result = await call_text_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "title": result.get("title", knowledge_point),
        "content": result.get("content", ""),
        "knowledge_points": result.get("knowledge_points", knowledge_point),
        "subject": result.get("subject", subject),
    }


KNOWLEDGE_SUMMARY_SYSTEM_PROMPT = """你是一个严谨的考研复习总结助手。你的任务是根据提供的 source references（来源引用）生成复习总结。

核心规则：
1. 每个事实性结论必须绑定 source_refs，标明出处。
2. 如果内容是你基于已有信息的推理，必须标注为 ai_inference。
3. 如果来源不足，不得编造事实，应返回 insufficient_context。
4. 不得编造不存在的 source_id、slug、URL 或 excerpt。
5. 输出必须是严格合法 JSON，不要输出其他内容。

输出格式：
{
  "title": "总结标题",
  "blocks": [
    {
      "type": "source_backed_claim",
      "text": "事实性结论文本",
      "source_refs": [{"source_type": "mistake", "source_id": "xxx", "field": "analysis"}]
    },
    {
      "type": "ai_inference",
      "text": "推理或建议文本",
      "source_refs": []
    }
  ]
}

如果 sources 不足，返回：
{
  "status": "insufficient_context",
  "message": "No usable source references are available for factual generation.",
  "outline": []
}"""


@router.post("/knowledge-summary", response_model=KnowledgeSummaryResponse | InsufficientContextResponse)
async def knowledge_summary(
    request_body: KnowledgeSummaryRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_knowledge_summary", after={"source_count": len(request_body.context_pack.sources)},
    )

    sources = request_body.context_pack.sources
    if not sources or len(sources) == 0:
        return InsufficientContextResponse(
            status="insufficient_context",
            message="No usable source references are available for factual generation.",
            outline=[],
        )

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

    user_content = (
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

    messages = [
        {"role": "system", "content": KNOWLEDGE_SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        result = await call_text_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    if result.get("status") == "insufficient_context":
        return InsufficientContextResponse(
            status="insufficient_context",
            message=result.get("message", "No usable source references are available for factual generation."),
            outline=result.get("outline", []),
        )

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

    return KnowledgeSummaryResponse(
        title=result.get("title", ""),
        blocks=blocks,
    )


PROMPT_TEMPLATES = {
    "mistake": {
        "ocr": {
            "name": "错题 OCR 识别",
            "description": "从图片中提取题目信息，必要时解题",
            "prompt": OCR_SYSTEM_PROMPT[:500] + "...",
            "route": "OCR/vision",
            "full_prompt": OCR_SYSTEM_PROMPT,
        },
        "text_analysis": {
            "name": "错题文本分析",
            "description": "分析文本题目，给出答案和解析",
            "prompt": TEXT_SYSTEM_PROMPT[:500] + "...",
            "route": "text JSON",
            "full_prompt": TEXT_SYSTEM_PROMPT,
        },
        "variant": {
            "name": "变式题生成",
            "description": "根据知识点生成变式练习题",
            "prompt": VARIANT_SYSTEM_PROMPT,
            "route": "text JSON",
        },
        "knowledge_card": {
            "name": "知识卡片生成",
            "description": "生成结构化知识卡片",
            "prompt": KNOWLEDGE_CARD_SYSTEM_PROMPT,
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
            "prompt": KNOWLEDGE_SUMMARY_SYSTEM_PROMPT[:500] + "...",
            "route": "text JSON",
            "full_prompt": KNOWLEDGE_SUMMARY_SYSTEM_PROMPT,
        },
    },
}


@router.get("/prompts")
async def get_prompts(
    _admin=Depends(get_current_admin),
):
    result = {}
    for group, templates in PROMPT_TEMPLATES.items():
        result[group] = {}
        for key, tmpl in templates.items():
            result[group][key] = {
                "name": tmpl["name"],
                "description": tmpl["description"],
                "prompt": tmpl["prompt"],
                "route": tmpl["route"],
            }
    return result


@router.post("/prompt-test")
async def prompt_test(
    req: dict,
    _admin=Depends(get_current_admin),
):
    prompt_key = req.get("prompt_key", "")
    sample_input = req.get("sample_input", "")
    custom_prompt = req.get("custom_prompt", "")
    route = req.get("route", "text JSON")

    if not sample_input:
        raise HTTPException(status_code=400, detail="sample_input is required")

    system_prompt = custom_prompt
    if not system_prompt and prompt_key:
        group, _, key = prompt_key.partition(".")
        tmpl = PROMPT_TEMPLATES.get(group, {}).get(key, {})
        system_prompt = tmpl.get("full_prompt") or tmpl.get("prompt", "")
    if not system_prompt:
        raise HTTPException(status_code=400, detail="No prompt found")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": sample_input},
    ]

    import time as _time
    start = _time.monotonic()
    attempts = []

    try:
        from app.services.ai_service import _call_with_fallback
        caps = {"text", "json"} if "json" in route.lower() else {"text"}
        preferred = "deepseek" if "text" in route.lower() else "dashscope_vision"
        result = await _call_with_fallback(
            required_caps=caps,
            messages=messages,
            max_tokens=2000,
            response_format={"type": "json_object"} if "json" in route.lower() else None,
            preferred=preferred,
            parse_json="json" in route.lower(),
        )
        latency = int((_time.monotonic() - start) * 1000)
        return {
            "success": True,
            "provider_used": result.provider_used,
            "fallback_used": result.fallback_used,
            "latency_ms": latency,
            "output": result.data if isinstance(result.data, str) else result.data,
            "attempts": [
                {"provider": a.provider, "model": a.model, "success": a.success, "latency_ms": a.latency_ms, "error": a.error}
                for a in result.attempts
            ],
        }
    except Exception as e:
        latency = int((_time.monotonic() - start) * 1000)
        return {
            "success": False,
            "provider_used": "",
            "fallback_used": False,
            "latency_ms": latency,
            "output": None,
            "error": str(e)[:300],
            "attempts": [],
        }


@router.get("/provider-status")
async def provider_status(
    _admin=Depends(get_current_admin),
):
    from app.services.ai_service import get_provider_status
    return await get_provider_status()


# --- Staged mistake workflow endpoints ---


@router.post("/mistake/question-draft", response_model=QuestionDraftResponse)
async def mistake_question_draft(
    req: QuestionDraftRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    if not req.images and not req.text.strip():
        raise HTTPException(status_code=400, detail="At least one image or text is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_question_draft", after={"image_count": len(req.images), "has_text": bool(req.text.strip())},
    )

    try:
        from app.services.mistake_staged_service import generate_question_draft
        result = await generate_question_draft(
            images=[img.model_dump() for img in req.images],
            text=req.text,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return QuestionDraftResponse(**result)


@router.post("/mistake/question-draft/confirm", response_model=QuestionDraftConfirmResponse)
async def mistake_question_draft_confirm(
    req: QuestionDraftConfirmRequest,
    _admin=Depends(get_current_admin),
):
    now = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    return QuestionDraftConfirmResponse(
        status="confirmed",
        draft=req.draft,
        confirmed_at=now,
    )


@router.post("/mistake/error-interpretation", response_model=ErrorInterpretationResponse)
async def mistake_error_interpretation(
    req: ErrorInterpretationRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    if not req.user_error_reason.strip():
        raise HTTPException(status_code=400, detail="user_error_reason is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_error_interpretation", after={"reason_length": len(req.user_error_reason)},
    )

    try:
        from app.services.mistake_staged_service import generate_error_interpretation
        result = await generate_error_interpretation(
            question_draft=req.question_draft.model_dump(),
            user_error_reason=req.user_error_reason,
            rejection_history=req.rejection_history,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ErrorInterpretationResponse(**result)


@router.post("/mistake/error-interpretation/reject", response_model=ErrorInterpretationResponse)
async def mistake_error_interpretation_reject(
    req: InterpretationRejectionRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()
    if not req.rejection_reason.strip():
        raise HTTPException(status_code=400, detail="rejection_reason is required")

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_interpretation_reject", after={"rejection_reason": req.rejection_reason[:100]},
    )

    updated_history = list(req.rejection_history) + [req.rejection_reason]

    try:
        from app.services.mistake_staged_service import generate_error_interpretation
        result = await generate_error_interpretation(
            question_draft=req.question_draft.model_dump(),
            user_error_reason=req.user_error_reason,
            rejection_history=updated_history,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return ErrorInterpretationResponse(**result)


@router.post("/mistake/final-analysis", response_model=FinalAnalysisResponse)
async def mistake_final_analysis(
    req: FinalAnalysisRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_final_analysis",
        after={"interpretation_id": req.accepted_interpretation.interpretation_id},
    )

    try:
        from app.services.mistake_staged_service import generate_final_analysis
        result = await generate_final_analysis(
            question_draft=req.question_draft.model_dump(),
            user_error_reason=req.user_error_reason,
            accepted_interpretation=req.accepted_interpretation.model_dump(),
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return FinalAnalysisResponse(**result)


@router.post("/mistake/diagram", response_model=DiagramResponse)
async def mistake_diagram(
    req: DiagramStrategyRequest,
    request: Request,
    _admin=Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(None, alias="admin_session"),
):
    _check_rate_limit()

    from app.services.audit_service import audit_action
    await audit_action(
        db, action="ai_call", session_token=session_token, request=request,
        entity_type="ai_mistake_diagram",
        after={"interpretation_id": req.accepted_interpretation.interpretation_id},
    )

    from app.services.diagram_service import classify_diagram_strategy, generate_structured_diagram

    strategy, reason = classify_diagram_strategy(req.question_draft.model_dump())

    if strategy == "structured":
        structured_data = await generate_structured_diagram(
            question_draft=req.question_draft.model_dump(),
            accepted_interpretation=req.accepted_interpretation.model_dump(),
            final_analysis=req.final_analysis.model_dump(),
        )
        return DiagramResponse(
            strategy="structured",
            strategy_reason=reason,
            structured_data=structured_data,
            accepted_interpretation_id=req.accepted_interpretation.interpretation_id,
            accepted_interpretation_version=req.accepted_interpretation.version,
            uses_error_interpretation=True,
        )

    from app.services.diagram_service import generate_qwen_image_fallback
    image_url, image_prompt = await generate_qwen_image_fallback(
        question_draft=req.question_draft.model_dump(),
        accepted_interpretation=req.accepted_interpretation.model_dump(),
        final_analysis=req.final_analysis.model_dump(),
    )
    return DiagramResponse(
        strategy="qwen_image_fallback",
        strategy_reason=reason,
        image_url=image_url,
        image_prompt=image_prompt,
        accepted_interpretation_id=req.accepted_interpretation.interpretation_id,
        accepted_interpretation_version=req.accepted_interpretation.version,
        uses_error_interpretation=True,
    )
