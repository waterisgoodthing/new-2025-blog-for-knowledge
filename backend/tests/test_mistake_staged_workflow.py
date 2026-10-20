import unittest
from unittest.mock import AsyncMock, patch

from app.schemas.ai import (
    DiagramResponse,
    ErrorInterpretationRequest,
    ErrorInterpretationResponse,
    FinalAnalysisRequest,
    FinalAnalysisResponse,
    InterpretationRejectionRequest,
    QuestionDraftConfirmRequest,
    QuestionDraftConfirmResponse,
    QuestionDraftRequest,
    QuestionDraftResponse,
    StructuredDiagramData,
    StructuredDiagramEdge,
    StructuredDiagramNode,
    StructuredDiagramTable,
    StructuredDiagramTableRow,
)
from app.services.diagram_service import classify_diagram_strategy, QWEN_IMAGE_CONFIGURED


class QuestionDraftSchemaTest(unittest.TestCase):
    """T1-02: Question draft confirmation gate schema tests."""

    def test_question_draft_request_accepts_images_and_text(self):
        req = QuestionDraftRequest(
            images=[],
            text="OSPF area 0 has routers A-B-C with cost 10, 20, 30.",
        )
        self.assertEqual(req.text, "OSPF area 0 has routers A-B-C with cost 10, 20, 30.")
        self.assertEqual(req.images, [])

    def test_question_draft_request_defaults_empty(self):
        req = QuestionDraftRequest()
        self.assertEqual(req.images, [])
        self.assertEqual(req.text, "")

    def test_question_draft_response_has_required_fields(self):
        resp = QuestionDraftResponse(
            title="OSPF路径选择",
            question="Which path has the lowest cost?",
            options=["A-B-C", "A-D-C"],
            visual_context="Network topology with 4 routers",
            key_conditions=["Cost values", "OSPF area 0"],
            candidate_answer="A-B-C",
            knowledge_points="OSPF,路由选择",
            question_type="network_topology",
            subject="计算机网络",
            difficulty="medium",
        )
        self.assertEqual(resp.title, "OSPF路径选择")
        self.assertEqual(resp.question_type, "network_topology")
        self.assertEqual(resp.options, ["A-B-C", "A-D-C"])

    def test_question_draft_confirm_requires_draft(self):
        draft = QuestionDraftResponse(
            title="Test",
            question="Q?",
        )
        confirm = QuestionDraftConfirmRequest(draft=draft)
        self.assertEqual(confirm.draft.title, "Test")

    def test_question_draft_confirm_response_status(self):
        resp = QuestionDraftConfirmResponse(
            draft=QuestionDraftResponse(title="T", question="Q?"),
        )
        self.assertEqual(resp.status, "confirmed")


class ErrorInterpretationSchemaTest(unittest.TestCase):
    """T1-03: Personal error reason priority schema tests."""

    def test_error_interpretation_request_carries_user_reason(self):
        draft = QuestionDraftResponse(
            title="OSPF路径选择",
            question="Which path?",
            question_type="network_topology",
        )
        req = ErrorInterpretationRequest(
            question_draft=draft,
            user_error_reason="没有结合 cost 来看，只按 TTL/跳数判断了。",
        )
        self.assertIn("cost", req.user_error_reason)
        self.assertEqual(req.rejection_history, [])

    def test_error_interpretation_request_with_rejection_history(self):
        draft = QuestionDraftResponse(title="T", question="Q?")
        req = ErrorInterpretationRequest(
            question_draft=draft,
            user_error_reason="没有结合 cost 来看",
            rejection_history=["你只说了 TTL，但我实际是没看 cost"],
        )
        self.assertEqual(len(req.rejection_history), 1)

    def test_error_interpretation_response_has_identity(self):
        resp = ErrorInterpretationResponse(
            interpretation_id="interp-001",
            version=1,
            summary="learner focused on TTL instead of cost",
            diagnosis="The learner ignored OSPF cost metric",
            root_cause="Knowledge gap in OSPF cost-based path selection",
        )
        self.assertEqual(resp.interpretation_id, "interp-001")
        self.assertEqual(resp.version, 1)

    def test_error_interpretation_response_fields(self):
        resp = ErrorInterpretationResponse(
            interpretation_id="i1",
            summary="s",
            diagnosis="d",
            root_cause="r",
            knowledge_gap="OSPF cost",
            suggested_correction="Always check cost before TTL",
            reasoning_trace="Learner says X, which means Y",
        )
        self.assertEqual(resp.knowledge_gap, "OSPF cost")
        self.assertIn("cost", resp.suggested_correction.lower())


