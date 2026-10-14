#!/usr/bin/env python3
"""PR-09 verify: wk3-mistake-visibility-v1 ledger runner matrix.

Run exclusively through the Week 3 scratch guard:

    python3 scripts/week3-scratch-guard.py run \\
        --db-name astra_week3_pr09_verify_led \\
        --url postgresql+asyncpg://postgres@127.0.0.1:49621/astra_week3_pr09_verify_led \\
        -- backend/.venv/bin/python scripts/pr09_verify_ledger_matrix.py

Covers: dry-run zero persistence, full 4-cell W3-D06 e2e with canonical-izable
seeds, v1-* visibility reconcile, idempotent replay, ReviewItem v2 mapping,
and changed-source conflict behaviour.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "docs/workflows/personal-learning-system-convergence/week3/evidence"
MIG = EVIDENCE / "migrations"
SQL_DIR = EVIDENCE / "sql"

SUBJECT_NAME = "PR09 Verify Subject"
KP_ONE = "PR09 Verify KP One"
KP_TWO = "PR09 Verify KP Two"
LEAK_MARKER = "PR09LEAK_my_answer_f7c2a9"
NEXT_REVIEW_DATE = date(2030, 1, 15)

CELLS = [
    # (key, status, hidden, next_review, expected_visibility)
    ("published_visible", "published", False, NEXT_REVIEW_DATE, "public"),
    ("published_hidden", "published", True, None, "private"),
    ("unpublished_visible", "unpublished", False, NEXT_REVIEW_DATE, "private"),
    ("unpublished_hidden", "unpublished", True, None, "private"),
]

FAILURES: list[str] = []


def check(condition: bool, label: str, detail: str = "") -> bool:
    mark = "PASS" if condition else "FAIL"
    line = f"{mark}: {label}" + (f" | {detail}" if detail else "")
    print(line)
    if not condition:
        FAILURES.append(line)
    return condition


def write_json(name: str, data: object) -> None:
    MIG.mkdir(parents=True, exist_ok=True)
    path = MIG / f"pr-09-verify-{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def write_sql_log(name: str, body: str) -> None:
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    path = SQL_DIR / f"pr-09-verify-{name}.log"
    path.write_text(body, encoding="utf-8")
    print(f"WROTE {path.relative_to(ROOT)}")


def note_ai_metadata() -> str:
    return json.dumps({
        "legacy_question": {
            "question_type": "single_choice",
            "options": [
                {"key": "A", "text": "4"},
                {"key": "B", "text": "3"},
            ],
        }
    })


async def seed_foundation(session: AsyncSession) -> dict[str, uuid.UUID]:
    await session.execute(text(
        "INSERT INTO public.users (id,username,password_hash,is_admin) "
        "VALUES (gen_random_uuid(),'pr09-verify-admin','!',true) ON CONFLICT DO NOTHING"
    ))
    await session.execute(text(
        "DO $$ BEGIN "
        "IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_adapter_runner') THEN "
        "  CREATE ROLE legacy_note_adapter_runner LOGIN; "
        "END IF; "
        "END $$"
    ))
    subject_id = (await session.execute(text(
        "INSERT INTO public.subjects (name,status,sort_order) VALUES (:n,'active',0) RETURNING id"
    ), {"n": SUBJECT_NAME})).scalar_one()
    kp1 = (await session.execute(text(
        "INSERT INTO public.knowledge_points (subject_id,name,status,sort_order) "
        "VALUES (:s,:n,'active',0) RETURNING id"
    ), {"s": subject_id, "n": KP_ONE})).scalar_one()
    kp2 = (await session.execute(text(
        "INSERT INTO public.knowledge_points (subject_id,name,status,sort_order) "
        "VALUES (:s,:n,'active',0) RETURNING id"
    ), {"s": subject_id, "n": KP_TWO})).scalar_one()
    await session.commit()
    return {"subject_id": int(subject_id), "kp1": int(kp1), "kp2": int(kp2)}


async def seed_matrix_notes(session: AsyncSession, foundation: dict) -> dict[str, uuid.UUID]:
    ids: dict[str, uuid.UUID] = {}
    for key, status, hidden, next_review, _expected in CELLS:
        note_id = uuid.uuid4()
        my_answer = LEAK_MARKER if key == "published_visible" else f"my-answer-{key}"
        await session.execute(text(
            "INSERT INTO public.notes ("
            "id,slug,title,content,type,status,hidden,subject,difficulty,"
            "question,my_answer,correct_answer,analysis,knowledge_points,"
            "ef,interval,repetitions,next_review,ai_metadata,revision"
            ") VALUES ("
            ":id,:slug,:title,:content,'mistake',:status,:hidden,:subject,'easy',"
            ":question,:my_answer,'A',:analysis,:kp,"
            "2.5,3,5,:next_review,CAST(:meta AS json),1)"
        ), {
            "id": note_id,
            "slug": f"pr09-verify-{key}",
            "title": f"Verify fixture {key}",
            "content": f"Content for {key}",
            "status": status,
            "hidden": hidden,
            "subject": SUBJECT_NAME,
            "question": "2 + 2 = ?",
            "my_answer": my_answer,
            "analysis": f"analysis-{key}",
            "kp": KP_ONE,
            "next_review": next_review,
            "meta": note_ai_metadata(),
        })
        ids[key] = note_id
    await session.commit()
    return ids


async def counts(session: AsyncSession) -> dict[str, int]:
    out = {}
    for table in ("notes", "mistakes", "legacy_note_migrations", "review_items", "questions", "draft_items"):
        out[table] = int((await session.execute(
            text(f"SELECT count(*) FROM public.{table}")
        )).scalar() or 0)
    out["notes_mistake"] = int((await session.execute(
        text("SELECT count(*) FROM public.notes WHERE type='mistake'")
    )).scalar() or 0)
    return out


async def main() -> int:
    url = os.environ.get("DATABASE_URL", "")
    if "astra_week3_pr09_" not in url:
        print("FAIL: must run via week3-scratch-guard with astra_week3_pr09_* database")
        return 2

    from app.services.wk3_mistake_visibility_migration import (
        MAPPING_VERSION,
        run_wk3_migration,
        write_report,
    )

    engine = create_async_engine(url, poolclass=None)
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    try:
        # --------------------------------------------------------------
        # 0. foundation + 4-cell rich seeds
        # --------------------------------------------------------------
        async with maker() as session:
            foundation = await seed_foundation(session)
            note_ids = await seed_matrix_notes(session, foundation)
            before = await counts(session)
        check(before["notes_mistake"] == 4, "seeded 4 legacy mistake notes", str(before))
        check(before["legacy_note_migrations"] == 0, "ledger empty before run")
        check(before["mistakes"] == 0, "mistakes empty before run")

        # --------------------------------------------------------------
        # 1. dry-run zero persistence
        # --------------------------------------------------------------
        async with maker() as session:
            report = await run_wk3_migration(session, dry_run=True)
            await session.rollback()
            dry_json = report.to_json_dict()
            after_dry = await counts(session)
        write_json("wk3-dry-run-report", dry_json)
        check(report.dry_run is True, "dry_run flag set")
        check(after_dry["legacy_note_migrations"] == before["legacy_note_migrations"],
              "dry-run leaves ledger row count unchanged (0)", str(after_dry))
        check(after_dry["mistakes"] == before["mistakes"],
              "dry-run leaves mistakes count unchanged (0)", str(after_dry))
        check(after_dry["review_items"] == before["review_items"],
              "dry-run leaves review_items unchanged", str(after_dry))
        check(dry_json["source"]["total_legacy_mistakes"] == 4, "dry-run source total=4", str(dry_json["source"]))
        check(dry_json["targets"]["created"] == 4, "dry-run plans 4 creations", str(dry_json["targets"]))

        # --------------------------------------------------------------
        # 2. full 4-cell e2e
        # --------------------------------------------------------------
        async with maker() as session:
            report1 = await run_wk3_migration(session, dry_run=False)
            await session.commit()
            run_json = report1.to_json_dict()
            after_run = await counts(session)
        write_json("wk3-run-report", run_json)

        by_mapping = run_json["source"]["by_mapping"]
        check(by_mapping == {
            "published_visible": 1,
            "published_hidden": 1,
            "unpublished_visible": 1,
            "unpublished_hidden": 1,
        }, "source matrix covers all 4 cells", str(by_mapping))
        check(run_json["targets"]["created"] == 4, "targets.created=4", str(run_json["targets"]))
        check(run_json["targets"]["rejected"] == [], "no rejections", str(run_json["targets"]["rejected"]))
        check(run_json["checks"]["count_match"] is True, "count_match true (source=created+skipped+rejected)",
              str(run_json["source"]["total_legacy_mistakes"]))
        check(run_json["unmapped_source_fields"] == ["ef", "interval", "repetitions", "last_reviewed"],
              "unmapped ef/interval/repetitions/last_reviewed", str(run_json["unmapped_source_fields"]))

        # visibility matrix on canonical Mistake rows
        async with maker() as session:
            rows = (await session.execute(text(
                "SELECT n.slug, n.status AS src_status, n.hidden, m.visibility, m.status AS dst_status, "
                "m.my_answer, m.id AS mistake_id, ri.id AS review_id, ri.algorithm, ri.interval_days, "
                "ri.repetitions, ri.next_review_at, l.source_note_id, l.mapping_version, l.state "
                "FROM public.notes n "
                "JOIN public.legacy_note_migrations l ON l.source_note_id = n.id "
                "JOIN public.mistakes m ON m.id = l.target_mistake_id "
                "LEFT JOIN public.review_items ri ON ri.id = l.target_review_item_id "
                "WHERE n.type='mistake' ORDER BY n.slug"
            ))).mappings().all()
        write_sql_log(
            "visibility-matrix",
            "\n".join(str(dict(r)) for r in rows) + "\n",
        )
        check(len(rows) == 4, "4 provenance-linked canonical mistakes", str(len(rows)))
        seen_cells = set()
        next_due_matches = 0
        next_due_default = 0
        for row in rows:
            slug = row["slug"]
            key = slug.replace("pr09-verify-", "")
            expected_vis = dict((c[0], c[4]) for c in CELLS)[key]
            check(row["visibility"] == expected_vis,
                  f"{key} visibility == W3-D06 ({expected_vis})", str(row["visibility"]))
            check(row["dst_status"] == "active", f"{key} canonical status=active (learning lifecycle)", str(row["dst_status"]))
            check(row["mapping_version"] == MAPPING_VERSION, f"{key} ledger mapping_version", str(row["mapping_version"]))
            check(row["source_note_id"] == note_ids[key], f"{key} provenance source_note_id matches seed")
            check(row["algorithm"] == "fixed_interval_v2", f"{key} ReviewItem algorithm v2", str(row["algorithm"]))
            check(int(row["interval_days"]) == 0 and int(row["repetitions"]) == 0,
                  f"{key} ef/interval/repetitions NOT copied from legacy SM-2",
                  f"interval_days={row['interval_days']} repetitions={row['repetitions']}")
            if key == "published_visible":
                check(row["my_answer"] and LEAK_MARKER in str(row["my_answer"]),
                      "private my_answer retained on canonical row")
            cell = key
            seen_cells.add(cell)
            src_next = dict((c[0], c[3]) for c in CELLS)[key]
            if src_next is not None:
                # W3-D08: next_review -> next_due. Record actual behaviour.
                actual = row["next_review_at"]
                match = actual is not None and actual.date() == src_next
                if match:
                    next_due_matches += 1
                else:
                    next_due_default += 1
                    check(False, f"{key} next_due equals source next_review {src_next}",
                          f"actual={actual}")
            else:
                if row["next_review_at"] is not None:
                    next_due_default += 1
        check(seen_cells == {"published_visible", "published_hidden", "unpublished_visible", "unpublished_hidden"},
              "all 4 W3-D06 cells asserted")
        write_sql_log("next-due-mapping", f"next_due_matches_source={next_due_matches} next_due_other={next_due_default}\n")

        # --------------------------------------------------------------
        # 3. v1-* already-migrated target visibility reconcile
        # --------------------------------------------------------------
        v1_note = uuid.uuid4()
        v1_actors = [uuid.uuid4() for _ in range(4)]
        async with maker() as session:
            await session.execute(text(
                "INSERT INTO public.notes ("
                "id,slug,title,content,type,status,hidden,subject,difficulty,"
                "question,my_answer,correct_answer,analysis,knowledge_points,"
                "ef,interval,repetitions,next_review,ai_metadata,revision"
                ") VALUES ("
                ":id,'pr09-verify-v1-target','V1 target','c','mistake','published',false,:subject,'easy',"
                "'2 + 2 = ?','v1-my','A','v1-an',:kp,2.5,3,5,NULL,CAST(:meta AS json),1)"
            ), {"id": v1_note, "subject": SUBJECT_NAME, "kp": KP_TWO, "meta": note_ai_metadata()})
            for actor in v1_actors:
                await session.execute(text(
                    "INSERT INTO public.users (id,username,password_hash,is_admin) "
                    "VALUES (:id,:name,'!',false) ON CONFLICT (id) DO NOTHING"
                ), {"id": actor, "name": f"pr09-v1-actor-{actor.hex[:8]}"})
            await session.commit()

        async with maker() as session:
            from app.services.legacy_note_migration_adapter import migrate

            await session.execute(text("SET SESSION AUTHORIZATION legacy_note_adapter_runner"))
            try:
                payload = (await session.execute(text(
                    "SELECT legacy_migration.canonicalize_legacy_note(:id)"
                ), {"id": v1_note})).scalar_one()
                source_hash = (await session.execute(text(
                    "SELECT encode(public.digest(convert_to(legacy_migration.canonicalize_legacy_note(:id)::text,'UTF8'),'sha256'),'hex')"
                ), {"id": v1_note})).scalar_one()
                await session.commit()
                v1_result = await migrate(
                    session,
                    source_note_id=v1_note,
                    mapping_version="v1-verify-baseline",
                    source_approved_by=v1_actors[0],
                    source_approved_at=datetime.now(timezone.utc),
                    source_approval_sequence=1,
                    question_conversion_approved_by=v1_actors[1],
                    question_conversion_approved_at=datetime.now(timezone.utc),
                    question_conversion_sequence=1,
                    mistake_conversion_approved_by=v1_actors[2],
                    mistake_conversion_approved_at=datetime.now(timezone.utc),
                    mistake_conversion_sequence=1,
                    canonical_payload=payload,
                    expected_source_hash=source_hash,
                    schedule_approved_by=v1_actors[3],
                    schedule_approved_at=datetime.now(timezone.utc),
                    schedule_approval_sequence=1,
                    mapped_next_review_at=datetime.now(timezone.utc),
                )
            finally:
                await session.execute(text("RESET SESSION AUTHORIZATION"))
            await session.commit()
            v1_mistake_id = uuid.UUID(str(v1_result.target_mistake_id))
            # force visibility away from the W3-D06 expectation so the UPDATE is observable
            await session.execute(text(
                "UPDATE public.mistakes SET visibility='private', version=version+1 WHERE id=:id"
            ), {"id": v1_mistake_id})
            # and capture pre-image for field-identity assertion
            pre = (await session.execute(text(
                "SELECT title, question_text, my_answer, correct_answer, analysis, status, version "
                "FROM public.mistakes WHERE id=:id"
            ), {"id": v1_mistake_id})).mappings().one()
            pre_image = dict(pre)
            ledger_before_reconcile = int((await session.execute(text(
                "SELECT count(*) FROM public.legacy_note_migrations"
            )).scalar_one()))
            await session.commit()

        async with maker() as session:
            report2 = await run_wk3_migration(session, dry_run=False)
            await session.commit()
            rec_json = report2.to_json_dict()
        write_json("wk3-v1-reconcile-report", rec_json)

        async with maker() as session:
            post = (await session.execute(text(
                "SELECT title, question_text, my_answer, correct_answer, analysis, status, version, visibility "
                "FROM public.mistakes WHERE id=:id"
            ), {"id": v1_mistake_id})).mappings().one()
            post_image = dict(post)
            ledger_after_reconcile = int((await session.execute(text(
                "SELECT count(*) FROM public.legacy_note_migrations"
            )).scalar_one()))
            wk3_rows_for_v1 = int((await session.execute(text(
                "SELECT count(*) FROM public.legacy_note_migrations "
                "WHERE source_note_id=:src AND mapping_version=:mv"
            ), {"src": v1_note, "mv": MAPPING_VERSION})).scalar_one())
            v1_target_rows = int((await session.execute(text(
                "SELECT count(*) FROM public.legacy_note_migrations WHERE source_note_id=:src"
            ), {"src": v1_note})).scalar_one())
            mistake_count_now = int((await session.execute(text(
                "SELECT count(*) FROM public.mistakes"
            )).scalar_one()))

        check(post_image["visibility"] == "public",
              "v1-* target visibility reconciled to public (W3-D06)", str(post_image["visibility"]))
        for field in ("title", "question_text", "my_answer", "correct_answer", "analysis", "status"):
            check(post_image[field] == pre_image[field],
                  f"v1 reconcile leaves {field} unchanged (UPDATE visibility only)")
        check(wk3_rows_for_v1 == 0,
              "no new wk3 ledger target row for v1-migrated source", str(wk3_rows_for_v1))
        check(v1_target_rows == 1, "only the original v1 ledger row for that source", str(v1_target_rows))
        check(ledger_after_reconcile == ledger_before_reconcile,
              "ledger row count unchanged by reconcile run",
              f"{ledger_before_reconcile}->{ledger_after_reconcile}")
        check(rec_json["targets"]["visibility_reconciled"] >= 1,
              "report counts visibility_reconciled", str(rec_json["targets"]))
        check(mistake_count_now == 5, "no duplicate mistakes created (4 matrix + 1 v1)", str(mistake_count_now))

        # --------------------------------------------------------------
        # 4. idempotent replay
        # --------------------------------------------------------------
        async with maker() as session:
            report3 = await run_wk3_migration(session, dry_run=False)
            await session.commit()
            replay_json = report3.to_json_dict()
        write_json("wk3-replay-report", replay_json)
        check(replay_json["targets"]["created"] == 0, "replay targets.created=0", str(replay_json["targets"]))
        check(replay_json["targets"]["visibility_reconciled"] == 0,
              "replay visibility_reconciled is no-op (0)", str(replay_json["targets"]))
        check(replay_json["idempotency"]["replay_noop"] is True, "idempotency.replay_noop=true",
              str(replay_json["idempotency"]))
        check(replay_json["checks"]["replay_noop"] is True, "checks.replay_noop=true")
        check(replay_json["targets"]["skipped_already_migrated"] + replay_json["targets"][
            "skipped_already_migrated_private_ok"] >= 5,
              "all sources skipped on replay", str(replay_json["targets"]))

        # --------------------------------------------------------------
        # 5. changed-source conflict behaviour (record actual)
        # --------------------------------------------------------------
        async with maker() as session:
            await session.execute(text(
                "UPDATE public.notes SET content='CHANGED AFTER MIGRATION', revision=revision+1 "
                "WHERE id=:id"
            ), {"id": note_ids["published_visible"]})
            await session.commit()

        async with maker() as session:
            report4 = await run_wk3_migration(session, dry_run=False)
            await session.commit()
            conflict_json = report4.to_json_dict()
        write_json("wk3-changed-source-report", conflict_json)

        async with maker() as session:
            after_change = (await session.execute(text(
                "SELECT m.question_text, m.my_answer, m.visibility, l.source_hash, l.state "
                "FROM public.legacy_note_migrations l JOIN public.mistakes m ON m.id=l.target_mistake_id "
                "WHERE l.source_note_id=:id"
            ), {"id": note_ids["published_visible"]})).mappings().one()
            await session.execute(text("SET SESSION AUTHORIZATION legacy_note_adapter_runner"))
            try:
                live_hash = (await session.execute(text(
                    "SELECT encode(public.digest(convert_to(legacy_migration.canonicalize_legacy_note(:id)::text,'UTF8'),'sha256'),'hex')"
                ), {"id": note_ids["published_visible"]})).scalar_one()
            finally:
                await session.execute(text("RESET SESSION AUTHORIZATION"))
        write_sql_log("changed-source-conflict", json.dumps({
            "behaviour": "recorded",
            "replay_after_source_change": conflict_json,
            "ledger_source_hash": str(after_change["source_hash"]),
            "live_source_hash": live_hash,
            "hash_drift": str(after_change["source_hash"]) != live_hash,
            "canonical_mistake_unchanged_visibility": after_change["visibility"],
        }, indent=2, default=str))
        check(conflict_json["idempotency"]["replay_noop"] is True,
              "changed source: replay stays no-op (terminal ledger, visibility-only path)",
              str(conflict_json["idempotency"]))
        check(str(after_change["source_hash"]) != live_hash,
              "changed source: ledger source_hash now differs from live (drift recorded)")
        # design says events go to reconciliation report rather than new ledger rows
        check(conflict_json["targets"]["created"] == 0, "changed source: no new targets created")

        write_sql_log("ledger-counts", json.dumps({
            "before": before, "after_dry": after_dry, "after_run": after_run,
            "final_mistakes": mistake_count_now,
            "ledger_before_reconcile": ledger_before_reconcile,
            "ledger_after_reconcile": ledger_after_reconcile,
        }, indent=2, default=str))

        summary = "ALL_PASS" if not FAILURES else f"FAILURES={len(FAILURES)}"
        write_sql_log("ledger-summary", summary + "\n" + "\n".join(FAILURES) + "\n")
        print(f"LEDGER_MATRIX_{summary}")
        return 0 if not FAILURES else 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
