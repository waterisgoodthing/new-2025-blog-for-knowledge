from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_run import AiRun
from app.schemas.ai_run import sanitize_run_output
from app.services.audit_service import audit_action


_REPLAY_INPUT_ALLOWLIST: dict[str, frozenset[str]] = {
    "capture_draft": frozenset({"recognized_text", "user_error_reason"}),
    "capture_recognition": frozenset({"attachment_id", "mime_type"}),
    "analyze_text": frozenset(
        {
            "text",
            "question",
            "my_answer",
            "correct_answer",
            "user_error_analysis",
            "analysis_mode",
        }
    ),
    "generate_variant": frozenset({"knowledge_point", "subject"}),
    "generate_knowledge_card": frozenset({"knowledge_point", "subject"}),
}
_FORBIDDEN_REPLAY_KEYS = {
    "api_key",
    "authorization",
    "cookie",
    "image",
    "images",
    "path",
    "session_token",
    "storage_key",
    "token",
}


class AiRunConflict(Exception):
    """A requested Run transition conflicts with current state."""


class AiRunReplayUnavailable(AiRunConflict):
    """The Run has no safe, structured replay input."""


class AiRunNotFound(Exception):
    """The requested private Run does not exist."""


def _validate_replay_input(
    task_type: str,
    replay_input: dict | None,
) -> dict | None:
    if replay_input is None:
        return None
    allowed = _REPLAY_INPUT_ALLOWLIST.get(task_type, frozenset())
    for key, value in replay_input.items():
        normalized = str(key).casefold()
        if normalized in _FORBIDDEN_REPLAY_KEYS:
            raise ValueError(f"Replay input field is forbidden: {key}")
        if key not in allowed:
            raise ValueError(f"Replay input field is not allowed for {task_type}: {key}")
        if isinstance(value, str) and (
            value.startswith("data:") or "base64," in value
        ):
            raise ValueError(f"Replay input value is forbidden for field: {key}")
    return dict(replay_input)


def _require_running(run: AiRun) -> None:
    if run.status != "running":
        raise ValueError("AI Run must be running")


async def start_ai_run(
    db: AsyncSession,
    *,
    task_type: str,
    target_type: str | None = None,
    target_id: str | None = None,
    prompt_version: str | None = None,
    input_summary: str | None = None,
    replay_input: dict | None = None,
    review_required: bool = False,
    parent_run_id=None,
    attempt: int = 1,
) -> AiRun:
    safe_replay_input = _validate_replay_input(task_type, replay_input)
    run = AiRun(
        task_type=task_type,
        target_type=target_type,
        target_id=target_id,
        prompt_version=prompt_version,
        status="running",
        validation_status="pending",
        input_summary=input_summary[:1000] if input_summary else None,
        replay_input=safe_replay_input,
        attempt=attempt,
        parent_run_id=parent_run_id,
        review_status="pending" if review_required else "not_required",
        review_revision=0,
        started_at=datetime.now(UTC),
    )
    db.add(run)
    await db.flush()
    return run


async def complete_ai_run(
    db: AsyncSession,
    run: AiRun,
    *,
    provider_used: str | None = None,
    model: str | None = None,
    output_data: Any = None,
    validation_status: str,
    warnings: list | None = None,
    latency_ms: int | None = None,
) -> AiRun:
    _require_running(run)
    run.status = "succeeded"
    run.provider_used = provider_used
    run.model = model
    run.output_data = sanitize_run_output(output_data)
    run.validation_status = validation_status
    run.warnings = warnings or []
    run.latency_ms = latency_ms
    run.finished_at = datetime.now(UTC)
    await db.flush()
    return run


async def fail_ai_run(
    db: AsyncSession,
    run: AiRun,
    *,
    error_code: str,
    error_message_safe: str,
    provider_used: str | None = None,
    model: str | None = None,
    latency_ms: int | None = None,
) -> AiRun:
    _require_running(run)
    run.status = "failed"
    run.validation_status = "not_applicable"
    run.error_code = error_code[:50]
    run.error_message_safe = error_message_safe[:1000]
    run.provider_used = provider_used
    run.model = model
    run.latency_ms = latency_ms
    run.finished_at = datetime.now(UTC)
    await db.flush()
    return run


async def retry_ai_run(db: AsyncSession, parent: AiRun) -> AiRun:
    if parent.status == "running":
        raise AiRunConflict("A running AI Run cannot be retried")
    if not parent.replay_input:
        raise AiRunReplayUnavailable("AI Run has no replay input")
    return await start_ai_run(
        db,
        task_type=parent.task_type,
        target_type=parent.target_type,
        target_id=parent.target_id,
        prompt_version=parent.prompt_version,
        replay_input=parent.replay_input,
        review_required=parent.review_status != "not_required",
        parent_run_id=parent.id,
        attempt=parent.attempt + 1,
    )


async def decide_ai_run(
    db: AsyncSession,
    run: AiRun,
    *,
    decision: str,
    expected_revision: int,
    note: str | None = None,
    session_token: str | None = None,
    request=None,
) -> AiRun:
    if decision not in {"accepted", "rejected"}:
        raise ValueError("Decision must be accepted or rejected")
    if run.review_status == decision:
        return run
    if run.review_status in {"accepted", "rejected"}:
        raise AiRunConflict("AI Run already has a conflicting decision")
    if run.status != "succeeded":
        raise AiRunConflict("Only succeeded AI Runs can be reviewed")
    if run.validation_status not in {"passed", "warning"}:
        raise AiRunConflict("AI Run validation does not allow review")
    if run.review_status != "pending":
        raise AiRunConflict("AI Run is not pending review")
    if run.review_revision != expected_revision:
        raise AiRunConflict("AI Run review revision conflict")

    before_revision = run.review_revision
    run.review_status = decision
    run.review_revision += 1
    run.reviewed_at = datetime.now(UTC)
    run.review_note = note[:1000] if note else None
    await db.flush()
    await audit_action(
        db,
        action=f"ai_run.{decision.removesuffix('ed')}",
        session_token=session_token,
        request=request,
        entity_type="ai_run",
        entity_id=str(run.id),
        before={"review_status": "pending", "review_revision": before_revision},
        after={
            "review_status": decision,
            "review_revision": run.review_revision,
            "note_present": bool(note),
        },
    )
    await db.refresh(run)
    return run


async def get_ai_run(db: AsyncSession, run_id) -> AiRun:
    run = await db.get(AiRun, run_id)
    if run is None:
        raise AiRunNotFound("AI Run not found")
    return run


async def query_ai_runs(
    db: AsyncSession,
    *,
    task_type: str | None = None,
    status: str | None = None,
    validation_status: str | None = None,
    review_status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[AiRun], int]:
    filters = []
    if task_type:
        filters.append(AiRun.task_type == task_type)
    if status:
        filters.append(AiRun.status == status)
    if validation_status:
        filters.append(AiRun.validation_status == validation_status)
    if review_status:
        filters.append(AiRun.review_status == review_status)

    stmt = select(AiRun).where(*filters).order_by(AiRun.created_at.desc())
    result = await db.execute(stmt.limit(limit).offset(offset))
    count_result = await db.execute(
        select(func.count()).select_from(AiRun).where(*filters)
    )
    return list(result.scalars().all()), int(count_result.scalar_one())