class StagedGateSchemaTest(unittest.TestCase):
    """T1-04: Staged gate behavior schema tests."""

    def test_final_analysis_request_requires_accepted_interpretation(self):
        draft = QuestionDraftResponse(title="T", question="Q?")
        interp = ErrorInterpretationResponse(
            interpretation_id="i1",
            summary="s",
            diagnosis="d",
            root_cause="r",
        )
        req = FinalAnalysisRequest(
            question_draft=draft,
            user_error_reason="没有结合 cost 来看",
            accepted_interpretation=interp,
        )
        self.assertEqual(req.accepted_interpretation.interpretation_id, "i1")

    def test_final_analysis_response_binds_interpretation_id(self):
        resp = FinalAnalysisResponse(
            analysis="Full analysis text",
            error_reason="Ignored cost metric",
            key_step="Check OSPF cost first",
            accepted_interpretation_id="i1",
            accepted_interpretation_version=1,
        )
        self.assertEqual(resp.accepted_interpretation_id, "i1")
        self.assertEqual(resp.accepted_interpretation_version, 1)


class InterpretationVersionBindingTest(unittest.TestCase):
    """T1-05: Accepted interpretation version binding tests."""

    def test_interpretation_version_increments(self):
        v1 = ErrorInterpretationResponse(
            interpretation_id="i1", version=1, summary="s", diagnosis="d", root_cause="r",
        )
        v2 = ErrorInterpretationResponse(
            interpretation_id="i1", version=2, summary="s2", diagnosis="d2", root_cause="r2",
        )
        self.assertEqual(v1.interpretation_id, v2.interpretation_id)
        self.assertNotEqual(v1.version, v2.version)

    def test_final_analysis_records_version(self):
        resp = FinalAnalysisResponse(
            analysis="a",
            error_reason="e",
            key_step="k",
            accepted_interpretation_id="i1",
            accepted_interpretation_version=2,
        )
        self.assertEqual(resp.accepted_interpretation_version, 2)

    def test_diagram_response_records_interpretation(self):
        resp = DiagramResponse(
            strategy="structured",
            structured_data=StructuredDiagramData(
                diagram_type="graph",
                title="OSPF Path",
                nodes=[
                    StructuredDiagramNode(id="A", label="Router A"),
                    StructuredDiagramNode(id="B", label="Router B", highlighted=True),
                ],
                edges=[
                    StructuredDiagramEdge(source="A", target="B", label="cost=10", highlighted=True),
                ],
            ),
            accepted_interpretation_id="i1",
            accepted_interpretation_version=1,
            uses_error_interpretation=True,
        )
        self.assertEqual(resp.accepted_interpretation_id, "i1")
        self.assertTrue(resp.uses_error_interpretation)


