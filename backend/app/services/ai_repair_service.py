"""AI 结果修复服务 — LaTeX 修复 + 确定性校对。

从 ai.py 抽离的纯业务逻辑，不含路由/HTTP 层代码。
"""

import json
import re
from collections.abc import Awaitable, Callable

from app.services.ai_prompt_registry import build_text_messages
from app.services.ai_task_types import AiTaskType


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

    dynamic_prompt = (
        "你是错题分析结果的确定性校对器。你会收到上一轮 AI 输出的 JSON。"
        "请只返回修正后的完整 JSON，不要添加解释文字。"
        "必须修复以下问题："
        "1. correct_answer、analysis、error_reason、key_step 中不得使用“可能”“也许”“似乎”“大概”“推测”等模糊词来形成最终结论；"
        "2. correct_answer 必须与 analysis 的推导结论一致；"
        "3. 如果题目信息足够，必须给出唯一确定结论；"
        "4. 如果题目信息不足，correct_answer 留空，analysis 明确写“信息不足”并列出缺失条件；"
        "5. 不要讨论教材预期、其他理解、也不要保留互相矛盾的答案。"
    )
    repair_messages = build_text_messages(
        AiTaskType.REPAIR_DETERMINISTIC,
        json.dumps(result, ensure_ascii=False),
        system_prompt_override=dynamic_prompt,
    )

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
