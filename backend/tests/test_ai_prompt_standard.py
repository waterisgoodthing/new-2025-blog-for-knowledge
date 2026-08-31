"""Behavior tests for the Batch 10.2 prompt standard checker."""

from dataclasses import replace

from app.services.ai_prompt_registry import PROMPT_REGISTRY, PromptTemplate
from app.services.ai_prompt_standard import validate_prompt_registry
from app.services.ai_task_types import AiTaskType


def _template(**overrides) -> PromptTemplate:
    template = PromptTemplate(
        task_type=AiTaskType.CAPTURE_DRAFT,
        version="v1",
        system_prompt=(
            "[Role]\nassistant\n[Task]\nextract\n[Input]\nuser content\n"
            "[Constraints]\ndo not invent\n[Output Contract]\nReturn JSON.\n"
            "[Failure / Uncertainty]\nreport missing input"
        ),
        output_schema_name="MistakeDraftSuggestionV1",
        json_mode=True,
        preferred_provider="deepseek",
        max_tokens=8000,
        description="draft",
    )
    return replace(template, **overrides)


def test_valid_prompt_registry_has_no_violations():
    assert validate_prompt_registry({AiTaskType.CAPTURE_DRAFT: _template()}) == []


def test_prompt_violations_are_stable_and_sorted():
    invalid = _template(version="1", system_prompt="")

    violations = validate_prompt_registry({AiTaskType.CAPTURE_DRAFT: invalid})

    assert [(item.task_type.value, item.code) for item in violations] == [
        ("capture_draft", "dynamic_prompt_mismatch"),
        ("capture_draft", "empty_prompt"),
        ("capture_draft", "invalid_version"),
        ("capture_draft", "json_contract_mismatch"),
        ("capture_draft", "missing_structure_section"),
    ]


def test_production_registry_conforms_to_prompt_standard():
    assert validate_prompt_registry(PROMPT_REGISTRY) == []


def test_static_prompt_versions_advance_when_standardized():
    for task_type, template in PROMPT_REGISTRY.items():
        expected = "v1" if template.dynamic_prompt else "v2"
        assert template.version == expected, task_type.value


def test_schema_name_must_match_existing_validator_contract():
    invalid = _template(output_schema_name="NotTheRegisteredSchema")

    violations = validate_prompt_registry({AiTaskType.CAPTURE_DRAFT: invalid})

    assert [item.code for item in violations] == ["schema_contract_mismatch"]


def test_detects_undeclared_input_variable():
    sensitive_value = "top-secret-user-input"
    invalid = _template(
        user_content_template="Question: {undeclared_question}",
        input_variables=(),
    )

    violations = validate_prompt_registry({AiTaskType.CAPTURE_DRAFT: invalid})

    assert [item.code for item in violations] == ["undeclared_input_variable"]
    assert sensitive_value not in " ".join(item.message for item in violations)


def test_detects_missing_input_variable():
    sensitive_value = "private-variable-value"
    invalid = _template(
        user_content_template="Static question text",
        input_variables=("required_question",),
    )

    violations = validate_prompt_registry({AiTaskType.CAPTURE_DRAFT: invalid})

    assert [item.code for item in violations] == ["missing_input_variable"]
    assert sensitive_value not in " ".join(item.message for item in violations)
