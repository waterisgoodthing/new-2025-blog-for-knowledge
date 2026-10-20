"""Guarded rollback/restore rehearsal for synthetic migration rows."""
import argparse
import asyncio, json, os, uuid
from urllib.parse import urlsplit, urlunsplit
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from tests.lsr03_guarded_runner import GuardError, identity_probe, parse_isolated_url

BASELINE_SOURCE = uuid.UUID("44444444-4444-4444-8444-444444444445")
ACTIVE_SOURCE = uuid.UUID("88888888-8888-4888-8888-888888888888")
ROLLBACK_ACTOR = uuid.UUID("55555555-5555-4555-8555-555555555555")
INBOUND_IDS = {
    "capture": uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
    "attempt": uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
    "attachment": uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
}

def _asyncpg_url(raw: str) -> str:
    return raw.replace("postgresql://", "postgresql+asyncpg://", 1)


def _role_url(raw: str, role: str) -> str:
    parsed = urlsplit(raw)
    return urlunsplit((parsed.scheme, f"{role}@{parsed.hostname}:{parsed.port}", parsed.path, "", ""))


def _validate_rehearsal_url(raw_url: str):
    """Require the same explicit URL that the fail-closed runner validated."""
    if not raw_url or os.environ.get("LSR03_DATABASE_URL") != raw_url:
        raise GuardError("run_inbound_fixtures requires the explicit LSR03_DATABASE_URL")
    inherited = os.environ.get("DATABASE_URL")
    if inherited and inherited != raw_url:
        raise GuardError("conflicting DATABASE_URL is forbidden")
    parsed = parse_isolated_url(raw_url)
    if not parsed.username:
        raise GuardError("isolated rehearsal URL must include an explicit admin identity")
    return parsed


async def _identity(session, expected_session_user: str, expected_database: str) -> dict[str, object]:
    """Return connection identity without reading any application table."""
    row = (await session.execute(text("""
      SELECT current_database() AS database, inet_server_addr()::text AS server_addr,
             inet_server_port() AS server_port, current_user AS current_user,
             session_user AS session_user
    """))).mappings().one()
    if (
        row["database"] != expected_database
        or row["server_addr"] not in {"127.0.0.1", "127.0.0.1/32", "::1", "::1/128"}
        or row["server_port"] != 55432
        or row["current_user"] != expected_session_user
        or row["session_user"] != expected_session_user
    ):
        raise AssertionError(f"unexpected isolated identity: {dict(row)}")
    return dict(row)


async def _ledger_snapshot(session, ledger_id: uuid.UUID) -> dict[str, object]:
    """Read every ledger column through the fixture-admin session only."""
    row = (await session.execute(text(f"""
      SELECT * FROM public.legacy_note_migrations WHERE id=:id
    """), {"id": ledger_id})).mappings().one()
    return dict(row)


async def _relation_snapshot(session, baseline: dict[str, object]) -> dict[str, list[dict[str, object]]]:
    """Capture all actual inbound rows relevant to this synthetic fixture."""
    snapshots: dict[str, list[dict[str, object]]] = {}
    for name, table, key, value in (
        ("capture", "capture_items", "id", INBOUND_IDS["capture"]),
        ("attempt", "attempts", "id", INBOUND_IDS["attempt"]),
        ("mistake_draft", "mistake_drafts", "id", baseline["target_mistake_draft_id"]),
        ("attachment", "attachments", "id", INBOUND_IDS["attachment"]),
    ):
        rows = (await session.execute(text(f"SELECT * FROM public.{table} WHERE {key}=:value"), {"value": value})).mappings().all()
        snapshots[name] = [dict(row) for row in rows]
    return snapshots