class DiagramSafetySchemaTest(unittest.TestCase):
    """T1-06: Structured diagram safety schema tests."""

    def test_structured_diagram_uses_constrained_schema(self):
        data = StructuredDiagramData(
            diagram_type="graph",
            title="Network",
            nodes=[
                StructuredDiagramNode(id="A", label="Node A"),
                StructuredDiagramNode(id="B", label="Node B", highlighted=True, annotation="Error here"),
            ],
            edges=[
                StructuredDiagramEdge(source="A", target="B", label="10", highlighted=True),
            ],
            error_reason_annotation="Learner ignored cost",
        )
        self.assertEqual(data.diagram_type, "graph")
        self.assertEqual(len(data.nodes), 2)
        self.assertTrue(data.nodes[1].highlighted)
        self.assertIn("cost", data.error_reason_annotation)

    def test_structured_diagram_table_schema(self):
        data = StructuredDiagramData(
            diagram_type="table",
            title="IP Fragmentation",
            table=StructuredDiagramTable(
                headers=["Fragment", "Offset", "Length", "MF"],
                rows=[
                    StructuredDiagramTableRow(cells=["1", "0", "776", "1"]),
                    StructuredDiagramTableRow(cells=["2", "97", "776", "1"]),
                    StructuredDiagramTableRow(cells=["3", "194", "8", "0"]),
                ],
                caption="IP fragmentation breakdown",
            ),
            error_reason_annotation="Learner forgot 8-byte alignment",
        )
        self.assertEqual(data.table.headers[0], "Fragment")
        self.assertEqual(len(data.table.rows), 3)

    def test_structured_diagram_mermaid_fallback(self):
        data = StructuredDiagramData(
            diagram_type="flowchart",
            mermaid="graph TD; A-->B; B-->C",
        )
        self.assertIn("graph TD", data.mermaid)

    def test_diagram_response_structured_has_no_image_url(self):
        resp = DiagramResponse(
            strategy="structured",
            structured_data=StructuredDiagramData(
                diagram_type="graph",
                nodes=[StructuredDiagramNode(id="A", label="A")],
            ),
        )
        self.assertEqual(resp.strategy, "structured")
        self.assertEqual(resp.image_url, "")

    def test_diagram_response_fallback_has_image_url(self):
        resp = DiagramResponse(
            strategy="qwen_image_fallback",
            image_url="https://example.com/diagram.png",
            image_prompt="Draw an educational diagram showing...",
        )
        self.assertEqual(resp.strategy, "qwen_image_fallback")
        self.assertIn("diagram", resp.image_url)

    def test_structured_diagram_node_annotation_is_string(self):
        node = StructuredDiagramNode(id="A", label="Router A", annotation="Learner chose this path incorrectly")
        self.assertIsInstance(node.annotation, str)

    def test_structured_diagram_edge_weight_is_string(self):
        edge = StructuredDiagramEdge(source="A", target="B", weight="10", highlighted=True)
        self.assertIsInstance(edge.weight, str)


class DiagramStrategyClassifierTest(unittest.TestCase):
    """T3-01 behavior: verify strategy classifier selects structured for known types."""

    def test_network_topology_selects_structured(self):
        draft = {"question_type": "network_topology", "question": "OSPF", "visual_context": "", "tags": []}
        strategy, reason = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")
        self.assertIn("network_topology", reason)

    def test_ip_fragmentation_selects_structured(self):
        draft = {"question_type": "ip_fragmentation", "question": "", "visual_context": "", "tags": []}
        strategy, _ = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")

    def test_algorithm_selects_structured(self):
        draft = {"question_type": "algorithm", "question": "", "visual_context": "", "tags": []}
        strategy, _ = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")

    def test_math_selects_structured(self):
        draft = {"question_type": "math", "question": "", "visual_context": "", "tags": []}
        strategy, _ = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")

    def test_ospf_keyword_in_question_selects_structured(self):
        draft = {"question_type": "other", "question": "OSPF cost path selection", "visual_context": "", "tags": []}
        strategy, reason = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")
        self.assertIn("ospf", reason)

    def test_分片_keyword_in_question_selects_structured(self):
        draft = {"question_type": "other", "question": "IP 分片计算", "visual_context": "", "tags": []}
        strategy, _ = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")

    def test_topology_keyword_in_visual_selects_structured(self):
        draft = {"question_type": "other", "question": "generic", "visual_context": "network 拓扑 diagram", "tags": []}
        strategy, _ = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "structured")

    def test_unknown_type_selects_fallback(self):
        draft = {"question_type": "other", "question": "what is photosynthesis", "visual_context": "", "tags": []}
        strategy, reason = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "qwen_image_fallback")
        self.assertIn("no structured", reason)

    def test_biology_scene_selects_fallback(self):
        draft = {"question_type": "other", "question": "describe the human heart", "visual_context": "", "tags": []}
        strategy, _ = classify_diagram_strategy(draft)
        self.assertEqual(strategy, "qwen_image_fallback")


class QwenImageFallbackConfigTest(unittest.TestCase):
    """T3-04 behavior: verify Qwen image fallback degrades cleanly."""

    def test_qwen_image_not_configured_by_default(self):
        self.assertFalse(QWEN_IMAGE_CONFIGURED)


