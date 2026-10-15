"""Canonical AI-creation contract (B05a/B05b).

A canonical, AI-assisted creation (currently: a mistake draft built from an AI
error-interpretation candidate) must be traceable to a *trusted* source and
saved atomically and idempotently. This module owns:

- the server-built ``creation_context`` persisted on the AiRun **before** the
  provider call (purpose, source question id/version, normalized input hash,
  output schema, prompt version);
- the confirmed-payload hash used to detect replays;
- :func:`confirm_canonical_creation`, a row-locked, per-run-serialised
  confirmation that either creates the entity once and binds the run, or
  returns the original entity on a replayed identical payload, or conflicts on
  a different payload/target.

Only runs created through this contract (non-NULL ``creation_context`` with a
known purpose) are confirmable. Historical/legacy runs keep NULL provenance and
are explicitly *not* eligible, so a stray ``source_run_id`` can never be bound
to an unrelated entity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Awaitable, Callable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_run import AiRun
from app.services.ai_run_service import (
    AiRunConflict,
    AiRunError,
    AiRunNotFound,
    AiRunTargetConflict,
)

PURPOSE_CANONICAL_MISTAKE_DRAFT = "mistake_canonical_draft"
CANONICAL_ENTITY_TYPE_MISTAKE_DRAFT = "MistakeDraft"

CANONICAL_CREATION_TASK_TYPES: frozenset[str] = frozenset(
    {"mistake_error_interpretation"}
)

CANONICAL_PURPOSES: dict[str, str] = {
    PURPOSE_CANONICAL_MISTAKE_DRAFT: CANONICAL_ENTITY_TYPE_MISTAKE_DRAFT,
}


class AiRunForbidden(AiRunError):
    """The requested confirmation is not owned by the acting admin."""


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_payload(payload: dict) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def canonical_input_hash(
    *,
    question_id,
    question_version: int,
    my_answer: str | None,
    user_error_reason: str | None,
) -> str:
    return hash_payload(
        {
            "question_id": str(question_id),
            "question_version": int(question_version),
            "my_answer": (my_answer or "").strip(),
            "user_error_reason": (user_error_reason or "").strip(),
        }
    )


def build_creation_context(
    *,
    purpose: str,
    source_question_id,
    source_question_version: int,
    input_hash: str,
    output_schema: str,
    prompt_version: str | None,
    input_summary: str | None = None,
) -> dict:
    if purpose not in CANONICAL_PURPOSES:
        raise ValueError(f"Unknown canonical creation purpose: {purpose}")
    return {
        "contract": "canonical_ai_creation_v1",
        "purpose": purpose,
        "source_question_id": str(source_question_id),
        "source_question_version": int(source_question_version),
        "input_hash": input_hash,
        "output_schema": output_schema,
        "prompt_version": prompt_version,
        "input_summary": (input_summary or "")[:200],
    }


async def _lock_run(db: AsyncSession, run_id: UUID) -> AiRun:
    run = (
        await db.execute(
            select(AiRun)
            .where(AiRun.id == run_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    if run is None:
        raise AiRunNotFound("AI Run not found")
    return run


def _validate_run_for_confirmation(
    run: AiRun,
    *,
    actor_id: UUID | None,
    purpose: str,
    task_types: frozenset[str],
) -> dict:
    if actor_id is not None and run.created_by is not None and run.created_by != actor_id:
        raise AiRunForbidden("AI Run was created by a different admin")
    context = run.creation_context or {}
    if context.get("contract") != "canonical_ai_creation_v1" or context.get("purpose") != purpose:
        raise AiRunConflict("AI Run is not a canonical creation run for this purpose")
    if run.task_type not in task_types:
        raise AiRunConflict(f"AI Run task type is not canonical: {run.task_type}")
    if run.status != "succeeded":
        raise AiRunConflict("Only succeeded AI Runs can be confirmed")
    if run.validation_status not in {"passed", "warning"}:
        raise AiRunConflict("AI Run validation does not allow confirmation")
    if run.review_status == "rejected":
        raise AiRunConflict("A rejected AI Run cannot be confirmed")
    return context


async def confirm_canonical_creation(
    db: AsyncSession,
    *,
    run_id: UUID,
    expected_revision: int,
    actor_id: UUID | None,
    entity_type: str,
    purpose: str,
    payload: dict,
    create_entity: Callable[[AiRun, dict], Awaitable[str | UUID]],
    load_entity: Callable[[str], Awaitable[object | None]],
    task_types: frozenset[str] = CANONICAL_CREATION_TASK_TYPES,
) -> tuple[str, bool]:
    """Confirm a canonical AI run into an entity, atomically and idempotently.

    Returns ``(entity_id, created)``. Validation/locking order is fixed so every
    confirm/reject/replay path serialises on the same AiRun row:

    1. lock and refresh the run;
    2. verify actor, purpose/task, status, validation, not-rejected;
    3. verify the review revision for unbound runs;
    4. compute the confirmed-payload hash and decide replay vs create.
    """
    run = await _lock_run(db, run_id)
    context = _validate_run_for_confirmation(
        run, actor_id=actor_id, purpose=purpose, task_types=task_types
    )

    new_hash = hash_payload(payload)

    if run.target_id is not None:
        # Already bound: idempotent only for the identical payload.
        if run.confirmed_payload_hash != new_hash:
            raise AiRunTargetConflict(
                "AI Run is already bound to a different confirmed payload"
            )
        existing = await load_entity(run.target_id)
        if existing is None:
            raise AiRunConflict("AI Run target is missing; refusing to recreate")
        return run.target_id, False

    if run.review_revision != expected_revision:
        raise AiRunConflict("AI Run review revision conflict")

    entity_id = await create_entity(run, context)
    if entity_id is None:
        raise AiRunConflict("Canonical entity creation returned no id")

    run.target_id = str(entity_id)
    run.target_type = entity_type
    run.confirmed_payload_hash = new_hash
    run.review_status = "accepted"
    run.review_revision += 1
    run.reviewed_at = datetime.now(UTC)
    run.confirmed_at = datetime.now(UTC)
    snapshot_context = dict(context)
    snapshot_context["confirmed_snapshot"] = {
        "payload_hash": new_hash,
        "payload": payload,
    }
    run.creation_context = snapshot_context
    await db.flush()
    return str(entity_id), True
