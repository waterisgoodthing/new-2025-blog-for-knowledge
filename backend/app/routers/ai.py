import json
import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.note import Note
from app.routers.auth import get_current_admin
from app.schemas.ai import AnalyzeRequest, AnalyzeResponse, DiagramItem, TextAnalyzeRequest
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

def _check_rate_limit(key: str = "global") -> None:
    now = time.time()
    timestamps = _rate_limit_store[key]
    _rate_limit_store[key] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[key]) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Max {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s.")
    _rate_limit_store[key].append(now)

OCR_SYSTEM_PROMPT = r"""你是一个严谨的错题图片识别助手，负责从用户上传的错题图片中提取题目信息，并输出结构化 JSON。

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
  "variant_questions": ["变式题1", "变式题2"],
  "diagrams": [{"type": "flowchart", "title": "图示标题", "mermaid": "graph TD; A-->B"}]
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
    _VALID_DIAGRAM_TYPES = {"flowchart", "timeline", "formula_breakdown", "network_topology", "geometry", "state_machine"}
    raw_diagrams = result.get("diagrams", [])
    diagrams = []
    for d in raw_diagrams:
        if isinstance(d, dict) and d.get("mermaid"):
            dtype = d.get("type", "flowchart")
            if dtype not in _VALID_DIAGRAM_TYPES:
                dtype = "flowchart"
            diagrams.append(DiagramItem(
                type=dtype,
                title=d.get("title", ""),
                mermaid=d["mermaid"],
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


@router.post("/analyze-stream")
async def analyze_mistake_stream(req: AnalyzeRequest, _admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    _check_rate_limit()

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

            messages = [
                {"role": "system", "content": "你是一个严谨的错题图片识别助手。请始终以 JSON 格式回复。"},
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

            yield f"data: {json.dumps({'type': 'progress', 'step': 'parsing_model_output', 'label': '正在解析AI分析结果...'})}\n\n"
            await asyncio.sleep(0)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'finding_related_notes', 'label': '正在查找相关笔记...'})}\n\n"
            await asyncio.sleep(0)

            related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
            await asyncio.sleep(0)

            parsed = _parse_result(result, related)
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
async def analyze_text_stream(req: TextAnalyzeRequest, _admin=Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    _check_rate_limit()

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

            messages = [
                {"role": "system", "content": TEXT_SYSTEM_PROMPT},
                {"role": "user", "content": req.text},
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

            yield f"data: {json.dumps({'type': 'progress', 'step': 'parsing_model_output', 'label': '正在解析AI分析结果...'})}\n\n"
            await asyncio.sleep(0)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'finding_related_notes', 'label': '正在查找相关笔记...'})}\n\n"
            await asyncio.sleep(0)

            related = await _find_related_notes(db, result.get("subject"), result.get("knowledge_points"))
            await asyncio.sleep(0)

            parsed = _parse_result(result, related)
            yield f"data: {json.dumps({'type': 'result', 'data': parsed.model_dump()})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'label': '分析完成'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    })


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
    request: KnowledgeSummaryRequest,
    _admin=Depends(get_current_admin),
):
    _check_rate_limit()

    sources = request.context_pack.sources
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
    if request.context_pack.related_notes:
        related_notes_ctx = "\n相关笔记:\n" + "\n".join(
            f"- {n.title} (subject: {n.subject}, slug: {n.slug})"
            for n in request.context_pack.related_notes[:5]
        )

    related_mistakes_ctx = ""
    if request.context_pack.related_mistakes:
        related_mistakes_ctx = "\n相关错题:\n" + "\n".join(
            f"- {m.title} (subject: {m.subject}, difficulty: {m.difficulty})"
            for m in request.context_pack.related_mistakes[:5]
        )

    stats_ctx = ""
    if request.context_pack.stats:
        stats = request.context_pack.stats
        stats_ctx = f"\n统计: 错题数={stats.mistake_count}, 笔记数={stats.note_count}"
        if stats.top_error_reasons:
            stats_ctx += f", 高频错误原因: {'、'.join(stats.top_error_reasons)}"

    user_content = (
        f"Mode: {request.mode}\n"
        f"Language: {request.requirements.get('language', 'zh-CN')}\n"
        f"Style: {request.requirements.get('style', 'exam_review')}\n"
        f"Max length: {request.requirements.get('max_length', 1200)}\n"
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