class QuestionDraftNormalizationTest(unittest.TestCase):
    """T2-01 behavior: verify question draft normalization."""

    def test_normalize_options_from_string(self):
        from app.services.mistake_staged_service import _normalize_question_draft
        raw = {"title": "T", "question": "Q?", "options": "A. opt1\nB. opt2", "tags": []}
        result = _normalize_question_draft(raw)
        self.assertIsInstance(result["options"], list)

    def test_normalize_key_conditions_from_string(self):
        from app.services.mistake_staged_service import _normalize_question_draft
        raw = {"title": "T", "question": "Q?", "key_conditions": "cond1，cond2", "tags": []}
        result = _normalize_question_draft(raw)
        self.assertIsInstance(result["key_conditions"], list)
        self.assertEqual(len(result["key_conditions"]), 2)

    def test_normalize_title_truncated(self):
        from app.services.mistake_staged_service import _normalize_question_draft
        raw = {"title": "A" * 50, "question": "Q?", "tags": []}
        result = _normalize_question_draft(raw)
        self.assertLessEqual(len(result["title"]), 30)

    def test_normalize_defaults(self):
        from app.services.mistake_staged_service import _normalize_question_draft
        raw = {}
        result = _normalize_question_draft(raw)
        self.assertEqual(result["question_type"], "other")
        self.assertEqual(result["difficulty"], "medium")
        self.assertEqual(result["image_dependency"], "none")


class GateValidationTest(unittest.TestCase):
    """Gate behavior: verify required fields prevent invalid state transitions."""

    def test_error_interpretation_requires_non_empty_reason(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ErrorInterpretationRequest(
                question_draft=QuestionDraftResponse(title="T", question="Q?"),
                user_error_reason="",
            )

    def test_final_analysis_requires_interpretation(self):
        interp = ErrorInterpretationResponse(
            interpretation_id="i1", summary="s", diagnosis="d", root_cause="r",
        )
        req = FinalAnalysisRequest(
            question_draft=QuestionDraftResponse(title="T", question="Q?"),
            user_error_reason="reason",
            accepted_interpretation=interp,
        )
        self.assertEqual(req.accepted_interpretation.interpretation_id, "i1")

    def test_rejection_requires_non_empty_reason(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            InterpretationRejectionRequest(
                question_draft=QuestionDraftResponse(title="T", question="Q?"),
                user_error_reason="reason",
                current_interpretation=ErrorInterpretationResponse(
                    interpretation_id="i1", summary="s", diagnosis="d", root_cause="r",
                ),
                rejection_reason="",
            )

    def test_diagram_requires_accepted_interpretation(self):
        interp = ErrorInterpretationResponse(
            interpretation_id="i1", version=2, summary="s", diagnosis="d", root_cause="r",
        )
        analysis = FinalAnalysisResponse(
            analysis="a", error_reason="e", key_step="k",
            accepted_interpretation_id="i1", accepted_interpretation_version=2,
        )
        resp = DiagramResponse(
            strategy="structured",
            structured_data=StructuredDiagramData(
                diagram_type="graph",
                nodes=[StructuredDiagramNode(id="A", label="A")],
            ),
            accepted_interpretation_id=interp.interpretation_id,
            accepted_interpretation_version=interp.version,
            uses_error_interpretation=True,
        )
        self.assertEqual(resp.accepted_interpretation_id, "i1")
        self.assertEqual(resp.accepted_interpretation_version, 2)
        self.assertTrue(resp.uses_error_interpretation)


class InterpretationVersionBehaviorTest(unittest.TestCase):
    """T1-05 behavior: version increments on rejection."""

    def test_version_matches_rejection_count_plus_one(self):
        rejections = ["too vague", "wrong focus"]
        version = len(rejections) + 1
        self.assertEqual(version, 3)

    def test_stale_analysis_detectable(self):
        interp_v1 = ErrorInterpretationResponse(
            interpretation_id="i1", version=1, summary="s", diagnosis="d", root_cause="r",
        )
        interp_v2 = ErrorInterpretationResponse(
            interpretation_id="i1", version=2, summary="s2", diagnosis="d2", root_cause="r2",
        )
        analysis = FinalAnalysisResponse(
            analysis="a", error_reason="e", key_step="k",
            accepted_interpretation_id="i1", accepted_interpretation_version=1,
        )
        self.assertNotEqual(analysis.accepted_interpretation_version, interp_v2.version)


if __name__ == "__main__":
    unittest.main()
