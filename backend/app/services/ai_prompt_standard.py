"""Deterministic static checks for Prompt Registry metadata."""

import re
from dataclasses import dataclass
from typing import Mapping

from app.services.ai_prompt_registry import PromptTemplate
from app.services.ai_task_types import AiTaskType
from app.services.ai_validator import SCHEMA_MAP


_VERSION_PATTERN = re.compile(r"^v[1-9][0-9]*$")
_REQUIRED_SECTIONS = (
    "[role]",
    "[task]",
    "[input]",
    "[constraints]",
    "[output contract]",
    "[failure / uncertainty]",
)

# Controlled output-contract exceptions. These tasks intentionally keep their
# existing manual parsers or plain-text pass-through behavior in Batch 10.2.
MANUAL_PARSE_TASKS = frozenset(
    {
        AiTaskType.ANALYZE_MISTAKE,
        AiTaskType.ANALYZE_TEXT,
        AiTaskType.KNOWLEDGE_SUMMARY,
        AiTaskType.REPAIR_DETERMINISTIC,
    }
)
PLAIN_TEXT_TASKS = frozenset(
    {
        AiTaskType.PROMPT_TEST,
        AiTaskType.DIAGRAM_FALLBACK,
        AiTaskType.NETEASE_REASON,
    }
)


@dataclass(frozen=True)
class PromptViolation:
    """One safe, deterministic Prompt contract violation."""

    task_type: AiTaskType
    code: str
    message: str


def _template_variables(template: str | None) -> set[str]:
    if not template:
        return set()
    return set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", template))


def validate_prompt_registry(
    registry: Mapping[AiTaskType, PromptTemplate],
) -> list[PromptViolation]:
    """Return stable violations without inspecting or executing user input."""

    violations: list[PromptViolation] = []
    for task_type, template in registry.items():
        dynamic_prompt = bool(getattr(template, "dynamic_prompt", False))
        prompt_text = "\n".join(
            part
            for part in (
                template.system_prompt,
                getattr(template, "vision_system_prompt", None),
                template.user_content_template,
            )
            if part
        )
        lowered = prompt_text.lower()

        if not prompt_text and not dynamic_prompt:
            violations.append(
                PromptViolation(task_type, "empty_prompt", "Prompt text is empty")
            )
        if not _VERSION_PATTERN.fullmatch(template.version):
            violations.append(
                PromptViolation(task_type, "invalid_version", "Version must match v<number>")
            )
        if not dynamic_prompt and any(
            section not in lowered for section in _REQUIRED_SECTIONS
        ):
            violations.append(
                PromptViolation(
                    task_type,
                    "missing_structure_section",
                    "Prompt is missing one or more required structure sections",
                )
            )

        declared = set(getattr(template, "input_variables", ()))
        discovered = _template_variables(template.user_content_template)
        if discovered - declared:
            violations.append(
                PromptViolation(
                    task_type,
                    "undeclared_input_variable",
                    "Template contains variables absent from its declared contract",
                )
            )
        if declared - discovered:
            violations.append(
                PromptViolation(
                    task_type,
                    "missing_input_variable",
                    "Declared variables are absent from the template",
                )
            )
        if template.json_mode and not dynamic_prompt and "json" not in lowered:
            violations.append(
                PromptViolation(
                    task_type,
                    "json_contract_mismatch",
                    "JSON mode requires an explicit JSON output contract",
                )
            )
        expected_schema = SCHEMA_MAP.get(task_type)
        expected_schema_name = expected_schema.__name__ if expected_schema else None
        output_contract_is_classified = (
            expected_schema is not None
            or task_type in MANUAL_PARSE_TASKS
            or task_type in PLAIN_TEXT_TASKS
        )
        schema_contract_mismatch = (
            (template.output_schema_name and not template.json_mode)
            or template.output_schema_name != expected_schema_name
            or not output_contract_is_classified
        )
        if schema_contract_mismatch:
            violations.append(
                PromptViolation(
                    task_type,
                    "schema_contract_mismatch",
                    "A structured output schema requires JSON mode",
                )
            )
        if dynamic_prompt != (not template.system_prompt):
            violations.append(
                PromptViolation(
                    task_type,
                    "dynamic_prompt_mismatch",
                    "Dynamic prompt metadata does not match the system prompt contract",
                )
            )

    return sorted(violations, key=lambda item: (item.task_type.value, item.code))
