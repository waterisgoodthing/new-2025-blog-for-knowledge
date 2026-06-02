import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note
from app.routers.auth import get_current_admin
from app.schemas.ai import AnalyzeRequest, AnalyzeResponse, TextAnalyzeRequest
from app.services.ai_service import call_ocr_model, call_text_model

router = APIRouter(prefix="/api/ai", tags=["ai"])

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 10
RATE_LIMIT_WINDOW = 60

def _check_rate_limit(key: str = "global") -> None:
    now = time.time()
    timestamps = _rate_limit_store[key]
    _rate_limit_store[key] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s.")
    _rate_limit_store[key].append(now)

OCR_SYSTEM_PROMPT = """你是一个严谨的错题图片识别助手，负责从用户上传的错题图片中提取题目信息，并输出结构化 JSON。

你的核心任务是：

1. 尽可能准确识别图片中的文字、公式、选项、图表信息。
2. 判断题目所属学科、题型、难度和知识点。
3. 提取题目原文，保持题干、条件、选项、公式的完整性。
4. 如果图片中已经包含答案或解析，需要一并提取。
5. 如果图片中没有答案或解析，不要编造答案，只根据可见内容填写。
6. 如果识别出题目属于算法、数据结构或编程题，需要在 tags 和 knowledge_points 中体现，但不要强行生成完整代码。完整代码由解题 AI 负责。

请严格遵守以下规则：

* 只根据图片中可见内容进行识别。
* 不要臆造图片中不存在的信息。
* 数学公式尽量使用 LaTeX 表示。
* 选择题需要保留所有选项。
* 多小问题目需要保留小问编号。
* 如果图片模糊、遮挡或无法完整识别，需要在 analysis 中说明识别不确定的位置。
* 输出必须是合法 JSON。
* 不要输出 Markdown。
* 不要使用 ```json 代码块。
* 不要在 JSON 前后添加任何解释性文字。

请按照以下 JSON 格式返回：

{
  "title": "题目标题，若图片中没有明确标题，则根据题目内容概括一个简短标题",
  "question": "完整题目内容，包括题干、条件、选项、公式、图表文字信息等",
  "correct_answer": "图片中可见的答案；如果图片中没有答案，填写空字符串",
  "analysis": "图片中可见的解析；如果图片中没有解析，填写识别说明或空字符串；如果存在识别不确定内容，需要在这里说明",
  "knowledge_points": "题目涉及的知识点，多个知识点用中文逗号分隔",
  "subject": "学科名称，例如：数学、英语、计算机、数据结构、算法、物理、化学、政治、未知",
  "difficulty": "easy|medium|hard",
  "tags": ["标签1", "标签2"],
  "error_reason": "如果图片中能看出错误原因则填写；否则填写空字符串",
  "key_step": "本题最关键的解题步骤或判断点；无法判断时填写空字符串",
  "similar_traps": ["相似易错点1", "相似易错点2"],
  "generalization": "这类题可迁移的一般方法；无法判断时填写空字符串",
  "review_advice": "复习建议；无法判断时填写空字符串",
  "variant_questions": ["变式题1", "变式题2"]
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
   * 只填写图片中已经出现的答案。
   * 图片中没有答案时，填写空字符串。
   * 不要主动求解。

4. analysis
   * 只填写图片中可见的解析。
   * 图片中没有解析时，可以填写空字符串。
   * 如果 OCR 不确定，需要写明，例如："部分公式识别不确定：第 2 行分母可能为 x+1。"

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

再次强调：

你只负责识别与结构化提取，不负责完整解题。
输出必须是严格合法 JSON。"""

TEXT_SYSTEM_PROMPT = """你是一个严谨的学习解题助手，负责根据用户提供的题目文本进行完整分析，并输出结构化 JSON。

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
  "variant_questions": ["变式题1", "变式题2"]
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
不要输出 JSON 以外的任何内容。"""


def _list_of_strings(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        normalized = value.replace("，", ",").replace("、", ",").replace("\n", ",")
        return [item.strip() for item in normalized.split(",") if item.strip()]
    return [str(value)]


def _parse_result(result: dict, related_notes: list[dict] | None = None) -> AnalyzeResponse:
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
async def analyze_mistake(req: AnalyzeRequest, _admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    _check_rate_limit()
    if not req.images:
        raise HTTPException(status_code=400, detail="At least one image is required")

    content = [{"type": "text", "text": OCR_SYSTEM_PROMPT}]

    for img in req.images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{img.mime_type};base64,{img.base64}"},
            }
        )

    messages = [
        {"role": "system", "content": "你是一个严谨的错题图片识别助手。请始终以 JSON 格式回复。"},
        {"role": "user", "content": content},
    ]

    try:
        result = await call_ocr_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
    return _parse_result(result, related)


@router.post("/analyze-text", response_model=AnalyzeResponse)
async def analyze_text(req: TextAnalyzeRequest, _admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    _check_rate_limit()
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    messages = [
        {"role": "system", "content": TEXT_SYSTEM_PROMPT},
        {"role": "user", "content": req.text},
    ]

    try:
        result = await call_text_model(messages)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
    return _parse_result(result, related)