async def _audit_event_snapshot(session, ledger_id: uuid.UUID) -> dict[str, list[dict[str, object]]]:
    """Capture rollback audit/events so a rejected call cannot append either."""
    events = (await session.execute(text(
        "SELECT * FROM public.legacy_note_migration_events WHERE ledger_id=:id ORDER BY id"
    ), {"id": ledger_id})).mappings().all()
    audits = (await session.execute(text(
        "SELECT * FROM public.legacy_migration_rollback_audits WHERE ledger_id=:id ORDER BY ledger_id"
    ), {"id": ledger_id})).mappings().all()
    return {"events": [dict(row) for row in events], "audits": [dict(row) for row in audits]}


async def _assert_zero_mutation(
    session,
    baseline: dict[str, object],
    expected_relations: dict[str, list[dict[str, object]]],
    expected_audit_events: dict[str, list[dict[str, object]]],
    label: str,
) -> dict[str, object]:
    """Prove a blocked rollback left every ledger/inbound/audit row unchanged."""
    after = await _ledger_snapshot(session, baseline["id"])
    if after != baseline:
        changed = sorted(key for key in set(after) | set(baseline) if after.get(key) != baseline.get(key))
        raise AssertionError(f"{label}: rollback mutated ledger columns {changed}")
    if await _relation_snapshot(session, baseline) != expected_relations:
        raise AssertionError(f"{label}: rollback mutated an inbound relation")
    if await _audit_event_snapshot(session, baseline["id"]) != expected_audit_events:
        raise AssertionError(f"{label}: rollback appended or changed audit/event rows")
    inbound = await session.scalar(text("""
      SELECT (
        EXISTS (SELECT 1 FROM public.capture_items WHERE id=:capture)
        OR EXISTS (SELECT 1 FROM public.attempts WHERE id=:attempt)
        OR EXISTS (SELECT 1 FROM public.mistake_drafts WHERE id=:draft AND attempt_id=:attempt)
      )
    """), {"capture": INBOUND_IDS["capture"], "attempt": INBOUND_IDS["attempt"], "draft": baseline["target_mistake_draft_id"]})
    if inbound is not True:
        raise AssertionError(f"{label}: blocked fixture reference was not retained")
    return {
        "ledger_unchanged": True,
        "inbound_reference_retained": True,
        "audit_event_unchanged": True,
    }


async def _assert_cleanup(session, baseline: dict[str, object], label: str) -> dict[str, object]:
    """Prove each synthetic inbound row and attachment was cleaned up."""
    counts = (await session.execute(text("""
      SELECT
        (SELECT count(*) FROM public.capture_items WHERE id=:capture) AS capture,
        (SELECT count(*) FROM public.attempts WHERE id=:attempt) AS attempt,
        (SELECT count(*) FROM public.attachments WHERE id=:attachment) AS attachment,
        (SELECT count(*) FROM public.mistake_drafts WHERE id=:draft AND attempt_id=:attempt) AS attempt_link
    """), {"capture": INBOUND_IDS["capture"], "attempt": INBOUND_IDS["attempt"], "attachment": INBOUND_IDS["attachment"], "draft": baseline["target_mistake_draft_id"]})).mappings().one()
    if any(counts[key] != 0 for key in ("capture", "attempt", "attachment", "attempt_link")):
        raise AssertionError(f"{label}: fixture cleanup incomplete: {dict(counts)}")
    return {"cleanup_zero": True, **{key: int(counts[key]) for key in counts}}


