"""ai_validator 测试 — Batch 10 P0-05。"""

import json

from app.services.ai_task_types import AiTaskType
from app.services.ai_validator import (
    SCHEMA_MAP,
    AiValidationResult,
    validate_ai_output,
)


class TestSchemaMap:
    def test_schema_map_covers_all_task_types(self):
        """SCHEMA_MAP 必须覆盖全部 16 个 AiTaskType。"""
        assert set(SCHEMA_MAP.keys()) == set(AiTaskType)

    def test_schema_map_has_9_schemas(self):
        """有 schema 的任务应为 9 个。"""
        with_schema = [k for k, v in SCHEMA_MAP.items() if v is not None]
        assert len(with_schema) == 9

    def test_schema_map_has_7_none(self):
        """无 schema 的任务应为 7 个。"""
        without_schema = [k for k, v in SCHEMA_MAP.items() if v is None]
        assert len(without_schema) == 7

    def test_expected_schema_assignments(self):
        """验证关键 task_type 的 schema 映射。"""
        from app.schemas.ai_output import (
            KnowledgeCardOutput,
            RecommendationOutput,
            RecognitionOutput,
            VariantOutput,
        )
        from app.schemas.capture import MistakeDraftSuggestionV1
        from app.schemas.ai import (
            ErrorInterpretationResponse,
            FinalAnalysisResponse,
            QuestionDraftResponse,
            StructuredDiagramData,
        )

        assert SCHEMA_MAP[AiTaskType.CAPTURE_DRAFT] is MistakeDraftSuggestionV1
        assert SCHEMA_MAP[AiTaskType.CAPTURE_RECOGNITION] is RecognitionOutput
        assert SCHEMA_MAP[AiTaskType.MISTAKE_QUESTION_DRAFT] is QuestionDraftResponse
        assert SCHEMA_MAP[AiTaskType.MISTAKE_ERROR_INTERPRETATION] is ErrorInterpretationResponse
        assert SCHEMA_MAP[AiTaskType.MISTAKE_FINAL_ANALYSIS] is FinalAnalysisResponse
        assert SCHEMA_MAP[AiTaskType.DIAGRAM_STRUCTURED] is StructuredDiagramData
        assert SCHEMA_MAP[AiTaskType.GENERATE_VARIANT] is VariantOutput
        assert SCHEMA_MAP[AiTaskType.GENERATE_KNOWLEDGE_CARD] is KnowledgeCardOutput
        assert SCHEMA_MAP[AiTaskType.RECOMMENDATION] is RecommendationOutput


class TestValidateWithSchema:
    def test_recognition_success(self):
        """有 schema 任务校验成功路径。"""
        result = validate_ai_output(
            AiTaskType.CAPTURE_RECOGNITION,
            {"text": "图片中的文字"},
        )
        assert result.success is True
        assert result.data == {"text": "图片中的文字"}
        assert result.error_code is None

    def test_recognition_missing_field(self):
        """有 schema 任务缺少必填字段 → schema_error。"""
        result = validate_ai_output(
            AiTaskType.CAPTURE_RECOGNITION,
            {"not_text": "oops"},
        )
        assert result.success is False
        assert result.error_code == "schema_error"
        assert result.error_message_safe is not None

    def test_capture_draft_success(self):
        result = validate_ai_output(
            AiTaskType.CAPTURE_DRAFT,
            {
                "question_text": "题目",
                "analysis_text": "解析",
                "error_summary": "错因",
            },
        )
        assert result.success is True

    def test_question_draft_success(self):
        result = validate_ai_output(
            AiTaskType.MISTAKE_QUESTION_DRAFT,
            {"title": "标题", "question": "题目内容"},
        )
        assert result.success is True

    def test_structured_diagram_success(self):
        result = validate_ai_output(
            AiTaskType.DIAGRAM_STRUCTURED,
            {"diagram_type": "graph", "title": "拓扑图"},
        )
        assert result.success is True

    def test_structured_diagram_invalid_type(self):
        result = validate_ai_output(
            AiTaskType.DIAGRAM_STRUCTURED,
            {"diagram_type": "invalid_type"},
        )
        assert result.success is False
        assert result.error_code == "schema_error"

    def test_recommendation_all_defaults(self):
        """RecommendationOutput 所有字段有默认值，空 dict 应通过。"""
        result = validate_ai_output(
            AiTaskType.RECOMMENDATION,
            {},
        )
        assert result.success is True

    def test_variant_missing_required(self):
        result = validate_ai_output(
            AiTaskType.GENERATE_VARIANT,
            {"question": "q"},
        )
        assert result.success is False
        assert result.error_code == "schema_error"

    def test_json_string_input(self):
        """字符串 JSON 输入应先解析再校验。"""
        result = validate_ai_output(
            AiTaskType.CAPTURE_RECOGNITION,
            json.dumps({"text": "from string"}),
        )
        assert result.success is True
        assert result.data == {"text": "from string"}

    def test_invalid_json_string(self):
        """非法 JSON 字符串 → parse_error。"""
        result = validate_ai_output(
            AiTaskType.CAPTURE_RECOGNITION,
            "not a json",
        )
        assert result.success is False
        assert result.error_code == "parse_error"

    def test_none_input_with_schema(self):
        """有 schema 任务传入 None → empty_result。"""
        result = validate_ai_output(
            AiTaskType.CAPTURE_RECOGNITION,
            None,
        )
        assert result.success is False
        assert result.error_code == "empty_result"


class TestValidateWithoutSchema:
    def test_text_task_returns_raw_string(self):
        """无 schema 任务直接返回原始字符串。"""
        result = validate_ai_output(
            AiTaskType.DIAGRAM_FALLBACK,
            "some prompt text",
        )
        assert result.success is True
        assert result.data == "some prompt text"
        assert result.error_code is None

    def test_text_task_returns_raw_dict(self):
        """无 schema 任务传入 dict 也直接返回。"""
        result = validate_ai_output(
            AiTaskType.ANALYZE_MISTAKE,
            {"any": "thing"},
        )
        assert result.success is True
        assert result.data == {"any": "thing"}

    def test_text_task_returns_none(self):
        """无 schema 任务传入 None 也直接返回。"""
        result = validate_ai_output(
            AiTaskType.NETEASE_REASON,
            None,
        )
        assert result.success is True
        assert result.data is None


class TestNoExceptions:
    def test_validator_never_raises(self):
        """validate_ai_output 不抛异常，始终返回 AiValidationResult。"""
        for task_type in AiTaskType:
            for raw in [None, "", "bad json", {}, {"x": 1}, 123, [], True]:
                result = validate_ai_output(task_type, raw)
                assert isinstance(result, AiValidationResult)
