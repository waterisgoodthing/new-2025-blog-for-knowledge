import main

from app.models.ai_call_log import AiCallLog
from app.models.ai_run import AiRun
from app.schemas.ai_call_log import AiCallLogOut


def test_business_runs_and_technical_logs_are_distinct_tables():
    assert AiRun.__tablename__ == "ai_runs"
    assert AiCallLog.__tablename__ == "ai_call_logs"
    assert AiRun.__table__ is not AiCallLog.__table__


def test_legacy_call_log_routes_remain_registered():
    contracts = {
        (route.path, method)
        for route in main.app.routes
        for method in getattr(route, "methods", set())
    }
    assert ("/api/ai/call-logs", "GET") in contracts
    assert ("/api/ai/call-logs/stats", "GET") in contracts


def test_legacy_call_log_response_contract_is_unchanged():
    assert set(AiCallLogOut.model_fields) == {
        "id",
        "task_type",
        "provider_used",
        "model",
        "latency_ms",
        "success",
        "error",
        "fallback_used",
        "attempts",
        "prompt_version",
        "created_at",
    }
