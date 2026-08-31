from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.ai_run import (
    AiRunDecisionRequest,
    AiRunDetail,
    AiRunListItem,
    AiRunListResponse,
)


def _run_data() -> dict:
    now = datetime.now(UTC)
    return {
        "id": uuid4(),
        "task_type": "capture_draft",
        "target_type": "capture",
        "target_id": "target-1",
        "provider_used": "deepseek",
        "model": "model",
        "prompt_version": "v2",
        "status": "succeeded",
        "validation_status": "passed",
        "review_status": "pending",
        "review_revision": 0,
        "attempt": 1,
        "parent_run_id": None,
        "latency_ms": 100,
        "error_code": None,
        "error_message_safe": None,
        "warnings": [],
        "input_summary": "safe summary",
        "output_data": {
            "answer": "safe",
            "storage_key": "private/object",
            "api_key": "secret",
            "nested": {"path": "/Users/private/file.png", "value": "keep"},
        },
        "started_at": now,
        "finished_at": now,
        "reviewed_at": None,
        "created_at": now,
        "updated_at": now,
    }


def test_list_item_excludes_full_output_and_replay_input():
    item = AiRunListItem.model_validate(_run_data())

    payload = item.model_dump()
    assert "output_data" not in payload
    assert "replay_input" not in payload
    assert "input_summary" not in payload


def test_list_response_includes_pagination_metadata_without_sensitive_payloads():
    response = AiRunListResponse(
        items=[AiRunListItem.model_validate(_run_data())],
        total=31,
        limit=20,
        offset=20,
    )

    payload = response.model_dump()
    assert payload["total"] == 31
    assert payload["limit"] == 20
    assert payload["offset"] == 20
    assert "output_data" not in payload["items"][0]
    assert "replay_input" not in payload["items"][0]


def test_detail_sanitizes_controlled_output_and_never_exposes_replay_input():
    detail = AiRunDetail.model_validate(_run_data())

    payload = detail.model_dump()
    assert payload["output_data"] == {
        "answer": "safe",
        "nested": {"value": "keep"},
    }
    assert "replay_input" not in payload
    assert "input_summary" not in payload


def test_decision_requires_revision_and_bounded_note():
    request = AiRunDecisionRequest(
        decision="accepted",
        expected_revision=0,
        note="reviewed",
    )
    assert request.expected_revision == 0

    with pytest.raises(ValidationError):
        AiRunDecisionRequest(decision="accepted", expected_revision=-1)
    with pytest.raises(ValidationError):
        AiRunDecisionRequest(
            decision="accepted",
            expected_revision=0,
            note="x" * 1001,
        )
