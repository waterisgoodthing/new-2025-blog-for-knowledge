"""AiRun persistence contract for Batch 11."""

from app.models.ai_run import AiRun


def test_ai_run_table_has_business_audit_fields():
    columns = AiRun.__table__.columns

    required = {
        "id",
        "task_type",
        "target_type",
        "target_id",
        "provider_used",
        "model",
        "prompt_version",
        "status",
        "validation_status",
        "input_summary",
        "replay_input",
        "output_data",
        "warnings",
        "error_code",
        "error_message_safe",
        "attempt",
        "parent_run_id",
        "review_status",
        "review_revision",
        "reviewed_at",
        "review_note",
        "latency_ms",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
    }

    assert required == set(columns.keys())


def test_ai_run_is_separate_from_technical_call_log():
    assert AiRun.__tablename__ == "ai_runs"
    foreign_keys = {
        fk.target_fullname
        for column in AiRun.__table__.columns
        for fk in column.foreign_keys
    }
    assert "ai_runs.id" in foreign_keys
    assert not any("ai_call_logs" in target for target in foreign_keys)