async def _rollback_attempt(session, row, label: str) -> str:
    payload = {
        "ledger_id": str(row["id"]),
        "source_note_id": str(row["source_note_id"]),
        "mapping_version": row["mapping_version"],
        "source_hash": str(row["source_hash"]),
    }
    payload_text = json.dumps(payload, separators=(",", ":"))
    ref = (await session.execute(text(
        "SELECT encode(public.digest(convert_to(CAST(:p AS jsonb)::text,'UTF8'),'sha256'),'hex')"
    ), {"p": payload_text})).scalar_one()
    await session.execute(text("""
      SELECT legacy_migration.load_legacy_migration_rollback_audit(
        :ledger,:source,:mapping,:hash,:ref,CAST(:payload AS jsonb))
    """), {"ledger": row["id"], "source": row["source_note_id"], "mapping": row["mapping_version"], "hash": str(row["source_hash"]), "ref": ref, "payload": payload_text})
    try:
        await session.execute(text("""
          SELECT legacy_migration.transition_legacy_note_migration(
            :ledger,'migrated_paused','rolled_back',:actor,'restore',:source,:mapping,:hash,
            ROW(:qditem,:qdraft,:question,:qsource,:mditem,:mdraft,:mistake,:review,:qkps,:projections)::legacy_migration.legacy_note_migration_target_bundle,
            :ref,:ref,NULL,NULL,'{}')
        """), {"ledger": row["id"], "actor": ROLLBACK_ACTOR, "source": row["source_note_id"], "mapping": row["mapping_version"], "hash": str(row["source_hash"]), "ref": ref, "qditem": row["target_question_draft_item_id"], "qdraft": row["target_question_draft_id"], "question": row["target_question_id"], "qsource": row["target_question_source_id"], "mditem": row["target_mistake_draft_item_id"], "mdraft": row["target_mistake_draft_id"], "mistake": row["target_mistake_id"], "review": row["target_review_item_id"], "qkps": row["target_qkp_ids"], "projections": row["target_projection_ids"]})
    except Exception as exc:  # expected database rejection; caller rolls back
        return repr(exc)
    raise AssertionError(f"{label}: rollback unexpectedly succeeded")


