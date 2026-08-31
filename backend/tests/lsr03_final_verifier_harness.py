"""Task-local LSR-03 verifier probes; never part of application runtime."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


SOURCE_ACTOR = "11111111-1111-4111-8111-111111111111"
QUESTION_ACTOR = "22222222-2222-4222-8222-222222222222"
MISTAKE_ACTOR = "33333333-3333-4333-8333-333333333333"
ROLLBACK_BASELINE_SOURCE = "44444444-4444-4444-8444-444444444445"
SCHEDULE_ACTOR = "66666666-6666-4666-8666-666666666666"
SYNTHETIC_OPTIONS = ({"key": "A", "text": "4"}, {"key": "B", "text": "3"})
SYNTHETIC_MY_ANSWER = "B"
SYNTHETIC_CORRECT_ANSWER = "A"
PRE026_RESTORE_SENTINEL = "77777777-7777-4777-8777-777777777777"
PRE026_SENTINEL_SLUG = "lsr03-pre026-restore-sentinel"
POSITIVE_SOURCE_PAIRS = (
    ("88888888-8888-4888-8888-888888888888", "v1-active", "migrated_active"),
    ("33333333-3333-4333-8333-333333333334", "v1-paused", "migrated_paused"),
    ("22222222-2222-4222-8222-222222222223", "v1-retained", "retained_public_only"),
    ("90000000-0000-4000-8000-000000000019", "v1-chapter-019", "migrated_paused"),
)


def _positive_expected_values_sql() -> str:
    return ",\n".join(
        f"('{source}'::uuid,'{mapping}','{state}'::public.legacy_note_migration_state)"
        for source, mapping, state in POSITIVE_SOURCE_PAIRS
    )


def _allowed_ledger_pairs_sql() -> str:
    return (
        "SELECT source_note_id,mapping_version FROM expected\n"
        "UNION ALL\n"
        f"VALUES ('{ROLLBACK_BASELINE_SOURCE}'::uuid,'v1-paused')"
    )


def _url(raw: str, role: str | None = None) -> str:
    parsed = urlsplit(raw)
    user = role or parsed.username or "fixture_admin"
    return urlunsplit((parsed.scheme, f"{user}@{parsed.hostname}:{parsed.port}", parsed.path, "", ""))


async def _engine(raw: str, role: str | None = None):
    from sqlalchemy.ext.asyncio import create_async_engine

    return create_async_engine(_url(raw, role), poolclass=None)


async def seed_extended(raw: str) -> dict[str, object]:
    """Add synthetic active/paused/public/chapter source Notes only."""
    from sqlalchemy import text

    engine = await _engine(raw)
    rows = (
        ("88888888-8888-4888-8888-888888888888", "lsr03-active-extra", "active", "published", True),
        ("33333333-3333-4333-8333-333333333334", "lsr03-paused-extra", "paused", "published", True),
        ("22222222-2222-4222-8222-222222222223", "lsr03-retained-public", "retained", "published", False),
        ("90000000-0000-4000-8000-000000000019", "lsr03-chapter-019", "chapter", "draft", True),
    )
    # Keep the canonical JSON shape valid while making this public source
    # deliberately unmappable: the mapper's closed QUESTION_INVALID branch
    # must produce retained_public_only, not a paused target chain.
    question_by_label = {"active": "2 + 2 = ?", "paused": "2 + 2 = ?", "retained": "", "chapter": "2 + 2 = ?"}
    try:
        async with engine.begin() as c:
            await c.execute(text("""
              INSERT INTO public.users(id,username,password_hash,is_admin)
              VALUES (:id,:username,'lsr03-fixture',true)
              ON CONFLICT (id) DO NOTHING
            """), {"id": SCHEDULE_ACTOR, "username": "lsr03_schedule"})
            await c.execute(text("""
              INSERT INTO public.legacy_migration_approval_authorizations(user_id,approval_kind,enabled)
              VALUES (:id,'schedule',true)
              ON CONFLICT (user_id,approval_kind) DO UPDATE SET enabled=true
            """), {"id": SCHEDULE_ACTOR})
            schedule_authorized = bool(await c.scalar(text("""
              SELECT enabled
                FROM public.legacy_migration_approval_authorizations
               WHERE user_id=:id AND approval_kind='schedule' AND enabled
            """), {"id": SCHEDULE_ACTOR}))
            for note_id, slug, label, status, hidden in rows:
                await c.execute(text("""
                  INSERT INTO public.notes(
                    id,slug,title,content,type,status,hidden,summary,subject,difficulty,
                    question,my_answer,correct_answer,analysis,knowledge_points,ef,interval,repetitions,
                    ai_metadata,revision
                  ) VALUES (
                    :id,:slug,:title,:content,'mistake',:status,:hidden,'LSR03 fixture','LSR03 R4 Subject','easy',
                    :question, :my_answer, :correct_answer, :analysis, 'LSR03 R4 KP', 2.5, 0, 0,
                    CAST(:metadata AS json), 1
                  ) ON CONFLICT (id) DO NOTHING
                """), {
                    "id": note_id, "slug": slug, "title": f"LSR03 {label}",
                    "content": f"Synthetic LSR-03 {label} source", "status": status,
                    "hidden": hidden, "analysis": f"Synthetic {label} analysis",
                    "question": question_by_label[label],
                    "my_answer": SYNTHETIC_MY_ANSWER, "correct_answer": SYNTHETIC_CORRECT_ANSWER,
                    "metadata": '{"legacy_question":{"question_type":"single_choice","options":[{"key":"A","text":"4"},{"key":"B","text":"3"}]}}',
                })
            count = await c.scalar(text("SELECT count(*) FROM public.notes WHERE id IN ('88888888-8888-4888-8888-888888888888','33333333-3333-4333-8333-333333333334','22222222-2222-4222-8222-222222222223','90000000-0000-4000-8000-000000000019')"))
        return {"extended_source_notes": int(count or 0), "schedule_authorized": schedule_authorized}
    finally:
        await engine.dispose()


async def introspect(raw: str) -> dict[str, object]:
    from sqlalchemy import text

    engine = await _engine(raw)
    try:
        async with engine.connect() as c:
            identity = dict((await c.execute(text("""
              SELECT current_database() AS database, inet_server_addr()::text AS server_addr,
                     inet_server_port() AS server_port, current_user, session_user,
                     pg_is_in_recovery() AS recovery
            """))).mappings().one())
            tables = [r[0] for r in (await c.execute(text("""
              SELECT table_name FROM information_schema.tables
              WHERE table_schema='public' AND table_name LIKE 'legacy_%'
              ORDER BY table_name
            """))).all()]
            functions = [dict(r) for r in (await c.execute(text("""
              SELECT n.nspname AS schema, p.proname AS name,
                     pg_get_function_identity_arguments(p.oid) AS args,
                     p.prosecdef AS security_definer, r.rolname AS owner
              FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
              JOIN pg_roles r ON r.oid=p.proowner
              WHERE n.nspname='legacy_migration'
              ORDER BY p.proname, args
            """))).mappings().all()]
            acl = [dict(r) for r in (await c.execute(text("""
              SELECT c.relname, r.rolname AS owner,
                     has_table_privilege('legacy_note_verifier',c.oid,'SELECT') AS verifier_select,
                     has_table_privilege('app_role',c.oid,'INSERT') AS app_insert,
                     has_table_privilege('legacy_note_adapter_runner',c.oid,'INSERT') AS runner_insert
              FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
              JOIN pg_roles r ON r.oid=c.relowner
              WHERE n.nspname='public' AND c.relname LIKE 'legacy_%' AND c.relkind='r'
              ORDER BY c.relname
            """))).mappings().all()]
            checks = [dict(r) for r in (await c.execute(text("""
              SELECT conrelid::regclass::text AS relation, conname, pg_get_constraintdef(oid) AS definition
              FROM pg_constraint
              WHERE connamespace='public'::regnamespace AND conname LIKE '%legacy%'
              ORDER BY relation, conname
            """))).mappings().all()]
            revision = await c.scalar(text("SELECT version_num FROM alembic_version"))
        result = {"identity": identity, "revision": revision, "legacy_tables": tables,
                  "function_count": len(functions), "functions": functions,
                  "acl": acl, "retained_or_legacy_checks": checks}
        print(json.dumps(result, default=str, sort_keys=True))
        return result
    finally:
        await engine.dispose()


async def _pre026_sentinel_snapshot(raw: str) -> dict[str, object]:
    """Return a deterministic ordinary-Note sentinel identity/count/hash."""
    from sqlalchemy import text

    engine = await _engine(raw)
    try:
        async with engine.connect() as c:
            row = (await c.execute(text("""
              SELECT count(*) AS rowcount,
                     (array_agg(id::text))[1] AS id,
                     max(slug) AS slug,
                     max(type) AS type,
                     max(status) AS status,
                     bool_and(hidden) AS hidden,
                     md5(convert_to(COALESCE((
                       SELECT jsonb_build_object(
                         'id',n.id,'slug',n.slug,'title',n.title,'content',n.content,
                         'type',n.type,'status',n.status,'hidden',n.hidden,
                         'created_at',to_char(n.created_at,'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                         'updated_at',to_char(n.updated_at,'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                         'question',n.question,'my_answer',n.my_answer,'correct_answer',n.correct_answer,
                         'analysis',n.analysis,'ef',n.ef,'interval',n.interval,
                         'repetitions',n.repetitions,'revision',n.revision
                       )::text
                       FROM public.notes n WHERE n.id=CAST(:id AS uuid)
                     ),'{}'),'UTF8')) AS row_hash,
                     md5(convert_to(jsonb_build_object(
                       'id',CAST(:id AS uuid),'slug',CAST(:slug AS text),'title','LSR03 pre026 sentinel',
                       'content','LSR03 pre026 ordinary Note sentinel','type','note',
                       'status','published','hidden',false,'created_at','2026-01-02T03:04:05.000000Z',
                       'updated_at','2026-01-02T03:04:05.000000Z','question',NULL,
                       'my_answer',NULL,'correct_answer',NULL,'analysis','pre026 restore sentinel',
                       'ef',2.5,'interval',0,'repetitions',0,'revision',1
                     )::text,'UTF8')) AS expected_hash
                FROM public.notes
               WHERE id=CAST(:id AS uuid)
            """), {"id": PRE026_RESTORE_SENTINEL, "slug": PRE026_SENTINEL_SLUG})).mappings().one()
        result = dict(row)
        result["sentinel_id"] = PRE026_RESTORE_SENTINEL
        result["sentinel_slug"] = PRE026_SENTINEL_SLUG
        return result
    finally:
        await engine.dispose()


async def seed_pre026_restore_sentinel(raw: str) -> dict[str, object]:
    """Write one fixed ordinary Note before the 026 dump, then report its hash."""
    from sqlalchemy import text

    engine = await _engine(raw)
    try:
        async with engine.begin() as c:
            await c.execute(text("""
              INSERT INTO public.notes(
                id,slug,title,content,type,status,hidden,question,my_answer,correct_answer,
                analysis,ef,interval,repetitions,revision,created_at,updated_at
              ) VALUES (
                :id,:slug,'LSR03 pre026 sentinel','LSR03 pre026 ordinary Note sentinel',
                'note','published',false,NULL,NULL,NULL,'pre026 restore sentinel',2.5,0,0,1,
                TIMESTAMP '2026-01-02 03:04:05',TIMESTAMP '2026-01-02 03:04:05'
              ) ON CONFLICT (id) DO NOTHING
            """), {"id": PRE026_RESTORE_SENTINEL, "slug": PRE026_SENTINEL_SLUG})
        result = await _pre026_sentinel_snapshot(raw)
        if result["rowcount"] != 1 or result["id"] != PRE026_RESTORE_SENTINEL:
            raise AssertionError(f"PRE026_SENTINEL_WRITE_MISMATCH:{result}")
        result["operation"] = "seed_pre026_restore_sentinel"
        print(json.dumps(result, default=str, sort_keys=True))
        return result
    finally:
        await engine.dispose()


async def verify_pre026_restore_sentinel(raw: str) -> dict[str, object]:
    """Verify the sentinel survived restore and no revision-026 object survived."""
    from sqlalchemy import text

    result = await _pre026_sentinel_snapshot(raw)
    engine = await _engine(raw)
    try:
        async with engine.connect() as c:
            shape = dict((await c.execute(text("""
              SELECT to_regclass('public.legacy_note_migrations') IS NULL AS ledger_absent,
                     NOT EXISTS (SELECT 1 FROM pg_catalog.pg_namespace WHERE nspname='legacy_migration') AS schema_absent,
                     COALESCE((SELECT bool_and(version_num='025') FROM public.alembic_version), false) AS revision_025_exact,
                     COALESCE((SELECT bool_and(version_num <> '026_legacy_system_retirement')
                               FROM public.alembic_version), true) AS revision_026_absent
            """))).mappings().one())
        checks = {
            "sentinel_count_exact": result["rowcount"] == 1,
            "sentinel_id_exact": result["id"] == PRE026_RESTORE_SENTINEL,
            "sentinel_slug_exact": result["slug"] == PRE026_SENTINEL_SLUG,
            "sentinel_hash_exact": result["row_hash"] == result["expected_hash"],
            "revision_025_exact_and_026_objects_absent": all(shape.values()),
        }
        evidence = {"operation": "verify_pre026_restore_sentinel", "sentinel": result,
                    "shape": shape, "checks": checks, "pass": all(checks.values())}
        if not evidence["pass"]:
            raise AssertionError(f"PRE026_RESTORE_SENTINEL_VERIFY_FAILED:{evidence}")
        print(json.dumps(evidence, default=str, sort_keys=True))
        return evidence
    finally:
        await engine.dispose()


async def verify_positive(raw: str) -> dict[str, object]:
    """Verify only the four synthetic positive sources, returning one JSON object."""
    from sqlalchemy import text

    # This query intentionally does not call the owner-only source helper:
    # that helper is adapter-only.  The verifier rebuilds the same canonical
    # JSON from locked, scoped live rows and compares the digest independently.
    verification_sql = f"""
      WITH expected(source_note_id,mapping_version,expected_state) AS (
        VALUES
          {_positive_expected_values_sql()}
      ),
      allowed_pairs(source_note_id,mapping_version) AS (
        {_allowed_ledger_pairs_sql()}
      ),
      actual_pairs AS (
        SELECT source_note_id,mapping_version,count(*) AS row_count
          FROM public.legacy_note_migrations
         GROUP BY source_note_id,mapping_version
      ),
      ledgers AS (
        SELECT l.*
          FROM public.legacy_note_migrations l
          JOIN expected e ON e.source_note_id=l.source_note_id
                           AND e.mapping_version=l.mapping_version
      ),
      source_payload AS (
        SELECT n.id AS source_note_id,
               jsonb_build_object(
                 'id',n.id,'source_note_id',n.id,'slug',n.slug,
                 'source_url','/notes/'||n.slug,'title',n.title,'content',n.content,
                 'type',n.type,'status',n.status,'hidden',n.hidden,
                 'created_at',to_char(n.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                 'updated_at',to_char(n.updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                 'summary',n.summary,'cover',n.cover,'category',n.category,
                 'subject',n.subject,'difficulty',n.difficulty,
                 'subject_id',(SELECT s.id FROM public.subjects s WHERE lower(s.name)=lower(n.subject)),
                 'question',n.question,
                 'question_type',n.ai_metadata::jsonb->'legacy_question'->>'question_type',
                 'options',COALESCE(n.ai_metadata::jsonb->'legacy_question'->'options','null'::jsonb),
                 'answers',jsonb_build_object('my_answer',n.my_answer,'correct_answer',n.correct_answer),
                 'analysis',n.analysis,
                 'knowledge_points',COALESCE((SELECT jsonb_agg(trim(k.value) ORDER BY k.ordinality)
                   FROM regexp_split_to_table(replace(replace(replace(replace(COALESCE(n.knowledge_points,''),'，',','),'、',','),E'\n',','),'；',','),',')
                   WITH ORDINALITY AS k(value,ordinality) WHERE trim(k.value)<>''),'[]'::jsonb),
                 'ef',n.ef,'legacy_ef_bits',encode(float8send(n.ef),'hex'),
                 'interval',n.interval,'repetitions',n.repetitions,
                 'next_review',to_char(n.next_review,'YYYY-MM-DD'),
                 'last_reviewed',to_char(n.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                 'images',n.images,'ai_metadata',n.ai_metadata,'folder_id',n.folder_id,
                 'sort_order',n.sort_order,'revision',n.revision,
                 'tags',COALESCE((SELECT jsonb_agg(to_jsonb(t.name) ORDER BY t.id,t.name)
                   FROM public.note_tags nt JOIN public.tags t ON t.id=nt.tag_id
                  WHERE nt.note_id=n.id),'[]'::jsonb),
                 'search_vector_token',CASE WHEN n.search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>'||n.search_vector::text END,
                 'legacy_review_json',jsonb_build_object(
                   'ef',n.ef,'interval',n.interval,'repetitions',n.repetitions,
                   'next_review',to_char(n.next_review,'YYYY-MM-DD'),
                   'last_reviewed',to_char(n.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'))
               ) AS payload,
               n.*
          FROM public.notes n
         WHERE n.id IN (SELECT source_note_id FROM expected)
      ),
      target_rows AS (
        SELECT l.*, e.expected_state,
               qdi.id AS qdi_id, qd.id AS qd_id, q.id AS q_id, qs.id AS qs_id,
               mdi.id AS mdi_id, md.id AS md_id, mi.id AS mi_id, ri.id AS ri_id,
               qdi.source_id AS qdi_source_id, qdi.source_hash AS qdi_hash,
               mdi.source_id AS mdi_source_id, mdi.source_hash AS mdi_hash,
               qd.title AS qd_title, qd.question_text AS qd_question, qd.question_type AS qd_type,
               qd.options AS qd_options, qd.correct_answer AS qd_correct,
               qd.explanation AS qd_explanation, qd.difficulty AS qd_difficulty,
               q.title AS q_title, q.question_text AS q_question, q.question_type AS q_type,
               q.options AS q_options, q.answer_data AS q_answer_data, q.correct_answer AS q_correct,
               q.analysis_md AS q_analysis, q.explanation AS q_explanation, q.difficulty AS q_difficulty,
               q.visibility AS q_visibility,
               md.title AS md_title, md.question_text AS md_question,
               md.my_answer AS md_my_answer, md.correct_answer_snapshot AS md_correct,
               md.explanation_snapshot AS md_explanation, md.difficulty AS md_difficulty,
               mi.title AS mi_title, mi.question_text AS mi_question,
               mi.my_answer AS mi_my_answer, mi.correct_answer AS mi_correct,
               mi.analysis AS mi_analysis, mi.difficulty AS mi_difficulty,
               mi.visibility AS mi_visibility,
               qs.source_title AS qs_title, qs.source_url AS qs_url,
               qs.source_ref AS qs_ref, qs.source_note AS qs_note,
               ri.state AS ri_state, ri.algorithm AS ri_algorithm,
               ri.interval_days AS ri_interval, ri.repetitions AS ri_repetitions,
               ri.next_review_at AS ri_next,
               sp.payload AS live_payload,
               sp.status AS live_status, sp.hidden AS live_hidden,
               sp.slug AS live_slug, sp.title AS live_title,
               sp.revision AS live_revision, sp.content AS live_content
          FROM ledgers l
          JOIN expected e ON e.source_note_id=l.source_note_id AND e.mapping_version=l.mapping_version
          JOIN source_payload sp ON sp.source_note_id=l.source_note_id
          LEFT JOIN public.draft_items qdi ON qdi.id=l.target_question_draft_item_id
          LEFT JOIN public.question_drafts qd ON qd.id=l.target_question_draft_id
          LEFT JOIN public.questions q ON q.id=l.target_question_id
          LEFT JOIN public.question_sources qs ON qs.id=l.target_question_source_id
          LEFT JOIN public.draft_items mdi ON mdi.id=l.target_mistake_draft_item_id
          LEFT JOIN public.mistake_drafts md ON md.id=l.target_mistake_draft_id
          LEFT JOIN public.mistakes mi ON mi.id=l.target_mistake_id
          LEFT JOIN public.review_items ri ON ri.id=l.target_review_item_id
      ),
      duplicate_targets AS (
        SELECT count(*) AS bad
          FROM (
            SELECT target_question_id AS id FROM ledgers WHERE target_question_id IS NOT NULL GROUP BY target_question_id HAVING count(*)>1
            UNION ALL SELECT target_question_source_id FROM ledgers WHERE target_question_source_id IS NOT NULL GROUP BY target_question_source_id HAVING count(*)>1
            UNION ALL SELECT target_mistake_id FROM ledgers WHERE target_mistake_id IS NOT NULL GROUP BY target_mistake_id HAVING count(*)>1
            UNION ALL SELECT target_review_item_id FROM ledgers WHERE target_review_item_id IS NOT NULL GROUP BY target_review_item_id HAVING count(*)>1
          ) duplicates
      ),
      counts AS (
        SELECT
          (SELECT count(*) FROM expected) AS expected_count,
          (SELECT count(*) FROM ledgers) AS ledger_count,
          (SELECT count(*) FROM public.legacy_note_migrations) AS actual_ledger_row_count,
          (SELECT count(*) FROM allowed_pairs) AS allowed_pair_count,
          (SELECT count(*) FROM actual_pairs) AS actual_pair_count,
          (SELECT count(*) FROM actual_pairs a
             WHERE a.row_count<>1) AS duplicate_pair_count,
          (SELECT count(*) FROM public.legacy_note_migrations l
             WHERE NOT EXISTS (
               SELECT 1 FROM allowed_pairs a
                WHERE a.source_note_id=l.source_note_id AND a.mapping_version=l.mapping_version
             )) AS extra_ledger_count,
          (SELECT count(*) FROM (
             (SELECT source_note_id,mapping_version FROM actual_pairs
              EXCEPT
              SELECT source_note_id,mapping_version FROM allowed_pairs)
             UNION ALL
             (SELECT source_note_id,mapping_version FROM allowed_pairs
              EXCEPT
              SELECT source_note_id,mapping_version FROM actual_pairs)
          ) pair_mismatch) AS allowed_pair_mismatch_count,
          (SELECT count(*) FROM target_rows t WHERE t.state IS DISTINCT FROM t.expected_state) AS state_mismatch,
          (SELECT count(*) FROM target_rows t WHERE t.expected_state IN ('migrated_active','migrated_paused') AND (
             t.qdi_id IS NULL OR t.qd_id IS NULL OR t.q_id IS NULL OR t.qs_id IS NULL OR
             t.mdi_id IS NULL OR t.md_id IS NULL OR t.mi_id IS NULL OR
             (t.expected_state='migrated_active' AND t.ri_id IS NULL) OR
             (t.expected_state='migrated_paused' AND t.ri_id IS NOT NULL) OR
             t.qdi_source_id IS DISTINCT FROM t.source_note_id::text OR t.qdi_hash IS DISTINCT FROM t.source_hash OR
             t.mdi_source_id IS DISTINCT FROM t.q_id::text OR t.mdi_hash IS DISTINCT FROM t.source_hash OR
             t.qd_title IS DISTINCT FROM t.live_title OR t.qd_question IS DISTINCT FROM t.q_question OR
             t.qd_type IS DISTINCT FROM 'single_choice' OR t.qd_options::jsonb IS DISTINCT FROM t.canonical_payload->'options' OR
             t.q_options::jsonb IS DISTINCT FROM t.canonical_payload->'options' OR
             t.q_options::jsonb IS DISTINCT FROM t.live_payload->'options' OR
             t.qd_correct IS DISTINCT FROM t.q_correct OR t.qd_title IS DISTINCT FROM t.live_title OR
             t.qd_explanation IS DISTINCT FROM t.live_payload->>'analysis' OR
             t.qd_difficulty IS DISTINCT FROM t.live_payload->>'difficulty' OR
             t.q_title IS DISTINCT FROM t.live_title OR
             t.q_question IS DISTINCT FROM t.md_question OR t.q_question IS DISTINCT FROM t.mi_question OR
             t.q_correct IS DISTINCT FROM (t.live_payload->'answers'->>'correct_answer') OR
             t.q_answer_data::jsonb IS DISTINCT FROM jsonb_build_object(
               'kind','single_choice','value',jsonb_build_array(t.live_payload->'answers'->>'correct_answer')) OR
             t.q_analysis IS DISTINCT FROM t.live_payload->>'analysis' OR
             t.q_explanation IS DISTINCT FROM t.live_payload->>'analysis' OR
             t.q_difficulty IS DISTINCT FROM t.live_payload->>'difficulty' OR
             t.mi_title IS DISTINCT FROM t.live_title OR t.md_title IS DISTINCT FROM t.live_title OR
             t.md_my_answer IS DISTINCT FROM (t.live_payload->'answers'->>'my_answer') OR
             t.mi_my_answer IS DISTINCT FROM (t.live_payload->'answers'->>'my_answer') OR
             t.md_correct IS DISTINCT FROM (t.live_payload->'answers'->>'correct_answer') OR
             t.mi_correct IS DISTINCT FROM (t.live_payload->'answers'->>'correct_answer') OR
             t.md_explanation IS DISTINCT FROM t.live_payload->>'analysis' OR
             t.md_difficulty IS DISTINCT FROM t.live_payload->>'difficulty' OR
             t.mi_analysis IS DISTINCT FROM t.live_payload->>'analysis' OR
             t.mi_difficulty IS DISTINCT FROM t.live_payload->>'difficulty' OR
             t.q_type IS DISTINCT FROM 'single_choice' OR
             t.q_visibility IS DISTINCT FROM 'private' OR t.mi_visibility IS DISTINCT FROM 'private' OR
             t.qs_title IS DISTINCT FROM t.live_title OR t.qs_url IS DISTINCT FROM ('/notes/'||t.live_slug) OR
             t.qs_ref IS DISTINCT FROM ('legacy-note:'||t.source_note_id::text) OR
             t.qs_note::jsonb->>'source_note_id' IS DISTINCT FROM t.source_note_id::text OR
             t.qs_note::jsonb->>'source_slug' IS DISTINCT FROM t.live_slug OR
             t.qs_note::jsonb->>'source_title' IS DISTINCT FROM t.live_title OR
             t.qs_note::jsonb->>'source_url' IS DISTINCT FROM ('/notes/'||t.live_slug) OR
             t.qs_note::jsonb->>'source_hash' IS DISTINCT FROM t.source_hash OR
             t.qs_note::jsonb->>'mapping_version' IS DISTINCT FROM t.mapping_version OR
             t.qs_note::jsonb->>'source_revision' IS DISTINCT FROM t.source_revision::text
          )) AS target_parity_mismatch,
          (SELECT count(*) FROM target_rows t WHERE t.expected_state='migrated_active' AND (
             t.ri_state IS DISTINCT FROM 'active' OR t.ri_algorithm IS DISTINCT FROM 'fixed_interval_v1' OR
             t.ri_interval IS DISTINCT FROM t.legacy_interval OR t.ri_repetitions IS DISTINCT FROM t.legacy_repetitions OR
             t.ri_next IS DISTINCT FROM t.mapped_next_review_at OR t.mapped_next_review_at IS NULL OR t.manual_review_required IS DISTINCT FROM false
          )) AS active_review_mismatch,
          (SELECT count(*) FROM target_rows t WHERE t.expected_state='migrated_paused' AND (
             t.ri_id IS NOT NULL OR t.mapped_next_review_at IS NOT NULL OR t.manual_review_required IS DISTINCT FROM true
          )) AS paused_review_mismatch,
          (SELECT count(*) FROM target_rows t WHERE t.expected_state='retained_public_only' AND (
             t.live_status IS DISTINCT FROM 'published' OR t.live_hidden IS DISTINCT FROM false OR
             t.target_question_draft_item_id IS NOT NULL OR t.target_question_draft_id IS NOT NULL OR
             t.target_question_id IS NOT NULL OR t.target_question_source_id IS NOT NULL OR
             t.target_mistake_draft_item_id IS NOT NULL OR t.target_mistake_draft_id IS NOT NULL OR
             t.target_mistake_id IS NOT NULL OR t.target_review_item_id IS NOT NULL OR
             t.target_qkp_ids IS NOT NULL OR t.target_projection_ids IS NOT NULL
          )) AS retained_mismatch,
          (SELECT count(*) FROM public.review_records rr
             WHERE rr.review_item_id IN (SELECT target_review_item_id FROM ledgers WHERE target_review_item_id IS NOT NULL)) AS review_record_count,
          (SELECT bad FROM duplicate_targets) AS duplicate_count,
          (SELECT count(*) FROM target_rows t WHERE encode(public.digest(convert_to(t.live_payload::text,'UTF8'),'sha256'),'hex') IS DISTINCT FROM t.source_hash) AS source_hash_mismatch,
          (SELECT count(*) FROM target_rows t WHERE t.canonical_payload IS DISTINCT FROM t.live_payload OR
             t.source_slug IS DISTINCT FROM t.live_slug OR t.source_title IS DISTINCT FROM t.live_title OR
             t.source_status IS DISTINCT FROM t.live_status OR t.source_hidden IS DISTINCT FROM t.live_hidden OR t.source_revision IS DISTINCT FROM t.live_revision OR
             t.live_content IS NULL) AS source_field_mismatch,
          (SELECT count(*) FROM target_rows t WHERE t.expected_state IN ('migrated_active','migrated_paused') AND (
             t.qdi_id IS NULL OR t.qd_id IS NULL OR t.q_id IS NULL OR t.qs_id IS NULL OR
             t.mdi_id IS NULL OR t.md_id IS NULL OR t.mi_id IS NULL OR
             (t.expected_state='migrated_active' AND t.ri_id IS NULL) OR
             t.target_qkp_ids IS NULL OR t.target_projection_ids IS NULL OR
             cardinality(t.target_qkp_ids) = 0 OR cardinality(t.target_projection_ids) = 0 OR
             ARRAY(SELECT qkp.knowledge_point_id FROM public.question_knowledge_points qkp WHERE qkp.question_id=t.target_question_id ORDER BY qkp.sort_order,qkp.knowledge_point_id) IS DISTINCT FROM t.target_qkp_ids OR
             ARRAY(SELECT kpl.id FROM public.knowledge_point_links kpl WHERE kpl.target_type='mistake' AND kpl.target_id=t.target_mistake_id::text ORDER BY kpl.id) IS DISTINCT FROM t.target_projection_ids
          )) AS relation_orphan_mismatch
      )
      SELECT jsonb_build_object(
        'scope', jsonb_build_object('expected_source_count',expected_count,'ledger_count',ledger_count,'extra_ledger_count',extra_ledger_count),
        'checks', to_jsonb(counts) - 'expected_count' - 'ledger_count' - 'extra_ledger_count',
        'admin_identity', jsonb_build_object('current_user',current_user,'session_user',session_user),
        'canonicalizer_called',false,
        'pass', expected_count=4 AND ledger_count=4 AND actual_ledger_row_count=allowed_pair_count AND
          actual_pair_count=allowed_pair_count AND duplicate_pair_count=0 AND
          allowed_pair_mismatch_count=0 AND extra_ledger_count=0 AND
          state_mismatch=0 AND target_parity_mismatch=0 AND active_review_mismatch=0 AND
          paused_review_mismatch=0 AND retained_mismatch=0 AND review_record_count=0 AND
          duplicate_count=0 AND source_hash_mismatch=0 AND source_field_mismatch=0 AND relation_orphan_mismatch=0
      ) AS evidence
      FROM counts
    """
    engine = await _engine(raw)
    try:
        async with engine.connect() as c:
            result = (await c.execute(text(verification_sql))).scalar_one()
        if isinstance(result, str):
            result = json.loads(result)
        if not result.get("pass"):
            raise AssertionError(f"LSR03_POST_POSITIVE_VERIFICATION_FAILED:{result}")
        print(json.dumps(result, default=str, sort_keys=True))
        return result
    finally:
        await engine.dispose()


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("LSR03_DATABASE_URL"))
    parser.add_argument("--seed-extended", action="store_true")
    parser.add_argument("--introspect", action="store_true")
    parser.add_argument("--verify-positive", action="store_true")
    parser.add_argument("--seed-pre026-restore-sentinel", action="store_true")
    parser.add_argument("--verify-pre026-restore-sentinel", action="store_true")
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("LSR03_DATABASE_URL required")
    if args.seed_extended:
        print(json.dumps(await seed_extended(args.database_url), sort_keys=True))
    if args.seed_pre026_restore_sentinel:
        await seed_pre026_restore_sentinel(args.database_url)
    if args.verify_pre026_restore_sentinel:
        await verify_pre026_restore_sentinel(args.database_url)
    if args.verify_positive:
        await verify_positive(args.database_url)
    if args.introspect:
        await introspect(args.database_url)


if __name__ == "__main__":
    asyncio.run(main())
