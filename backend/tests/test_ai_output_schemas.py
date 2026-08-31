"""Tests for AI output schemas — Batch 10 P0-03."""

import pytest
from pydantic import ValidationError

from app.schemas.ai_output import (
    KnowledgeCardOutput,
    RecognitionOutput,
    RecommendationOutput,
    VariantOutput,
)


class TestRecognitionOutput:
    def test_valid(self):
        out = RecognitionOutput(text="题目内容")
        assert out.text == "题目内容"

    def test_missing_text_raises(self):
        with pytest.raises(ValidationError):
            RecognitionOutput()

    def test_empty_text_allowed(self):
        """空字符串是合法的（AI 可能返回空）。"""
        out = RecognitionOutput(text="")
        assert out.text == ""


class TestVariantOutput:
    def test_valid_full(self):
        out = VariantOutput(
            question="什么是二分查找？",
            correct_answer="一种在有序数组中查找元素的算法",
            analysis="每次比较中间元素...",
            difficulty="medium",
            knowledge_points="二分查找,算法",
        )
        assert out.question == "什么是二分查找？"
        assert out.difficulty == "medium"

    def test_valid_minimal(self):
        out = VariantOutput(
            question="题",
            correct_answer="答",
            analysis="析",
        )
        assert out.difficulty == "medium"
        assert out.knowledge_points == ""

    def test_missing_required_raises(self):
        with pytest.raises(ValidationError):
            VariantOutput(question="题")


class TestKnowledgeCardOutput:
    def test_valid_full(self):
        out = KnowledgeCardOutput(
            title="二分查找知识卡片",
            content="## 核心概念\n...",
            knowledge_points="二分查找",
            subject="算法",
        )
        assert out.title == "二分查找知识卡片"

    def test_valid_minimal(self):
        out = KnowledgeCardOutput(title="卡片", content="内容")
        assert out.knowledge_points == ""
        assert out.subject == ""


class TestRecommendationOutput:
    def test_valid_full(self):
        out = RecommendationOutput(
            title="复习错题：二分查找",
            type="review",
            reason="这道错题今天到期复习",
            target="/mistakes/review",
            actionLabel="去复习",
        )
        assert out.type == "review"

    def test_valid_minimal(self):
        out = RecommendationOutput()
        assert out.title == ""
        assert out.type == "note"

    def test_extra_fields_ignored(self):
        out = RecommendationOutput.model_validate({
            "title": "test",
            "extra_field": "ignored",
        })
        assert out.title == "test"