async def run_inbound_fixtures(raw_url: str) -> dict[str, object]:
    """Insert one real inbound row at a time, then prove rollback is blocked.

    The fixture setup/cleanup uses the isolated superuser only; the rollback
    call itself uses the exact adapter-runner session identity.
    """
    parsed = _validate_rehearsal_url(raw_url)
    guard_identity = await identity_probe(raw_url)
    admin_engine = create_async_engine(_asyncpg_url(raw_url), poolclass=None)
    adapter_engine = create_async_engine(_asyncpg_url(_role_url(raw_url, "legacy_note_adapter_runner")), poolclass=None)
    admin_maker = async_sessionmaker(admin_engine, expire_on_commit=False)
    adapter_maker = async_sessionmaker(adapter_engine, expire_on_commit=False)
    results: dict[str, object] = {}
    try:
        async with admin_maker() as admin:
            admin_identity = await _identity(admin, parsed.username or "postgres", parsed.database)
            baseline_id = (await admin.execute(text("""
              SELECT id
                FROM public.legacy_note_migrations
               WHERE source_note_id=:source
                 AND mapping_version='v1-paused'
                 AND state='migrated_paused'
            """), {"source": BASELINE_SOURCE})).scalar_one()
            baseline = await _ledger_snapshot(admin, baseline_id)
            baseline_audit_events = await _audit_event_snapshot(admin, baseline["id"])
        async with adapter_maker() as adapter:
            adapter_identity = await _identity(adapter, "legacy_note_adapter_runner", parsed.database)
        for label in ("capture", "attempt", "mistake_draft_attempt_id"):
            expected_relations: dict[str, list[dict[str, object]]] | None = None
            async with admin_maker() as setup:
                if label == "capture":
                    await setup.execute(text("""
                      INSERT INTO public.attachments
                        (id,original_name,storage_key,mime_type,size_bytes,checksum_sha256,display_name,created_by)
                      VALUES (:id,'lsr03-fixture.txt','lsr03-fixture.txt','text/plain',0,repeat('c',64),'lsr03-fixture.txt',NULL)
                    """), {"id": INBOUND_IDS["attachment"]})
                    await setup.execute(text("""
                      INSERT INTO public.capture_items
                        (id,source_attachment_id,status,last_stage,mistake_draft_item_id)
                      VALUES (:id,:attachment,'converted','convert',:draft_item)
                    """), {"id": INBOUND_IDS["capture"], "attachment": INBOUND_IDS["attachment"], "draft_item": baseline["target_mistake_draft_item_id"]})
                elif label == "attempt":
                    await setup.execute(text("""
                      INSERT INTO public.attempts
                        (id,question_id,submitted_answer,is_correct,mistake_draft_item_id)
                      VALUES (:id,:question,'fixture',false,:draft_item)
                    """), {"id": INBOUND_IDS["attempt"], "question": baseline["target_question_id"], "draft_item": baseline["target_mistake_draft_item_id"]})
                else:
                    await setup.execute(text("""
                      INSERT INTO public.attempts
                        (id,question_id,submitted_answer,is_correct,mistake_draft_item_id)
                      VALUES (:id,:question,'fixture',false,NULL)
                    """), {"id": INBOUND_IDS["attempt"], "question": baseline["target_question_id"]})
                    await setup.execute(text("""
                      UPDATE public.mistake_drafts
                         SET question_id=:question, question_draft_id=NULL, attempt_id=:attempt
                       WHERE id=:draft
                    """), {"question": baseline["target_question_id"], "attempt": INBOUND_IDS["attempt"], "draft": baseline["target_mistake_draft_id"]})
                await setup.commit()
            async with admin_maker() as snapshot:
                expected_relations = await _relation_snapshot(snapshot, baseline)
            async with adapter_maker() as adapter:
                error = await _rollback_attempt(adapter, baseline, label)
                await adapter.rollback()
            async with admin_maker() as verify:
                zero_mutation = await _assert_zero_mutation(
                    verify, baseline, expected_relations, baseline_audit_events, label
                )
                results[label] = {
                    "error_contains_snapshot_restore_required": "SNAPSHOT_RESTORE_REQUIRED" in error,
                    "error": error.splitlines()[-1][:160],
                    **zero_mutation,
                }
            async with admin_maker() as cleanup:
                if label == "capture":
                    await cleanup.execute(text("DELETE FROM public.capture_items WHERE id=:id"), {"id": INBOUND_IDS["capture"]})
                    await cleanup.execute(text("DELETE FROM public.attachments WHERE id=:id"), {"id": INBOUND_IDS["attachment"]})
                elif label == "attempt":
                    await cleanup.execute(text("DELETE FROM public.attempts WHERE id=:id"), {"id": INBOUND_IDS["attempt"]})
                else:
                    await cleanup.execute(text("""
                      UPDATE public.mistake_drafts SET question_id=:question,attempt_id=NULL
                       WHERE id=:draft
                    """), {"question": baseline["target_question_id"], "draft": baseline["target_mistake_draft_id"]})
                    await cleanup.execute(text("DELETE FROM public.attempts WHERE id=:id"), {"id": INBOUND_IDS["attempt"]})
                await cleanup.commit()
                await _assert_cleanup(cleanup, baseline, label)
        if not all(result["error_contains_snapshot_restore_required"] for result in results.values()):
            raise AssertionError(results)
        evidence = {
            "actual_table_inbound": results,
            "identity": {"guard": guard_identity, "admin": admin_identity, "adapter": adapter_identity},
            "parsed_database": parsed.database,
            "cleanup_zero": True,
        }
        print(json.dumps(evidence, sort_keys=True))
        return evidence
    finally:
        await adapter_engine.dispose()
        await admin_engine.dispose()

