import json
import os

from app.services.ai_service import call_text_model, call_text_model_no_json


STRUCTURED_TYPES = {
    "network_topology",
    "ip_fragmentation",
    "algorithm",
    "math",
}

STRUCTURED_KEYWORDS = {
    "ospf", "dijkstra", "路由", "拓扑", "network", "router",
    "分片", "fragment", "ip", "子网", "subnet",
    "树", "tree", "graph", "图", "链表", "linked",
    "排序", "sort", "搜索", "search", "动态规划", "dp",
    "流程", "flowchart", "状态机", "state",
}


def classify_diagram_strategy(question_draft: dict) -> tuple[str, str]:
    """T3-01: Classify whether a question should use structured or fallback rendering.

    Returns (strategy, reason) where strategy is 'structured' or 'qwen_image_fallback'.
    """
    qtype = question_draft.get("question_type", "").lower()
    question_text = question_draft.get("question", "").lower()
    visual = question_draft.get("visual_context", "").lower()
    tags = [t.lower() for t in question_draft.get("tags", [])]
    combined = f"{question_text} {visual} {' '.join(tags)}"

    if qtype in STRUCTURED_TYPES:
        return "structured", f"question_type '{qtype}' is a structured type"

    for kw in STRUCTURED_KEYWORDS:
        if kw in combined:
            return "structured", f"keyword '{kw}' detected in question content"

    return "qwen_image_fallback", "no structured renderer matched this question type"


DIAGRAM_STRUCTURED_SYSTEM_PROMPT = r"""你是一个教学图解生成器。根据题目信息和已采纳的错因理解，生成结构化的图解数据。

输出严格合法 JSON，格式如下：

{
  "diagram_type": "graph|table|flowchart|packet_slices",
  "title": "图解标题",
  "nodes": [
    {"id": "A", "label": "节点A", "x": 0, "y": 0, "highlighted": false, "annotation": ""}
  ],
  "edges": [
    {"source": "A", "target": "B", "label": "边标签", "highlighted": false, "weight": ""}
  ],
  "table": null,
  "mermaid": "",
  "caption": "图解说明",
  "error_reason_annotation": "结合学生错因的标注说明"
}

规则：
- 网络拓扑题：用 graph 类型，节点=路由器/设备，边=链路(标注cost)
- IP分片题：用 table 或 packet_slices 类型，展示分片偏移/长度/MF
- 算法/流程题：用 flowchart 类型
- 数学计算题：用 table 类型展示推导步骤
- highlighted=true 标注正确路径或关键位置
- error_reason_annotation 说明学生错在哪里
- 不要生成原始 SVG 或 HTML
- 如果可以用 Mermaid 表达，填入 mermaid 字段

输出必须是严格合法 JSON。"""


async def generate_structured_diagram(
    question_draft: dict,
    accepted_interpretation: dict,
    final_analysis: dict,
) -> dict:
    """T3-02/T3-03: Generate structured diagram data for a question.

    Returns a dict matching StructuredDiagramData schema.
    """
    user_content = f"""题目信息：
{json.dumps(question_draft, ensure_ascii=False, indent=2)}

已采纳的错因理解：
{json.dumps(accepted_interpretation, ensure_ascii=False, indent=2)}

最终分析要点：
key_step: {final_analysis.get('key_step', '')}
error_reason: {final_analysis.get('error_reason', '')}"""

    messages = [
        {"role": "system", "content": DIAGRAM_STRUCTURED_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = await call_text_model(messages)

    diagram_type = result.get("diagram_type", "graph")
    if diagram_type not in ("graph", "table", "flowchart", "packet_slices"):
        diagram_type = "graph"

    nodes = []
    for n in result.get("nodes", []):
        if isinstance(n, dict):
            nodes.append({
                "id": str(n.get("id", "")),
                "label": str(n.get("label", "")),
                "x": float(n.get("x", 0)),
                "y": float(n.get("y", 0)),
                "highlighted": bool(n.get("highlighted", False)),
                "annotation": str(n.get("annotation", "")),
            })

    edges = []
    for e in result.get("edges", []):
        if isinstance(e, dict):
            edges.append({
                "source": str(e.get("source", "")),
                "target": str(e.get("target", "")),
                "label": str(e.get("label", "")),
                "highlighted": bool(e.get("highlighted", False)),
                "weight": str(e.get("weight", "")),
            })

    table_data = None
    raw_table = result.get("table")
    if isinstance(raw_table, dict):
        headers = raw_table.get("headers", [])
        rows = []
        for row in raw_table.get("rows", []):
            if isinstance(row, dict):
                rows.append({"cells": [str(c) for c in row.get("cells", [])]})
            elif isinstance(row, list):
                rows.append({"cells": [str(c) for c in row]})
        table_data = {"headers": headers, "rows": rows, "caption": raw_table.get("caption", "")}

    mermaid = result.get("mermaid", "")
    if isinstance(mermaid, str) and len(mermaid.strip()) < 5:
        mermaid = ""

    return {
        "diagram_type": diagram_type,
        "title": result.get("title", ""),
        "nodes": nodes,
        "edges": edges,
        "table": table_data,
        "mermaid": mermaid,
        "caption": result.get("caption", ""),
        "error_reason_annotation": result.get("error_reason_annotation", ""),
    }


QWEN_IMAGE_FALLBACK_PROMPT = r"""你是一个教学图解 prompt 编写器。请为以下题目编写一个适合图片生成模型的英文 prompt。

要求：
- 生成教学图解，不是装饰性图片
- 必须体现学生的错误原因
- 使用简洁的英文描述
- 输出格式：直接输出 prompt 文本，不要 JSON"""

QWEN_IMAGE_CONFIGURED = bool(os.environ.get("DASHSCOPE_IMAGE_API_KEY"))
QWEN_IMAGE_MODEL = os.environ.get("DASHSCOPE_IMAGE_MODEL", "qwen-image-2.0-pro")
QWEN_IMAGE_BASE_URL = os.environ.get(
    "DASHSCOPE_IMAGE_BASE_URL",
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
)


async def generate_qwen_image_fallback(
    question_draft: dict,
    accepted_interpretation: dict,
    final_analysis: dict,
) -> tuple[str, str]:
    """T3-04: Generate diagram using Qwen image model as fallback.

    Returns (image_url, image_prompt).
    """
    user_content = f"""题目: {question_draft.get('title', '')}
题目类型: {question_draft.get('question_type', '')}
视觉上下文: {question_draft.get('visual_context', '')}
学生错因: {accepted_interpretation.get('summary', '')}
关键步骤: {final_analysis.get('key_step', '')}"""

    messages = [
        {"role": "system", "content": QWEN_IMAGE_FALLBACK_PROMPT},
        {"role": "user", "content": user_content},
    ]

    result = await call_text_model_no_json(messages)
    image_prompt = result.strip() if isinstance(result, str) else str(result)

    if not QWEN_IMAGE_CONFIGURED:
        return "", image_prompt

    import httpx

    api_key = os.environ.get("DASHSCOPE_IMAGE_API_KEY", "")
    if not api_key:
        return "", image_prompt

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                QWEN_IMAGE_BASE_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": QWEN_IMAGE_MODEL,
                    "input": {"prompt": image_prompt},
                    "parameters": {"n": 1, "size": "1024*1024"},
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("output", {}).get("results", [])
                if results:
                    return results[0].get("url", ""), image_prompt
            return "", image_prompt
    except Exception:
        return "", image_prompt
