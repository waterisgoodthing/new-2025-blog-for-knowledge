"""Deterministic synthetic seed and paused-baseline setup for LSR-03.

This module is intentionally invoked only as a child of
``lsr03_guarded_runner.py`` with the project's private virtualenv.  It refuses
to seed a non-empty target and emits machine-readable identity/count/ID
evidence before the actual-table rollback rehearsal starts.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from tests.lsr03_guarded_runner import (
    GuardError,
    identity_probe,
    parse_isolated_url,
    require_project_runtime,
)


SOURCE_ACTOR = uuid.UUID("11111111-1111-4111-8111-111111111111")
QUESTION_ACTOR = uuid.UUID("22222222-2222-4222-8222-222222222222")
MISTAKE_ACTOR = uuid.UUID("33333333-3333-4333-8333-333333333333")
BASELINE_SOURCE = uuid.UUID("44444444-4444-4444-8444-444444444445")
ROLLBACK_ACTOR = uuid.UUID("55555555-5555-4555-8555-555555555555")
SCHEDULE_ACTOR = uuid.UUID("66666666-6666-4666-8666-666666666666")
PRE026_RESTORE_SENTINEL = uuid.UUID("77777777-7777-4777-8777-777777777777")
SUBJECT_ID = 1
KNOWLEDGE_POINT_ID = 1
SYNTHETIC_OPTIONS = ({"key": "A", "text": "4"}, {"key": "B", "text": "3"})
SYNTHETIC_MY_ANSWER = "B"
SYNTHETIC_CORRECT_ANSWER = "A"


def _runner_url(raw: str) -> str:
    parsed = urlsplit(raw)
    return urlunsplit(
        (parsed.scheme, f"legacy_note_adapter_runner@{parsed.hostname}:{parsed.port}", parsed.path, "", "")
    )


def _require_guarded_invocation(raw: str) -> None:
    require_project_runtime()
    parsed = parse_isolated_url(raw)
    expected_prefix = f"lsr03:{parsed.database}@{parsed.host}:{parsed.port}"
    if os.environ.get("DATABASE_URL") != raw or os.environ.get("LSR03_LOG_PREFIX") != expected_prefix:
        raise GuardError("LSR03_SEED_MUST_RUN_THROUGH_GUARDED_RUNNER")


async def _seed_source_data(raw: str) -> dict[str, object]:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(raw, poolclass=None)
    try:
        async with engine.begin() as connection:
            for table in (
                "users",
                "subjects",
                "knowledge_points",
                "legacy_note_migrations",
                "legacy_migration_approval_authorizations",
                "legacy_migration_rollback_admins",
            ):
                count = int(await connection.scalar(text(f"SELECT count(*) FROM public.{table}")))
                if count != 0:
                    raise GuardError(f"LSR03_SEED_TARGET_NOT_EMPTY:{table}")
            note_count = int(await connection.scalar(text(
                "SELECT count(*) FROM public.notes WHERE id <> :sentinel"
            ), {"sentinel": PRE026_RESTORE_SENTINEL}))
            if note_count != 0:
                raise GuardError("LSR03_SEED_TARGET_NOT_EMPTY:notes")
            for user_id, username in (
                (SOURCE_ACTOR, "lsr03_r4_source"),
                (QUESTION_ACTOR, "lsr03_r4_question"),
                (MISTAKE_ACTOR, "lsr03_r4_mistake"),
                (ROLLBACK_ACTOR, "lsr03_r4_rollback"),
                (SCHEDULE_ACTOR, "lsr03_schedule"),
            ):
                await connection.execute(text("""
                  INSERT INTO public.users(id,username,password_hash,is_admin)
                  VALUES (:id,:username,'lsr03-fixture',true)
                """), {"id": user_id, "username": username})
            await connection.execute(text("""
              INSERT INTO public.subjects(id,name,status,sort_order)
              VALUES (1,'LSR03 R4 Subject','active',0)
            """))
            await connection.execute(text("""
              INSERT INTO public.knowledge_points(id,subject_id,name,status,sort_order)
              VALUES (1,1,'LSR03 R4 KP','active',0)
            """))
            await connection.execute(text("""
              INSERT INTO public.notes(
                id,slug,title,content,type,status,hidden,summary,subject,difficulty,
                question,my_answer,correct_answer,analysis,knowledge_points,ef,interval,repetitions,
                ai_metadata,revision
              ) VALUES (
                :id,'lsr03-r4-paused','LSR03 R4 paused source','Synthetic LSR-03 R4 source',
                'mistake','published',true,'R4 fixture','LSR03 R4 Subject','easy',
                '2 + 2 = ?',:my_answer,:correct_answer,'R4 fixture analysis','LSR03 R4 KP',2.5,0,0,
                CAST(:metadata AS json),1
              )
            """), {
                "id": BASELINE_SOURCE,
                "my_answer": SYNTHETIC_MY_ANSWER,
                "correct_answer": SYNTHETIC_CORRECT_ANSWER,
                "metadata": '{"legacy_question":{"question_type":"single_choice","options":[{"key":"A","text":"4"},{"key":"B","text":"3"}]}}',
            })
            for user_id, kind in (
                (SOURCE_ACTOR, "source"),
                (QUESTION_ACTOR, "question_conversion"),
                (MISTAKE_ACTOR, "mistake_conversion"),
                (SCHEDULE_ACTOR, "schedule"),
            ):
                await connection.execute(text("""
                  INSERT INTO public.legacy_migration_approval_authorizations(user_id,approval_kind,enabled)
                  VALUES (:user_id,:kind,true)
                """), {"user_id": user_id, "kind": kind})
            await connection.execute(text("""
              INSERT INTO public.legacy_migration_rollback_admins(user_id,enabled)
              VALUES (:user_id,true)
            """), {"user_id": ROLLBACK_ACTOR})
            counts = {
                table: int(await connection.scalar(text(f"SELECT count(*) FROM public.{table}")))
                for table in ("users", "subjects", "knowledge_points", "notes")
            }
        return {"counts": counts}
    finally:
        await engine.dispose()


async def _create_paused_baseline(raw: str) -> dict[str, object]:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.services.legacy_note_migration_adapter import migrate

    engine = create_async_engine(_runner_url(raw), poolclass=None)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as session:
            payload = (await session.execute(text(
                "SELECT legacy_migration.canonicalize_legacy_note(:id)"
            ), {"id": BASELINE_SOURCE})).scalar_one()
            source_hash = (await session.execute(text(
                "SELECT encode(public.digest(convert_to(legacy_migration.canonicalize_legacy_note(:id)::text,'UTF8'),'sha256'),'hex')"
            ), {"id": BASELINE_SOURCE})).scalar_one()
            await session.commit()
            result = await migrate(
                session,
                source_note_id=BASELINE_SOURCE,
                mapping_version="v1-paused",
                source_approved_by=SOURCE_ACTOR,
                source_approved_at=datetime.now(timezone.utc),
                source_approval_sequence=1,
                question_conversion_approved_by=QUESTION_ACTOR,
                question_conversion_approved_at=datetime.now(timezone.utc),
                question_conversion_sequence=1,
                mistake_conversion_approved_by=MISTAKE_ACTOR,
                mistake_conversion_approved_at=datetime.now(timezone.utc),
                mistake_conversion_sequence=1,
                canonical_payload=payload,
                expected_source_hash=source_hash,
            )
            await session.commit()
            return {
                "ledger_id": str(result.ledger_id),
                "state": result.state,
                "target_question_id": str(result.target_question_id),
                "target_mistake_draft_item_id": str(result.target_mistake_draft_item_id),
                "target_mistake_draft_id": str(result.target_mistake_draft_id),
            }
    finally:
        await engine.dispose()


async def main() -> None:
    raw = os.environ.get("LSR03_DATABASE_URL", "")
    _require_guarded_invocation(raw)
    guard_identity = await identity_probe(raw)
    seed = await _seed_source_data(raw)
    baseline = await _create_paused_baseline(raw)
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    adapter_engine = create_async_engine(_runner_url(raw), poolclass=None)
    try:
        async with adapter_engine.connect() as connection:
            adapter_identity = dict((await connection.execute(text(
                "SELECT current_database() AS database, inet_server_addr()::text AS server_addr, "
                "inet_server_port() AS server_port, current_user AS current_user, session_user AS session_user"
            ))).mappings().one())
    finally:
        await adapter_engine.dispose()
    print(json.dumps({
        "identity": {"guard": guard_identity, "adapter": adapter_identity},
        "seed": {
            "source_actor": str(SOURCE_ACTOR),
            "question_actor": str(QUESTION_ACTOR),
            "mistake_actor": str(MISTAKE_ACTOR),
            "schedule_actor": str(SCHEDULE_ACTOR),
            "rollback_actor": str(ROLLBACK_ACTOR),
            "source_note": str(BASELINE_SOURCE),
            "subject_id": SUBJECT_ID,
            "knowledge_point_id": KNOWLEDGE_POINT_ID,
            **seed,
        },
        "paused_baseline": baseline,
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except GuardError as exc:
        print(f"LSR03_GUARD_ERROR: {exc}", flush=True)
        raise SystemExit(64)