async def main():
    url = _asyncpg_url(_role_url(os.environ["LSR03_DATABASE_URL"], "legacy_note_adapter_runner"))
    engine = create_async_engine(url)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with maker() as s:
            row = (await s.execute(text("""
              SELECT id,source_note_id,mapping_version,source_hash,state,
                target_question_draft_item_id,target_question_draft_id,target_question_id,
                target_question_source_id,target_mistake_draft_item_id,target_mistake_draft_id,
                target_mistake_id,target_review_item_id,target_qkp_ids,target_projection_ids
              FROM public.legacy_note_migrations
              WHERE source_note_id=:source
                AND mapping_version='v1-active'
               AND state='migrated_active'
            """), {"source": ACTIVE_SOURCE})).mappings().one()
            assert row["state"] == "migrated_active"
            payload = {"source": str(row["source_note_id"]), "mapping": row["mapping_version"], "action": "restore"}
            payload_text = json.dumps(payload, separators=(",", ":"))
            ref = (await s.execute(text("SELECT encode(public.digest(convert_to(CAST(:p AS jsonb)::text,'UTF8'),'sha256'),'hex')"), {"p": payload_text})).scalar_one()
            await s.execute(text("""
              SELECT legacy_migration.load_legacy_migration_rollback_audit(
                :ledger,:source,:mapping,:hash,:ref,CAST(:payload AS jsonb))
            """), {"ledger": row["id"], "source": row["source_note_id"], "mapping": row["mapping_version"], "hash": str(row["source_hash"]), "ref": ref, "payload": payload_text})
            await s.execute(text("""
              SELECT legacy_migration.transition_legacy_note_migration(
                :ledger,'migrated_active','rolled_back',:actor,'restore',:source,:mapping,:hash,
                ROW(:qditem,:qdraft,:question,:qsource,:mditem,:mdraft,:mistake,:review,:qkps,:projections)::legacy_migration.legacy_note_migration_target_bundle,
                :ref,:ref,NULL,NULL,'{}')
            """), {"ledger": row["id"], "actor": ROLLBACK_ACTOR, "source": row["source_note_id"], "mapping": row["mapping_version"], "hash": str(row["source_hash"]), "ref": ref, "qditem": row["target_question_draft_item_id"], "qdraft": row["target_question_draft_id"], "question": row["target_question_id"], "qsource": row["target_question_source_id"], "mditem": row["target_mistake_draft_item_id"], "mdraft": row["target_mistake_draft_id"], "mistake": row["target_mistake_id"], "review": row["target_review_item_id"], "qkps": row["target_qkp_ids"], "projections": row["target_projection_ids"]})
            await s.commit()
            state = dict((await s.execute(text("""
              SELECT state,rollback_actor_id,rollback_event_id,rollback_reference,
                     target_question_draft_item_id,target_question_draft_id,target_question_source_id,
                     target_qkp_ids,target_question_id,target_projection_ids,target_mistake_draft_item_id,
                     target_mistake_draft_id,target_mistake_id,target_review_item_id,target_bundle_hash
                FROM public.legacy_note_migrations WHERE id=:id
            """), {"id": row["id"]})).mappings().one())
            delete_counts = dict((await s.execute(text("""
              SELECT
                (SELECT count(*) FROM public.review_items WHERE id=:review) AS review_items,
                (SELECT count(*) FROM public.knowledge_point_links WHERE id=ANY(CAST(:projections AS integer[]))) AS projections,
                (SELECT count(*) FROM public.mistakes WHERE id=:mistake) AS mistakes,
                (SELECT count(*) FROM public.mistake_drafts WHERE id=:mdraft) AS mistake_drafts,
                (SELECT count(*) FROM public.question_sources WHERE id=:qsource) AS question_sources,
                (SELECT count(*) FROM public.question_knowledge_points WHERE question_id=:question) AS qkps,
                (SELECT count(*) FROM public.questions WHERE id=:question) AS questions,
                (SELECT count(*) FROM public.question_drafts WHERE id=:qdraft) AS question_drafts,
                (SELECT count(*) FROM public.draft_items WHERE id=ANY(CAST(:draft_items AS uuid[]))) AS draft_items
            """), {
                "review": row["target_review_item_id"], "projections": row["target_projection_ids"],
                "mistake": row["target_mistake_id"], "mdraft": row["target_mistake_draft_id"],
                "qsource": row["target_question_source_id"], "question": row["target_question_id"],
                "qdraft": row["target_question_draft_id"],
                "draft_items": [row["target_question_draft_item_id"], row["target_mistake_draft_item_id"]],
            })).mappings().one())
            event = dict((await s.execute(text("""
              SELECT id,ledger_id,source_note_id,mapping_version,source_hash,actor_id,
                     approval_kind,rollback_hash FROM public.legacy_note_migration_events
               WHERE id=:id AND ledger_id=:ledger
            """), {"id": state["rollback_event_id"], "ledger": row["id"]})).mappings().one())
            audit = dict((await s.execute(text("""
              SELECT ledger_id,source_note_id,mapping_version,source_hash,rollback_reference,rollback_json
                FROM public.legacy_migration_rollback_audits
               WHERE ledger_id=:ledger
            """), {"ledger": row["id"]})).mappings().one())
            replay_hash = (await s.execute(text(
                "SELECT encode(public.digest(convert_to(CAST(:payload AS jsonb)::text,'UTF8'),'sha256'),'hex')"
            ), {"payload": json.dumps(audit["rollback_json"], separators=(",", ":"))})).scalar_one()
            state_targets_null = state["state"] == "rolled_back" and all(
                state[key] is None for key in (
                    "target_question_draft_item_id", "target_question_draft_id", "target_question_source_id",
                    "target_qkp_ids", "target_question_id", "target_projection_ids",
                    "target_mistake_draft_item_id", "target_mistake_draft_id", "target_mistake_id",
                    "target_review_item_id", "target_bundle_hash",
                )
            )
            event_bound = (
                event["ledger_id"] == row["id"] and event["source_note_id"] == row["source_note_id"]
                and event["mapping_version"] == row["mapping_version"] and str(event["source_hash"]) == str(row["source_hash"])
                and event["actor_id"] == ROLLBACK_ACTOR and event["approval_kind"] == "rollback"
                and str(event["rollback_hash"]) == str(audit["rollback_reference"])
            )
            audit_bound = (
                audit["ledger_id"] == row["id"] and audit["source_note_id"] == row["source_note_id"]
                and audit["mapping_version"] == row["mapping_version"] and str(audit["source_hash"]) == str(row["source_hash"])
                and str(audit["rollback_reference"]) == str(state["rollback_reference"])
            )
            evidence = {
                "rollback_ledger_state": state,
                "pre_rollback_target_ids": {key: str(row[key]) if row[key] is not None else None for key in (
                    "target_question_draft_item_id", "target_question_draft_id", "target_question_source_id",
                    "target_question_id", "target_mistake_draft_item_id", "target_mistake_draft_id",
                    "target_mistake_id", "target_review_item_id", "target_qkp_ids", "target_projection_ids",
                )},
                "pre_rollback_target_counts": {key: int(value) for key, value in delete_counts.items()},
                "rollback_event": event,
                "rollback_audit": audit,
                "rollback_replay": {
                    "source_note_id": str(row["source_note_id"]), "mapping_version": row["mapping_version"],
                    "source_hash": str(row["source_hash"]), "rollback_reference": str(audit["rollback_reference"]),
                    "rollback_hash": str(event["rollback_hash"]), "rollback_audit_digest": replay_hash,
                    "identity_equal": replay_hash == str(audit["rollback_reference"]),
                },
                "checks": {
                    "state_targets_null": state_targets_null,
                    "all_pre_rollback_target_rows_deleted": all(value == 0 for value in delete_counts.values()),
                    "rollback_event_bound": event_bound,
                    "rollback_audit_bound": audit_bound,
                },
            }
            evidence["pass"] = all(evidence["checks"].values()) and evidence["rollback_replay"]["identity_equal"]
            if not evidence["pass"]:
                raise AssertionError(f"LSR03_ROLLBACK_EVIDENCE_FAILED:{evidence}")
            print(json.dumps(evidence, default=str, sort_keys=True))
    finally:
        await engine.dispose()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inbound-fixtures", action="store_true")
    args = parser.parse_args()
    if args.inbound_fixtures:
        asyncio.run(run_inbound_fixtures(os.environ["LSR03_DATABASE_URL"]))
    else:
        asyncio.run(main())
