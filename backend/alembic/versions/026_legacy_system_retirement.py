"""Install the governed legacy Note migration contract.

This revision is intentionally isolated from the HTTP route cutover.  It adds
the provenance ledger, append-only audit relations, owner functions and the
small target-column delta required by the frozen LSR-02 contract.
"""

from collections.abc import Sequence
import re

from alembic import op
import sqlalchemy as sa


revision: str = "026"
down_revision: str | None = "025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_DEFERRED_TABLES: list[str] = []
_DEFERRED_FUNCTIONS: list[str] = []
_DEFERRED_TRIGGERS: list[str] = []


def _sql(statement: str) -> None:
    """Execute top-level statements separately for asyncpg prepared statements."""
    dollar_tag: str | None = None
    quote: str | None = None
    start = 0
    statements: list[str] = []
    index = 0
    while index < len(statement):
        char = statement[index]
        if quote:
            if char == quote:
                if index + 1 < len(statement) and statement[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            elif char == "\\" and quote == "'":
                index += 2
                continue
        elif dollar_tag:
            if statement.startswith(dollar_tag, index):
                index += len(dollar_tag)
                dollar_tag = None
                continue
        elif char in ("'", '"'):
            quote = char
        elif char == "$":
            match = re.match(r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$", statement[index:])
            if match:
                dollar_tag = match.group(0)
                index += len(dollar_tag)
                continue
        elif char == ";":
            if statement[start:index].strip():
                statements.append(statement[start:index])
            start = index + 1
        index += 1
    if statement[start:].strip():
        statements.append(statement[start:])
    for item in statements:
        normalized = item.lstrip().upper()
        if normalized.startswith("CREATE FUNCTION"):
            _DEFERRED_FUNCTIONS.append(item)
        elif normalized.startswith("CREATE TRIGGER"):
            _DEFERRED_TRIGGERS.append(item)
        elif normalized.startswith((
            "CREATE TABLE PUBLIC.LEGACY_NOTE_MIGRATION_EVENTS",
            "CREATE TABLE PUBLIC.LEGACY_MIGRATION_APPROVAL_AUTHORIZATIONS",
            "CREATE TABLE PUBLIC.LEGACY_MIGRATION_ROLLBACK_ADMINS",
            "CREATE TABLE PUBLIC.LEGACY_MIGRATION_ROLLBACK_AUDITS",
            "CREATE TABLE PUBLIC.LEGACY_NOTE_MIGRATION_REJECTIONS",
            "ALTER TABLE PUBLIC.LEGACY_NOTE_MIGRATIONS\n          ADD CONSTRAINT FK_LNM_",
        )):
            _DEFERRED_TABLES.append(item)
        else:
            op.execute(sa.text(item + ";"))


def _flush_deferred() -> None:
    for item in _DEFERRED_TABLES:
        op.execute(sa.text(item + ";"))
    for item in _DEFERRED_FUNCTIONS:
        function_sql = item.rstrip()
        if function_sql.endswith("END $$"):
            function_sql = function_sql[:-len("END $$")] + "END; $$"
        op.execute(sa.text(function_sql + ";"))
    for item in _DEFERRED_TRIGGERS:
        op.execute(sa.text(item + ";"))
    _DEFERRED_TABLES.clear()
    _DEFERRED_FUNCTIONS.clear()
    _DEFERRED_TRIGGERS.clear()


def upgrade() -> None:
    # The contract is non-production only until a separate release decision.
    _sql("CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public")
    _sql(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='app_role') THEN
            CREATE ROLE app_role NOLOGIN;
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_migration_owner') THEN
            CREATE ROLE legacy_migration_owner NOLOGIN;
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_adapter') THEN
            CREATE ROLE legacy_note_adapter NOLOGIN;
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_adapter_runner') THEN
            CREATE ROLE legacy_note_adapter_runner LOGIN;
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_migration_maintenance_runner') THEN
            CREATE ROLE legacy_migration_maintenance_runner LOGIN;
          END IF;
          IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='legacy_note_verifier') THEN
            CREATE ROLE legacy_note_verifier NOLOGIN;
          END IF;
        END $$;
        GRANT legacy_note_adapter TO legacy_note_adapter_runner;
        REVOKE legacy_note_adapter FROM app_role, legacy_note_verifier;
        REVOKE legacy_migration_owner FROM app_role, legacy_note_adapter,
          legacy_note_adapter_runner, legacy_migration_maintenance_runner,
          legacy_note_verifier;
        """
    )
    _sql(
        """
        CREATE FUNCTION legacy_migration.transition_legacy_note_migration(
          p_ledger_id UUID,p_expected_from public.legacy_note_migration_state,p_to public.legacy_note_migration_state,
          p_actor_id UUID,p_reason TEXT,p_source_note_id UUID,p_mapping_version VARCHAR(64),p_expected_source_hash TEXT,
          p_target_bundle legacy_migration.legacy_note_migration_target_bundle,p_rollback_reference TEXT,
          p_expected_rollback_hash TEXT,p_mapped_next_review_at TIMESTAMPTZ,p_mapped_last_reviewed_at TIMESTAMPTZ,p_event_details JSONB)
        RETURNS public.legacy_note_migrations LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE m public.legacy_note_migrations%ROWTYPE; result public.legacy_note_migrations; eid UUID; bundle_hash CHAR(64);
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner' OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED'; END IF;
          IF NOT EXISTS (SELECT 1 FROM legacy_migration.allowed_legacy_note_migration_transitions WHERE from_state=p_expected_from AND to_state=p_to) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_ILLEGAL_TRANSITION'; END IF;
          IF p_expected_source_hash IS NULL OR p_expected_source_hash !~ '^[0-9a-f]{64}$' OR p_actor_id IS NULL THEN RAISE EXCEPTION 'LEGACY_MIGRATION_INVALID_REASON_OR_REQUIRED_PARAMETER'; END IF;
          SELECT * INTO m FROM public.legacy_note_migrations WHERE id=p_ledger_id FOR UPDATE;
          IF NOT FOUND OR m.state<>p_expected_from OR m.source_note_id<>p_source_note_id OR m.mapping_version<>p_mapping_version OR m.source_hash<>p_expected_source_hash::char(64) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_STALE_EXPECTED_STATE'; END IF;
          IF p_to IN ('ready','retained_public_only') AND (m.source_approval_event_id IS NULL OR m.source_approved_by<>p_actor_id) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_APPROVAL_REQUIRED'; END IF;
          IF p_to='retained_public_only' AND (m.source_status<>'published' OR m.source_hidden) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_PUBLIC_ONLY_TARGETS_NONNULL'; END IF;
          IF p_to='retained_public_only' AND (
             m.source_approved_by IS NULL OR m.source_approved_at IS NULL OR m.source_approval_sequence IS NULL
             OR m.source_approval_event_id IS NULL OR m.approved_by IS DISTINCT FROM m.source_approved_by
             OR m.approved_at IS DISTINCT FROM m.source_approved_at
          ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_APPROVAL_REQUIRED'; END IF;
          IF p_to='retained_public_only' AND (
             p_target_bundle.target_question_draft_item_id IS NOT NULL
             OR p_target_bundle.target_question_draft_id IS NOT NULL
             OR p_target_bundle.target_question_id IS NOT NULL
             OR p_target_bundle.target_question_source_id IS NOT NULL
             OR p_target_bundle.target_mistake_draft_item_id IS NOT NULL
             OR p_target_bundle.target_mistake_draft_id IS NOT NULL
             OR p_target_bundle.target_mistake_id IS NOT NULL
             OR p_target_bundle.target_review_item_id IS NOT NULL
             OR p_target_bundle.target_qkp_ids IS NOT NULL
             OR p_target_bundle.target_projection_ids IS NOT NULL
             OR p_mapped_next_review_at IS NOT NULL OR p_mapped_last_reviewed_at IS NOT NULL
             OR p_rollback_reference IS NOT NULL OR p_expected_rollback_hash IS NOT NULL
             OR m.mapped_next_review_at IS NOT NULL OR m.mapped_last_reviewed_at IS NOT NULL
             OR m.rollback_reference IS NOT NULL OR m.rollback_event_id IS NOT NULL
             OR m.rollback_actor_id IS NOT NULL OR m.target_bundle_hash IS NOT NULL
             OR m.question_conversion_approved_by IS NOT NULL OR m.question_conversion_approved_at IS NOT NULL
             OR m.question_conversion_sequence IS NOT NULL OR m.question_approval_event_id IS NOT NULL
             OR m.mistake_conversion_approved_by IS NOT NULL OR m.mistake_conversion_approved_at IS NOT NULL
             OR m.mistake_conversion_sequence IS NOT NULL OR m.mistake_approval_event_id IS NOT NULL
             OR m.schedule_approved_by IS NOT NULL OR m.schedule_approved_at IS NOT NULL
             OR m.schedule_approval_sequence IS NOT NULL OR m.schedule_approval_event_id IS NOT NULL
          ) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_PUBLIC_ONLY_TARGETS_NONNULL'; END IF;
          IF p_to='migrated_active' AND (m.schedule_approval_event_id IS NULL OR m.schedule_approved_by<>p_actor_id OR p_mapped_next_review_at IS NULL OR p_target_bundle.target_review_item_id IS NULL) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_ACTIVE_TARGETS_REQUIRED'; END IF;
          IF p_to='migrated_paused' AND (m.question_approval_event_id IS NULL OR m.mistake_approval_event_id IS NULL OR p_target_bundle.target_review_item_id IS NOT NULL OR p_mapped_next_review_at IS NOT NULL) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_PAUSED_TARGET_SHAPE'; END IF;
          IF p_to IN ('migrated_active','migrated_paused') AND (p_target_bundle.target_question_id IS NULL OR p_target_bundle.target_question_source_id IS NULL OR p_target_bundle.target_mistake_id IS NULL OR p_target_bundle.target_qkp_ids IS NULL OR p_target_bundle.target_projection_ids IS NULL OR p_target_bundle.target_question_draft_item_id IS NULL OR p_target_bundle.target_question_draft_id IS NULL OR p_target_bundle.target_mistake_draft_item_id IS NULL OR p_target_bundle.target_mistake_draft_id IS NULL) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_TARGETS_REQUIRED'; END IF;
          IF p_to='rolled_back' THEN
            IF p_rollback_reference IS NULL OR p_expected_rollback_hash IS DISTINCT FROM p_rollback_reference OR NOT EXISTS (SELECT 1 FROM public.legacy_migration_rollback_audits a WHERE a.ledger_id=m.id AND a.rollback_reference=p_rollback_reference) OR NOT EXISTS (SELECT 1 FROM public.legacy_migration_rollback_admins a WHERE a.user_id=p_actor_id AND a.enabled) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_HASH_MISMATCH'; END IF;
            IF EXISTS (SELECT 1 FROM public.capture_items c WHERE c.mistake_draft_item_id=m.target_mistake_draft_item_id)
               OR EXISTS (SELECT 1 FROM public.attempts a WHERE a.mistake_draft_item_id=m.target_mistake_draft_item_id)
               OR EXISTS (SELECT 1 FROM public.mistake_drafts d WHERE d.id=m.target_mistake_draft_id AND d.attempt_id IS NOT NULL) THEN
              RAISE EXCEPTION 'LEGACY_MIGRATION_UNEXPECTED_INBOUND_REFERENCE_SNAPSHOT_RESTORE_REQUIRED';
            END IF;
          ELSIF p_rollback_reference IS NOT NULL THEN RAISE EXCEPTION 'LEGACY_MIGRATION_UNEXPECTED_ROLLBACK_REFERENCE'; END IF;
          bundle_hash := pg_catalog.encode(public.digest(pg_catalog.convert_to(row_to_json(p_target_bundle)::text,'UTF8'),'sha256'),'hex');
          eid := public.gen_random_uuid();
          PERFORM legacy_migration.set_legacy_transition_marker(
            'INSERT','public','legacy_note_migration_events',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
            m.state::text,p_to::text,CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN bundle_hash ELSE NULL END,
            eid,CASE WHEN p_to='rolled_back' THEN 'rollback' ELSE 'state_transition' END,p_actor_id,
            CASE WHEN p_to='rolled_back' THEN p_rollback_reference ELSE NULL END);
          INSERT INTO public.legacy_note_migration_events(id,ledger_id,source_note_id,from_state,to_state,actor_id,approval_kind,reason,details,source_hash,mapping_version,target_bundle_hash,rollback_hash)
          VALUES(eid,m.id,m.source_note_id,m.state,p_to,p_actor_id,CASE WHEN p_to='rolled_back' THEN 'rollback' ELSE 'state_transition' END,COALESCE(NULLIF(p_reason,''),'transition'),COALESCE(p_event_details,'{}'::jsonb),m.source_hash,m.mapping_version,CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN bundle_hash ELSE NULL END,CASE WHEN p_to='rolled_back' THEN p_rollback_reference ELSE NULL END);
          IF p_to='rolled_back' THEN
            PERFORM legacy_migration.set_legacy_transition_marker(
              'UPDATE','public','legacy_note_migrations',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
              m.state::text,m.state::text,NULL,eid,'rollback',p_actor_id,p_rollback_reference);
            UPDATE public.legacy_note_migrations
              SET target_question_draft_item_id=NULL,target_question_draft_id=NULL,target_question_source_id=NULL,
                  target_qkp_ids=NULL,target_question_id=NULL,target_projection_ids=NULL,
                  target_mistake_draft_item_id=NULL,target_mistake_draft_id=NULL,target_mistake_id=NULL,
                  target_review_item_id=NULL,target_bundle_hash=NULL
              WHERE id=m.id;
            DELETE FROM public.knowledge_point_links
             WHERE target_type='mistake' AND target_id=m.target_mistake_id::text;
            DELETE FROM public.review_items WHERE id=m.target_review_item_id;
            DELETE FROM public.mistakes WHERE id=m.target_mistake_id;
            DELETE FROM public.mistake_drafts WHERE id=m.target_mistake_draft_id;
            DELETE FROM public.question_sources WHERE id=m.target_question_source_id;
            DELETE FROM public.question_knowledge_points WHERE question_id=m.target_question_id;
            DELETE FROM public.questions WHERE id=m.target_question_id;
            DELETE FROM public.question_drafts WHERE id=m.target_question_draft_id;
            DELETE FROM public.draft_items WHERE id IN (m.target_question_draft_item_id,m.target_mistake_draft_item_id);
            PERFORM legacy_migration.set_legacy_transition_marker(
              'UPDATE','public','legacy_note_migrations',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
              m.state::text,'rolled_back',NULL,eid,'rollback',p_actor_id,p_rollback_reference);
            UPDATE public.legacy_note_migrations SET state='rolled_back',rollback_actor_id=p_actor_id,rollback_reference=p_rollback_reference,rollback_event_id=eid,transition_event_id=NULL,target_question_draft_item_id=NULL,target_question_draft_id=NULL,target_question_source_id=NULL,target_qkp_ids=NULL,target_question_id=NULL,target_projection_ids=NULL,target_mistake_draft_item_id=NULL,target_mistake_draft_id=NULL,target_mistake_id=NULL,target_review_item_id=NULL,target_bundle_hash=NULL,manual_review_required=TRUE,mapped_next_review_at=NULL,approved_by=NULL,approved_at=NULL,source_approved_by=NULL,source_approved_at=NULL,source_approval_sequence=NULL,question_conversion_approved_by=NULL,question_conversion_approved_at=NULL,question_conversion_sequence=NULL,mistake_conversion_approved_by=NULL,mistake_conversion_approved_at=NULL,mistake_conversion_sequence=NULL,schedule_approved_by=NULL,schedule_approved_at=NULL,schedule_approval_sequence=NULL,source_approval_event_id=NULL,question_approval_event_id=NULL,mistake_approval_event_id=NULL,schedule_approval_event_id=NULL,updated_at=now() WHERE id=m.id;
          ELSIF p_to='failed' THEN
            PERFORM legacy_migration.set_legacy_transition_marker(
              'UPDATE','public','legacy_note_migrations',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
              m.state::text,'failed',NULL,eid,'state_transition',p_actor_id,NULL);
            UPDATE public.legacy_note_migrations SET state='failed',target_question_draft_item_id=NULL,target_question_draft_id=NULL,target_question_source_id=NULL,target_qkp_ids=NULL,target_question_id=NULL,target_projection_ids=NULL,target_mistake_draft_item_id=NULL,target_mistake_draft_id=NULL,target_mistake_id=NULL,target_review_item_id=NULL,target_bundle_hash=NULL,manual_review_required=TRUE,mapped_next_review_at=NULL,updated_at=now() WHERE id=m.id;
          ELSIF p_to='pending_mapping' THEN
            PERFORM legacy_migration.set_legacy_transition_marker(
              'UPDATE','public','legacy_note_migrations',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
              m.state::text,'pending_mapping',NULL,eid,'state_transition',p_actor_id,NULL);
            UPDATE public.legacy_note_migrations SET state='pending_mapping',approved_by=NULL,approved_at=NULL,source_approved_by=NULL,source_approved_at=NULL,source_approval_sequence=NULL,question_conversion_approved_by=NULL,question_conversion_approved_at=NULL,question_conversion_sequence=NULL,mistake_conversion_approved_by=NULL,mistake_conversion_approved_at=NULL,mistake_conversion_sequence=NULL,schedule_approved_by=NULL,schedule_approved_at=NULL,schedule_approval_sequence=NULL,source_approval_event_id=NULL,question_approval_event_id=NULL,mistake_approval_event_id=NULL,schedule_approval_event_id=NULL,updated_at=now() WHERE id=m.id;
          ELSE
            PERFORM legacy_migration.set_legacy_transition_marker(
              'UPDATE','public','legacy_note_migrations',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
              m.state::text,p_to::text,CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN bundle_hash ELSE NULL END,
              eid,'state_transition',p_actor_id,NULL);
            UPDATE public.legacy_note_migrations SET state=p_to,transition_event_id=eid,target_question_draft_item_id=p_target_bundle.target_question_draft_item_id,target_question_draft_id=p_target_bundle.target_question_draft_id,target_question_source_id=p_target_bundle.target_question_source_id,target_qkp_ids=p_target_bundle.target_qkp_ids,target_question_id=p_target_bundle.target_question_id,target_projection_ids=p_target_bundle.target_projection_ids,target_mistake_draft_item_id=p_target_bundle.target_mistake_draft_item_id,target_mistake_draft_id=p_target_bundle.target_mistake_draft_id,target_mistake_id=p_target_bundle.target_mistake_id,target_review_item_id=p_target_bundle.target_review_item_id,target_bundle_hash=CASE WHEN p_to IN ('migrated_active','migrated_paused') THEN bundle_hash ELSE NULL END,manual_review_required=(p_to<>'migrated_active'),mapped_next_review_at=CASE WHEN p_to='migrated_active' THEN p_mapped_next_review_at ELSE NULL END,mapped_last_reviewed_at=COALESCE(p_mapped_last_reviewed_at,m.mapped_last_reviewed_at),updated_at=now() WHERE id=m.id;
          END IF;
          SELECT * INTO result FROM public.legacy_note_migrations WHERE id=m.id; RETURN result;
        END $$;

        CREATE FUNCTION legacy_migration.load_legacy_migration_rollback_audit(
          p_ledger_id UUID,p_source_note_id UUID,p_mapping_version VARCHAR(64),p_source_hash TEXT,p_rollback_reference TEXT,p_rollback_json JSONB)
        RETURNS public.legacy_migration_rollback_audits LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE r public.legacy_migration_rollback_audits;
          l public.legacy_note_migrations%ROWTYPE;
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner' OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED'; END IF;
          IF p_source_hash !~ '^[0-9a-f]{64}$' OR p_rollback_reference !~ '^[0-9a-f]{64}$' OR pg_catalog.encode(public.digest(pg_catalog.convert_to(p_rollback_json::text,'UTF8'),'sha256'),'hex') IS DISTINCT FROM p_rollback_reference THEN RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_HASH_INVALID'; END IF;
          SELECT * INTO l FROM public.legacy_note_migrations WHERE id=p_ledger_id FOR UPDATE;
          IF NOT FOUND OR l.source_note_id IS DISTINCT FROM p_source_note_id
             OR l.mapping_version IS DISTINCT FROM p_mapping_version
             OR l.source_hash IS DISTINCT FROM p_source_hash::char(64) THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_SOURCE_BINDING_MISMATCH';
          END IF;
          PERFORM legacy_migration.set_legacy_transition_marker(
            'INSERT','public','legacy_migration_rollback_audits',p_ledger_id,p_source_note_id,p_mapping_version,p_source_hash,
            NULL,'rollback_audit',NULL,NULL,NULL,NULL,p_rollback_reference);
          INSERT INTO public.legacy_migration_rollback_audits(ledger_id,source_note_id,mapping_version,source_hash,rollback_reference,rollback_json)
          VALUES(p_ledger_id,p_source_note_id,p_mapping_version,p_source_hash::char(64),p_rollback_reference::char(64),p_rollback_json) RETURNING * INTO r;
          RETURN r;
        END $$;

        CREATE FUNCTION legacy_migration.record_legacy_note_migration_rejection(
          p_rejection_id UUID,p_source_note_id UUID,p_mapping_version TEXT,p_source_hash TEXT,p_source_title TEXT,p_disposition TEXT,p_reason TEXT,p_snapshot_ref TEXT,p_idempotency_key TEXT,p_actor_id UUID)
        RETURNS public.legacy_note_migration_rejections LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE n public.notes%ROWTYPE; r public.legacy_note_migration_rejections; live JSONB; live_hash CHAR(64);
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner' OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED'; END IF;
          IF p_reason<>'SOURCE_TITLE_TOO_LONG' OR p_disposition NOT IN ('manual','failed') THEN RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_REASON_INVALID'; END IF;
          SELECT * INTO n FROM public.notes WHERE id=p_source_note_id FOR UPDATE;
          IF NOT FOUND OR n.type<>'mistake' THEN RAISE EXCEPTION 'SOURCE_TYPE_NOT_MISTAKE'; END IF;
          live:=legacy_migration.canonicalize_legacy_note(p_source_note_id);
          live_hash:=pg_catalog.encode(public.digest(pg_catalog.convert_to(live::text,'UTF8'),'sha256'),'hex');
          IF p_source_hash IS DISTINCT FROM live_hash OR p_snapshot_ref IS DISTINCT FROM 'sha256:'||live_hash THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_DRIFT'; END IF;
          IF n.title IS NULL OR char_length(n.title)<=300 OR p_source_title IS DISTINCT FROM n.title THEN RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG'; END IF;
          IF EXISTS (SELECT 1 FROM public.legacy_note_migration_rejections WHERE source_note_id=p_source_note_id AND mapping_version=p_mapping_version AND idempotency_key=p_idempotency_key) THEN SELECT * INTO r FROM public.legacy_note_migration_rejections WHERE source_note_id=p_source_note_id AND mapping_version=p_mapping_version AND idempotency_key=p_idempotency_key; RETURN r; END IF;
          INSERT INTO public.legacy_note_migration_rejections(id,source_note_id,mapping_version,source_hash,snapshot_ref,source_title,reason,disposition,migration_notes,created_at,idempotency_key,actor_id)
          VALUES(p_rejection_id,p_source_note_id,p_mapping_version,p_source_hash::char(64),p_snapshot_ref,p_source_title,p_reason,p_disposition,jsonb_build_array(p_reason),now(),p_idempotency_key,p_actor_id) RETURNING * INTO r;
          RETURN r;
        END $$;
        """
    )
    _sql(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='legacy_note_migration_state') THEN
            CREATE TYPE public.legacy_note_migration_state AS ENUM
              ('pending_mapping','ready','migrated_active','migrated_paused',
               'retained_public_only','failed','rolled_back');
          END IF;
        END $$
        """
    )
    _sql(
        """
        CREATE SCHEMA IF NOT EXISTS legacy_migration AUTHORIZATION legacy_migration_owner;
        REVOKE CREATE ON SCHEMA legacy_migration FROM PUBLIC;
        GRANT USAGE ON SCHEMA legacy_migration TO legacy_note_adapter,
          legacy_note_verifier, legacy_migration_maintenance_runner;
        GRANT USAGE ON SCHEMA public TO legacy_migration_owner
        """
    )

    _sql(
        """
        CREATE FUNCTION legacy_migration.create_legacy_note_migration_pending(
          p_ledger_id UUID,p_source_note_id UUID,p_mapping_version VARCHAR(64),
          p_source_hash TEXT,p_source_slug VARCHAR(255),p_source_title VARCHAR(500),
          p_source_url VARCHAR(500),p_source_status VARCHAR(20),p_source_hidden BOOLEAN,
          p_source_revision INTEGER,p_snapshot_ref VARCHAR(255),p_idempotency_key VARCHAR(128),
          p_canonical_payload JSONB,p_legacy_review_json JSONB,p_migration_notes JSONB)
        RETURNS public.legacy_note_migrations LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE n public.notes%ROWTYPE; old public.legacy_note_migrations%ROWTYPE;
          result public.legacy_note_migrations; live JSONB; live_hash CHAR(64);
          expected_idempotency_key VARCHAR(128);
          ef_bits TEXT; ef_value DOUBLE PRECISION; iv INTEGER; reps INTEGER;
          next_day DATE; last_seen TIMESTAMP; mapped_last TIMESTAMPTZ;
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
             OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
          END IF;
          IF p_source_hash IS NULL OR octet_length(p_source_hash)<>64 OR p_source_hash !~ '^[0-9a-f]{64}$'
             OR p_snapshot_ref IS DISTINCT FROM 'sha256:'||lower(p_source_hash)
             OR p_canonical_payload IS NULL OR jsonb_typeof(p_canonical_payload)<>'object'
             OR p_legacy_review_json IS NULL OR jsonb_typeof(p_legacy_review_json)<>'object'
             OR p_migration_notes IS NULL OR jsonb_typeof(p_migration_notes)<>'array' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
          END IF;
          IF p_source_title IS NULL OR char_length(p_source_title)>300
             OR p_canonical_payload->>'title' IS NULL
             OR char_length(p_canonical_payload->>'title')>300 THEN
            RAISE EXCEPTION 'SOURCE_TITLE_TOO_LONG';
          END IF;
          IF NOT (p_canonical_payload ?& ARRAY['id','source_note_id','slug','source_url','title','content','type','status','hidden','created_at','updated_at','summary','cover','category','subject','difficulty','question','answers','analysis','knowledge_points','ef','legacy_ef_bits','interval','repetitions','next_review','last_reviewed','images','ai_metadata','folder_id','sort_order','revision','tags','search_vector_token','legacy_review_json']) THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
          END IF;
          IF NOT (p_canonical_payload ?& ARRAY['subject_id','question_type','options']) THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
          END IF;
          IF jsonb_typeof(p_canonical_payload->'answers')<>'object'
             OR jsonb_typeof(p_canonical_payload->'knowledge_points')<>'array'
             OR jsonb_typeof(p_canonical_payload->'tags')<>'array'
             OR jsonb_typeof(p_canonical_payload->'ef')<>'number'
             OR jsonb_typeof(p_canonical_payload->'legacy_ef_bits')<>'string'
             OR p_canonical_payload->>'legacy_ef_bits' !~ '^[0-9a-f]{16}$'
             OR p_canonical_payload->>'interval' !~ '^(0|[1-9][0-9]{0,9})$'
             OR p_canonical_payload->>'repetitions' !~ '^(0|[1-9][0-9]{0,9})$' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
          END IF;
          BEGIN
            ef_value := (p_canonical_payload->>'ef')::double precision;
            iv := (p_canonical_payload->>'interval')::integer;
            reps := (p_canonical_payload->>'repetitions')::integer;
            next_day := CASE WHEN p_canonical_payload->>'next_review' IS NULL THEN NULL ELSE (p_canonical_payload->>'next_review')::date END;
            last_seen := CASE WHEN p_canonical_payload->>'last_reviewed' IS NULL THEN NULL ELSE ((p_canonical_payload->>'last_reviewed')::timestamptz AT TIME ZONE 'UTC') END;
            mapped_last := CASE WHEN p_canonical_payload->>'last_reviewed' IS NULL THEN NULL ELSE (p_canonical_payload->>'last_reviewed')::timestamptz END;
          EXCEPTION WHEN others THEN RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
          END;
          ef_bits := p_canonical_payload->>'legacy_ef_bits';
          IF ef_value::text IN ('NaN','Infinity','-Infinity') THEN RAISE EXCEPTION 'LEGACY_MIGRATION_EF_NONFINITE'; END IF;
          IF ef_bits IS DISTINCT FROM pg_catalog.encode(pg_catalog.float8send(ef_value),'hex')
             OR iv<0 OR reps<0 THEN RAISE EXCEPTION 'LEGACY_MIGRATION_EF_NONFINITE'; END IF;
          live := legacy_migration.canonicalize_legacy_note(p_source_note_id);
          live_hash := pg_catalog.encode(public.digest(pg_catalog.convert_to(live::text,'UTF8'),'sha256'),'hex');
          IF live_hash IS DISTINCT FROM lower(p_source_hash)
             OR p_canonical_payload IS DISTINCT FROM live THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_DRIFT';
          END IF;
          expected_idempotency_key := 'legacy:'||pg_catalog.encode(
            public.digest(pg_catalog.convert_to(
              'legacy-note-migration|'||lower(p_source_note_id::text)||'|'||p_source_revision::text||'|'||lower(p_source_hash)||'|'||p_mapping_version,
              'UTF8'),'sha256'),'hex');
          IF p_idempotency_key IS DISTINCT FROM expected_idempotency_key THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_IDEMPOTENCY_CONFLICT';
          END IF;
          SELECT * INTO n FROM public.notes WHERE id=p_source_note_id FOR UPDATE;
          IF NOT FOUND OR n.type IS DISTINCT FROM 'mistake' THEN RAISE EXCEPTION 'SOURCE_TYPE_NOT_MISTAKE'; END IF;
          IF n.slug IS DISTINCT FROM p_source_slug OR n.title IS DISTINCT FROM p_source_title
             OR n.status IS DISTINCT FROM p_source_status OR n.hidden IS DISTINCT FROM p_source_hidden
             OR n.revision IS DISTINCT FROM p_source_revision OR p_source_url IS DISTINCT FROM '/notes/'||n.slug THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_DRIFT';
          END IF;
          SELECT * INTO old FROM public.legacy_note_migrations
           WHERE source_note_id=p_source_note_id AND mapping_version=p_mapping_version FOR UPDATE;
          IF FOUND THEN
            IF old.id IS DISTINCT FROM p_ledger_id OR old.source_hash IS DISTINCT FROM p_source_hash
               OR old.idempotency_key IS DISTINCT FROM p_idempotency_key THEN
              RAISE EXCEPTION 'LEGACY_MIGRATION_IDEMPOTENCY_CONFLICT';
            END IF;
            RETURN old;
          END IF;
          PERFORM legacy_migration.set_legacy_transition_marker(
            'INSERT','public','legacy_note_migrations',p_ledger_id,p_source_note_id,p_mapping_version,p_source_hash,
            NULL,'pending_mapping',NULL,NULL,NULL,NULL,NULL);
          INSERT INTO public.legacy_note_migrations(
            id,source_note_id,source_slug,source_title,source_url,source_status,source_hidden,
            source_revision,source_hash,snapshot_ref,mapping_version,idempotency_key,state,
            legacy_ef,legacy_ef_bits,legacy_interval,legacy_repetitions,legacy_next_review,
            legacy_last_reviewed,mapped_last_reviewed_at,legacy_review_json,canonical_payload,migration_notes)
          VALUES(p_ledger_id,p_source_note_id,p_source_slug,p_source_title,p_source_url,p_source_status,
            p_source_hidden,p_source_revision,p_source_hash,p_snapshot_ref,p_mapping_version,p_idempotency_key,
            'pending_mapping',ef_value,ef_bits::char(16),iv,reps,next_day,last_seen,mapped_last,
            p_legacy_review_json,p_canonical_payload,p_migration_notes) RETURNING * INTO result;
          RETURN result;
        END $$;

        CREATE FUNCTION legacy_migration.record_legacy_note_migration_approval(
          p_ledger_id UUID,p_mapping_version TEXT,p_expected_source_hash TEXT,
          p_expected_state public.legacy_note_migration_state,p_kind VARCHAR(32),p_actor_id UUID,
          p_approved_at TIMESTAMPTZ,p_expected_sequence INTEGER,p_sequence INTEGER,p_reason TEXT,p_event_details JSONB)
        RETURNS public.legacy_note_migrations LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE m public.legacy_note_migrations%ROWTYPE; eid UUID; result public.legacy_note_migrations; expected_seq INTEGER;
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner' OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED'; END IF;
          IF p_kind NOT IN ('source','question_conversion','mistake_conversion','schedule') OR p_actor_id IS NULL OR p_approved_at IS NULL OR p_sequence IS NULL OR p_sequence<=0 THEN RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_KIND_INVALID'; END IF;
          SELECT * INTO m FROM public.legacy_note_migrations WHERE id=p_ledger_id FOR UPDATE;
          IF NOT FOUND OR m.mapping_version<>p_mapping_version OR m.source_hash<>p_expected_source_hash::char(64) OR m.state<>p_expected_state THEN RAISE EXCEPTION 'LEGACY_MIGRATION_STALE_EXPECTED_STATE'; END IF;
          IF NOT EXISTS (SELECT 1 FROM public.legacy_migration_approval_authorizations a WHERE a.user_id=p_actor_id AND a.approval_kind=p_kind AND a.enabled) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_APPROVAL_ACTOR_NOT_AUTHORIZED'; END IF;
          IF (p_kind='source' AND (m.state<>'pending_mapping' OR m.source_approval_event_id IS NOT NULL)) OR
             (p_kind IN ('question_conversion','mistake_conversion') AND (m.state<>'ready' OR (p_kind='question_conversion' AND m.question_approval_event_id IS NOT NULL) OR (p_kind='mistake_conversion' AND m.mistake_approval_event_id IS NOT NULL))) OR
             (p_kind='schedule' AND m.state NOT IN ('ready','migrated_paused')) THEN RAISE EXCEPTION 'LEGACY_MIGRATION_DUPLICATE_APPROVAL'; END IF;
          expected_seq := CASE p_kind
            WHEN 'source' THEN COALESCE(m.source_approval_sequence,0)
            WHEN 'question_conversion' THEN COALESCE(m.question_conversion_sequence,0)
            WHEN 'mistake_conversion' THEN COALESCE(m.mistake_conversion_sequence,0)
            ELSE COALESCE(m.schedule_approval_sequence,0)
          END;
          IF p_expected_sequence IS DISTINCT FROM expected_seq OR p_sequence<>expected_seq+1 THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_STALE_EXPECTED_SEQUENCE';
          END IF;
          eid := public.gen_random_uuid();
          PERFORM legacy_migration.set_legacy_transition_marker(
            'INSERT','public','legacy_note_migration_events',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
            m.state::text,m.state::text,NULL,eid,p_kind,p_actor_id,NULL);
          INSERT INTO public.legacy_note_migration_events(id,ledger_id,source_note_id,from_state,to_state,actor_id,approval_kind,reason,details,source_hash,mapping_version)
          VALUES(eid,m.id,m.source_note_id,m.state,m.state,p_actor_id,p_kind,COALESCE(NULLIF(p_reason,''),'approval'),COALESCE(p_event_details,'{}'::jsonb)||jsonb_build_object('approved_at',p_approved_at,'sequence',p_sequence),m.source_hash,m.mapping_version);
          PERFORM legacy_migration.set_legacy_transition_marker(
            'UPDATE','public','legacy_note_migrations',m.id,m.source_note_id,m.mapping_version,m.source_hash::text,
            m.state::text,m.state::text,NULL,eid,p_kind,p_actor_id,NULL);
          IF p_kind='source' THEN UPDATE public.legacy_note_migrations SET approved_by=p_actor_id,approved_at=p_approved_at,source_approved_by=p_actor_id,source_approved_at=p_approved_at,source_approval_sequence=p_sequence,source_approval_event_id=eid,updated_at=now() WHERE id=m.id;
          ELSIF p_kind='question_conversion' THEN UPDATE public.legacy_note_migrations SET question_conversion_approved_by=p_actor_id,question_conversion_approved_at=p_approved_at,question_conversion_sequence=p_sequence,question_approval_event_id=eid,updated_at=now() WHERE id=m.id;
          ELSIF p_kind='mistake_conversion' THEN UPDATE public.legacy_note_migrations SET mistake_conversion_approved_by=p_actor_id,mistake_conversion_approved_at=p_approved_at,mistake_conversion_sequence=p_sequence,mistake_approval_event_id=eid,updated_at=now() WHERE id=m.id;
          ELSE UPDATE public.legacy_note_migrations SET schedule_approved_by=p_actor_id,schedule_approved_at=p_approved_at,schedule_approval_sequence=p_sequence,schedule_approval_event_id=eid,updated_at=now() WHERE id=m.id;
          END IF;
          SELECT * INTO result FROM public.legacy_note_migrations WHERE id=m.id; RETURN result;
        END $$;
        """
    )

    _sql(
        """
        CREATE FUNCTION legacy_migration.legacy_uuid_or_null(p_value TEXT)
        RETURNS UUID LANGUAGE plpgsql IMMUTABLE SECURITY INVOKER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        BEGIN
          IF p_value IS NULL OR p_value !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$' THEN
            RETURN NULL;
          END IF;
          RETURN p_value::uuid;
        EXCEPTION WHEN others THEN RETURN NULL;
        END $$;
        CREATE FUNCTION legacy_migration.canonicalize_legacy_note(p_source_note_id UUID)
        RETURNS JSONB LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE n public.notes%ROWTYPE; payload JSONB;
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
             OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CALLER_NOT_AUTHORIZED';
          END IF;
          SELECT * INTO n FROM public.notes WHERE id=p_source_note_id FOR UPDATE;
          IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_SOURCE_NOT_FOUND'; END IF;
          IF n.ef IS NULL OR n.interval IS NULL OR n.repetitions IS NULL
             OR n.ef::text IN ('NaN','Infinity','-Infinity') THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_INVALID';
          END IF;
          payload := jsonb_build_object(
            'id',n.id,'source_note_id',n.id,'slug',n.slug,'source_url','/notes/'||n.slug,
            'title',n.title,'content',n.content,'type',n.type,'status',n.status,'hidden',n.hidden,
            'created_at',to_char(n.created_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
            'updated_at',to_char(n.updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
            'summary',n.summary,'cover',n.cover,'category',n.category,'subject',n.subject,
            'difficulty',n.difficulty,'subject_id',(SELECT s.id FROM public.subjects s WHERE lower(s.name)=lower(n.subject)),
            'question',n.question,'question_type',n.ai_metadata::jsonb->'legacy_question'->>'question_type',
            'options',COALESCE(n.ai_metadata::jsonb->'legacy_question'->'options','null'::jsonb),
            'answers',jsonb_build_object('my_answer',n.my_answer,'correct_answer',n.correct_answer),
            'analysis',n.analysis,
            'knowledge_points',COALESCE((SELECT jsonb_agg(trim(k.value) ORDER BY k.ordinality)
              FROM regexp_split_to_table(replace(replace(replace(replace(COALESCE(n.knowledge_points,''),'，',','),'、',','),E'\\n',','),'；',','),',')
              WITH ORDINALITY AS k(value,ordinality) WHERE trim(k.value)<>''),'[]'::jsonb),
            'ef',n.ef,'legacy_ef_bits',pg_catalog.encode(pg_catalog.float8send(n.ef),'hex'),
            'interval',n.interval,'repetitions',n.repetitions,
            'next_review',to_char(n.next_review,'YYYY-MM-DD'),
            'last_reviewed',to_char(n.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
            'images',n.images,'ai_metadata',n.ai_metadata,'folder_id',n.folder_id,
            'sort_order',n.sort_order,'revision',n.revision,
            'tags',COALESCE((SELECT jsonb_agg(to_jsonb(t.name) ORDER BY t.id,t.name)
              FROM public.note_tags nt JOIN public.tags t ON t.id=nt.tag_id WHERE nt.note_id=n.id),'[]'::jsonb),
            'search_vector_token',CASE WHEN n.search_vector IS NULL THEN '<NULL>' ELSE '<VALUE>'||n.search_vector::text END,
            'legacy_review_json',jsonb_build_object('ef',n.ef,'interval',n.interval,
              'repetitions',n.repetitions,'next_review',to_char(n.next_review,'YYYY-MM-DD'),
              'last_reviewed',to_char(n.last_reviewed AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')));
          RETURN payload;
        END $$;
        """
    )
    _sql(
        """
        CREATE FUNCTION legacy_migration.legacy_question_options_normalize(p_options JSONB)
        RETURNS JSONB LANGUAGE plpgsql IMMUTABLE
        AS $$
        DECLARE out_value JSONB := '[]'::jsonb; v JSONB; i INTEGER := 0;
        BEGIN
          IF p_options IS NULL OR jsonb_typeof(p_options)<>'array' THEN RETURN NULL; END IF;
          IF jsonb_array_length(p_options)=0 THEN RETURN '[]'::jsonb; END IF;
          FOR v IN SELECT value FROM jsonb_array_elements(p_options)
          LOOP
            IF jsonb_typeof(v)='string' AND btrim(v#>>'{}')<>'' THEN
              out_value := out_value || jsonb_build_array(jsonb_build_object('key',chr(65+i),'text',v#>>'{}')); i:=i+1;
            ELSIF jsonb_typeof(v)='object' AND (v ? 'key') AND (v ? 'text')
              AND jsonb_typeof(v->'key')='string' AND jsonb_typeof(v->'text')='string'
              AND btrim(v->>'key')<>'' AND btrim(v->>'text')<>''
              AND (SELECT count(*) FROM jsonb_object_keys(v))=2 THEN
              out_value := out_value || jsonb_build_array(jsonb_build_object('key',v->>'key','text',v->>'text')); i:=i+1;
            ELSE RETURN NULL;
            END IF;
          END LOOP;
          RETURN out_value;
        END $$;
        CREATE FUNCTION legacy_migration.legacy_question_answer_data_expected(
          p_question_type TEXT, p_correct_answer TEXT)
        RETURNS JSONB LANGUAGE plpgsql IMMUTABLE
        AS $$
        BEGIN
          IF p_question_type='true_false' THEN
            IF p_correct_answer='True' THEN RETURN jsonb_build_object('kind','true_false','value',true); END IF;
            IF p_correct_answer='False' THEN RETURN jsonb_build_object('kind','true_false','value',false); END IF;
            RETURN NULL;
          ELSIF p_question_type IN ('single_choice','single') THEN
            IF p_correct_answer IS NULL OR btrim(p_correct_answer)='' OR position(',' IN p_correct_answer)>0 THEN RETURN NULL; END IF;
            RETURN jsonb_build_object('kind','single_choice','value',jsonb_build_array(btrim(p_correct_answer)));
          ELSIF p_question_type IN ('multiple_choice','multiple') THEN
            IF p_correct_answer IS NULL OR btrim(p_correct_answer)='' THEN RETURN NULL; END IF;
            IF EXISTS (
              SELECT btrim(v.value) FROM regexp_split_to_table(p_correct_answer,',') AS v(value)
              WHERE btrim(v.value)='' GROUP BY btrim(v.value)
              UNION ALL
              SELECT btrim(v.value) FROM regexp_split_to_table(p_correct_answer,',') AS v(value)
              GROUP BY btrim(v.value) HAVING count(*)>1
            ) THEN RETURN NULL; END IF;
            RETURN jsonb_build_object(
              'kind','multiple_choice',
              'value',COALESCE((SELECT jsonb_agg(trim(v.value) ORDER BY v.ordinality)
                FROM regexp_split_to_table(p_correct_answer,',') WITH ORDINALITY AS v(value,ordinality)
                WHERE trim(v.value)<>''),'[]'::jsonb));
          ELSIF p_question_type IN ('short_answer','essay') THEN
            IF p_correct_answer IS NULL OR btrim(p_correct_answer)='' THEN RETURN NULL; END IF;
            RETURN jsonb_build_object('kind',p_question_type,'value',p_correct_answer);
          END IF;
          RETURN NULL;
        END $$;
        CREATE FUNCTION legacy_migration.legacy_question_source_matches(
          p_source_id UUID,p_source_note_id UUID,p_mapping_version VARCHAR(64),
          p_source_slug VARCHAR(255),p_source_title VARCHAR(500),p_source_url VARCHAR(500),p_source_hash TEXT)
        RETURNS BOOLEAN LANGUAGE plpgsql STABLE SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE v_source RECORD; v_migration RECORD; v_meta JSONB; v_source_raw TEXT;
        BEGIN
          IF p_source_id IS NULL OR p_source_note_id IS NULL OR p_mapping_version IS NULL
             OR p_source_slug IS NULL OR p_source_title IS NULL OR p_source_url IS NULL
             OR p_source_hash IS NULL OR octet_length(p_source_hash)<>64
             OR p_source_hash !~ '^[0-9a-f]{64}$' THEN RETURN FALSE; END IF;
          SELECT q.id,q.source_type,q.source_ref,q.source_url,q.source_title,q.source_note,q.question_id
            INTO v_source FROM public.question_sources q WHERE q.id=p_source_id;
          IF NOT FOUND THEN RETURN FALSE; END IF;
          IF v_source.source_type IS DISTINCT FROM 'note'
             OR v_source.source_ref IS DISTINCT FROM ('legacy-note:'||lower(p_source_note_id::text))
             OR v_source.source_url IS DISTINCT FROM p_source_url
             OR v_source.source_title IS DISTINCT FROM p_source_title THEN RETURN FALSE; END IF;
          SELECT m.* INTO v_migration FROM public.legacy_note_migrations m
           WHERE m.source_note_id=p_source_note_id AND m.mapping_version=p_mapping_version
             AND m.target_question_source_id=p_source_id AND m.source_hash=p_source_hash::char(64);
          IF NOT FOUND THEN RETURN FALSE; END IF;
          v_source_raw := v_source.source_note;
          BEGIN
            v_meta := v_source_raw::jsonb;
          EXCEPTION WHEN invalid_text_representation THEN
            RETURN FALSE;
          END;
          RETURN v_meta->>'source_note_id' IS NOT DISTINCT FROM p_source_note_id::text
             AND v_meta->>'source_slug' IS NOT DISTINCT FROM p_source_slug
             AND v_meta->>'source_title' IS NOT DISTINCT FROM p_source_title
             AND v_meta->>'source_url' IS NOT DISTINCT FROM p_source_url
             AND v_meta->>'source_hash' IS NOT DISTINCT FROM p_source_hash
             AND v_meta->>'mapping_version' IS NOT DISTINCT FROM p_mapping_version
             AND v_meta->>'source_revision' IS NOT DISTINCT FROM v_migration.source_revision::text;
        END $$;
        CREATE FUNCTION legacy_migration.legacy_question_mirror_matches(
          p_question_id UUID,p_source_id UUID,p_source_note_id UUID,p_mapping_version VARCHAR(64),p_source_hash TEXT)
        RETURNS BOOLEAN LANGUAGE plpgsql STABLE SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE v_question RECORD; v_source RECORD; v_source_raw TEXT; v_meta JSONB;
          v_source_note JSONB; v_migration RECORD; v_expected JSONB; v_options JSONB;
          v_answer_parts JSONB; v_answer_count INTEGER; v_distinct_answer_count INTEGER;
        BEGIN
          IF p_question_id IS NULL OR p_source_id IS NULL OR p_source_note_id IS NULL
             OR p_mapping_version IS NULL OR p_source_hash IS NULL OR octet_length(p_source_hash)<>64
             OR p_source_hash !~ '^[0-9a-f]{64}$' THEN RETURN FALSE; END IF;
          SELECT q.id,q.subject_id,q.title,q.question_type,q.options,q.difficulty,q.question_text,q.stem_md,
                 q.correct_answer,q.answer_data,q.analysis_md,q.explanation,q.visibility,q.status,q.version INTO v_question
            FROM public.questions q WHERE q.id=p_question_id;
          IF NOT FOUND THEN RETURN FALSE; END IF;
          SELECT m.* INTO v_migration FROM public.legacy_note_migrations m
           WHERE m.source_note_id=p_source_note_id AND m.mapping_version=p_mapping_version
             AND m.target_question_id=p_question_id AND m.target_question_source_id=p_source_id
             AND m.source_hash=p_source_hash::char(64);
          IF NOT FOUND THEN RETURN FALSE; END IF;
          IF v_question.status IS DISTINCT FROM 'active'
             OR v_question.visibility IS DISTINCT FROM 'private' OR v_question.version IS DISTINCT FROM 1 THEN RETURN FALSE; END IF;
          SELECT qs.id,qs.question_id,qs.source_type,qs.source_ref,qs.source_url,qs.source_title,qs.source_note
            INTO v_source FROM public.question_sources qs WHERE qs.id=p_source_id;
          IF NOT FOUND THEN RETURN FALSE; END IF;
          IF v_source.question_id IS DISTINCT FROM p_question_id THEN RETURN FALSE; END IF;
          IF NOT legacy_migration.legacy_question_source_matches(
               p_source_id,p_source_note_id,p_mapping_version,v_migration.source_slug,
               v_migration.source_title,v_migration.source_url,p_source_hash) THEN RETURN FALSE; END IF;
          v_source_raw := v_source.source_note;
          BEGIN
            v_source_note := v_source_raw::jsonb;
          EXCEPTION WHEN invalid_text_representation THEN
            RETURN FALSE;
          END;
          IF v_source_note IS NULL OR jsonb_typeof(v_source_note->'mirror_contract') IS DISTINCT FROM 'object' THEN RETURN FALSE; END IF;
          IF v_source_note->>'source_revision' IS DISTINCT FROM v_migration.source_revision::text THEN RETURN FALSE; END IF;
          v_meta := v_source_note->'mirror_contract';
          IF v_question.question_type::text NOT IN ('short_answer','single_choice','multiple_choice','true_false') THEN RETURN FALSE; END IF;
          v_options := to_jsonb(v_question.options);
          IF jsonb_typeof(v_options) IS DISTINCT FROM 'array' THEN RETURN FALSE; END IF;
          IF v_question.question_type::text IN ('short_answer','true_false') AND v_options IS DISTINCT FROM '[]'::jsonb THEN RETURN FALSE; END IF;
          IF v_question.question_type::text IN ('single_choice','multiple_choice') THEN
            IF jsonb_array_length(v_options)<2 THEN RETURN FALSE; END IF;
            IF EXISTS (
              SELECT 1 FROM jsonb_array_elements(v_options) AS e(value)
              WHERE CASE WHEN jsonb_typeof(e.value)='object' THEN
                jsonb_object_length(e.value)<>2
                OR jsonb_typeof(e.value->'key')<>'string' OR jsonb_typeof(e.value->'text')<>'string'
                OR btrim(e.value->>'key')='' OR btrim(e.value->>'text')=''
                ELSE TRUE END
            ) THEN RETURN FALSE; END IF;
            IF (SELECT count(*) FROM jsonb_array_elements(v_options) AS e(value)) <>
               (SELECT count(DISTINCT e.value->>'key') FROM jsonb_array_elements(v_options) AS e(value)) THEN RETURN FALSE; END IF;
          END IF;
          IF v_question.correct_answer IS NULL OR btrim(v_question.correct_answer)='' THEN RETURN FALSE; END IF;
          IF v_question.question_type::text='true_false' AND v_question.correct_answer NOT IN ('True','False') THEN RETURN FALSE; END IF;
          IF v_question.question_type::text IN ('single_choice','multiple_choice') THEN
            v_answer_parts := COALESCE((SELECT jsonb_agg(trim(v.value) ORDER BY v.ordinality)
              FROM regexp_split_to_table(v_question.correct_answer,',') WITH ORDINALITY AS v(value,ordinality)), '[]'::jsonb);
            IF EXISTS (SELECT 1 FROM jsonb_array_elements_text(v_answer_parts) AS a(value) WHERE btrim(a.value)='') THEN RETURN FALSE; END IF;
            SELECT jsonb_array_length(v_answer_parts),count(DISTINCT a.value) INTO v_answer_count,v_distinct_answer_count
              FROM jsonb_array_elements_text(v_answer_parts) AS a(value);
            IF v_question.question_type::text='single_choice' AND
               (v_answer_count<>1 OR NOT EXISTS (SELECT 1 FROM jsonb_array_elements(v_options) AS e(value) WHERE e.value->>'key'=v_answer_parts->>0)) THEN RETURN FALSE; END IF;
            IF v_question.question_type::text='multiple_choice' AND
               (v_answer_count<1 OR v_answer_count<>v_distinct_answer_count OR EXISTS (
                 SELECT 1 FROM jsonb_array_elements_text(v_answer_parts) AS a(value)
                 WHERE NOT EXISTS (SELECT 1 FROM jsonb_array_elements(v_options) AS e(value) WHERE e.value->>'key'=a.value)
               )) THEN RETURN FALSE; END IF;
          END IF;
          v_expected := legacy_migration.legacy_question_answer_data_expected(v_question.question_type::text,v_meta->>'correct_answer');
          IF v_expected IS NULL THEN RETURN FALSE; END IF;
          RETURN v_question.subject_id::text IS NOT DISTINCT FROM v_meta->>'subject_id'
             AND v_question.title IS NOT DISTINCT FROM v_meta->>'title'
             AND v_question.question_text IS NOT DISTINCT FROM v_meta->>'question_text'
             AND v_question.stem_md IS NOT DISTINCT FROM v_meta->>'stem_md'
             AND v_question.question_type::text IS NOT DISTINCT FROM v_meta->>'question_type'
             AND to_jsonb(v_question.options) IS NOT DISTINCT FROM v_meta->'options'
             AND v_question.difficulty::text IS NOT DISTINCT FROM v_meta->>'difficulty'
             AND to_jsonb(v_question.correct_answer) IS NOT DISTINCT FROM v_meta->'correct_answer'
             AND to_jsonb(v_question.answer_data) IS NOT DISTINCT FROM v_expected
             AND v_meta->'answer_data' IS NOT DISTINCT FROM v_expected
             AND v_question.analysis_md IS NOT DISTINCT FROM v_meta->>'analysis_md'
             AND v_question.explanation IS NOT DISTINCT FROM v_meta->>'explanation';
        END $$;
        """
    )

    _sql(
        """
        CREATE TABLE public.legacy_note_migration_events (
          id UUID PRIMARY KEY,
          ledger_id UUID NOT NULL REFERENCES public.legacy_note_migrations(id) ON DELETE RESTRICT,
          source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
          from_state public.legacy_note_migration_state NOT NULL,
          to_state public.legacy_note_migration_state NOT NULL,
          actor_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          approval_kind VARCHAR(32) NOT NULL CHECK (approval_kind IN
            ('source','question_conversion','mistake_conversion','schedule','rollback','state_transition')),
          reason TEXT NOT NULL,
          details JSONB NOT NULL DEFAULT '{}'::jsonb,
          source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
          mapping_version VARCHAR(64) NOT NULL,
          target_bundle_hash CHAR(64) NULL CHECK (target_bundle_hash IS NULL OR target_bundle_hash ~ '^[0-9a-f]{64}$'),
          rollback_hash CHAR(64) NULL CHECK ((approval_kind='rollback' AND rollback_hash IS NOT NULL)
             OR (approval_kind<>'rollback' AND rollback_hash IS NULL)),
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          CHECK (from_state <> to_state OR approval_kind <> 'state_transition')
        );
        CREATE TABLE public.legacy_migration_approval_authorizations (
          user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          approval_kind VARCHAR(32) NOT NULL CHECK
            (approval_kind IN ('source','question_conversion','mistake_conversion','schedule')),
          enabled BOOLEAN NOT NULL DEFAULT TRUE,
          granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          PRIMARY KEY (user_id,approval_kind)
        );
        CREATE TABLE public.legacy_migration_rollback_admins (
          user_id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE RESTRICT,
          enabled BOOLEAN NOT NULL DEFAULT TRUE,
          granted_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE TABLE public.legacy_migration_rollback_audits (
          ledger_id UUID PRIMARY KEY REFERENCES public.legacy_note_migrations(id) ON DELETE RESTRICT,
          source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
          mapping_version VARCHAR(64) NOT NULL,
          source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
          rollback_reference CHAR(64) NOT NULL CHECK (rollback_reference ~ '^[0-9a-f]{64}$'),
          rollback_json JSONB NOT NULL CHECK (jsonb_typeof(rollback_json)='object'),
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE (source_note_id,mapping_version)
        );
        CREATE TABLE public.legacy_note_migration_rejections (
          id UUID PRIMARY KEY,
          source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
          mapping_version VARCHAR(64) NOT NULL,
          source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
          snapshot_ref VARCHAR(255) NOT NULL,
          source_title VARCHAR(500) NOT NULL,
          reason VARCHAR(64) NOT NULL CHECK (reason='SOURCE_TITLE_TOO_LONG'),
          disposition VARCHAR(16) NOT NULL CHECK (disposition IN ('manual','failed')),
          migration_notes JSONB NOT NULL CHECK (jsonb_typeof(migration_notes)='array'),
          created_at TIMESTAMPTZ NOT NULL,
          idempotency_key VARCHAR(128) NOT NULL,
          actor_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          UNIQUE (source_note_id,mapping_version,idempotency_key),
          UNIQUE (source_note_id,mapping_version,source_hash,reason)
        );
        """
    )
    _sql(
        """
        ALTER TABLE public.legacy_note_migrations
          ADD CONSTRAINT fk_lnm_source_approval_event FOREIGN KEY(source_approval_event_id)
            REFERENCES public.legacy_note_migration_events(id) DEFERRABLE INITIALLY DEFERRED,
          ADD CONSTRAINT fk_lnm_question_approval_event FOREIGN KEY(question_approval_event_id)
            REFERENCES public.legacy_note_migration_events(id) DEFERRABLE INITIALLY DEFERRED,
          ADD CONSTRAINT fk_lnm_mistake_approval_event FOREIGN KEY(mistake_approval_event_id)
            REFERENCES public.legacy_note_migration_events(id) DEFERRABLE INITIALLY DEFERRED,
          ADD CONSTRAINT fk_lnm_schedule_approval_event FOREIGN KEY(schedule_approval_event_id)
            REFERENCES public.legacy_note_migration_events(id) DEFERRABLE INITIALLY DEFERRED,
          ADD CONSTRAINT fk_lnm_transition_event FOREIGN KEY(transition_event_id)
            REFERENCES public.legacy_note_migration_events(id) DEFERRABLE INITIALLY DEFERRED,
          ADD CONSTRAINT fk_lnm_rollback_event FOREIGN KEY(rollback_event_id)
            REFERENCES public.legacy_note_migration_events(id) DEFERRABLE INITIALLY DEFERRED;
        """
    )
    _sql(
        """
        CREATE TABLE legacy_migration.legacy_migration_guard_nonces (
          nonce TEXT PRIMARY KEY CHECK (nonce ~ '^[0-9a-f]{32}$'),
          txid BIGINT NOT NULL, "session_user" VARCHAR(128) NOT NULL,
          op VARCHAR(16) NOT NULL CHECK (op IN ('INSERT','UPDATE')),
          table_schema VARCHAR(128) NOT NULL, table_name VARCHAR(128) NOT NULL,
          ledger_id UUID NOT NULL, source_note_id UUID NOT NULL,
          mapping_version VARCHAR(64) NOT NULL,
          expected_source_hash CHAR(64) NOT NULL CHECK (expected_source_hash ~ '^[0-9a-f]{64}$'),
          expected_from TEXT NULL, expected_to TEXT NOT NULL,
          target_bundle_hash CHAR(64) NULL CHECK (target_bundle_hash IS NULL OR target_bundle_hash ~ '^[0-9a-f]{64}$'),
          event_id UUID NULL, approval_kind VARCHAR(32) NULL, actor_id UUID NULL,
          rollback_hash CHAR(64) NULL CHECK (rollback_hash IS NULL OR rollback_hash ~ '^[0-9a-f]{64}$'),
          payload_hash CHAR(64) NOT NULL CHECK (payload_hash ~ '^[0-9a-f]{64}$'),
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(), consumed_at TIMESTAMPTZ NULL,
          UNIQUE(txid,nonce)
        );
        ALTER TABLE legacy_migration.legacy_migration_guard_nonces OWNER TO legacy_migration_owner;
        REVOKE ALL ON legacy_migration.legacy_migration_guard_nonces
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner,
            legacy_migration_maintenance_runner, legacy_note_verifier;
        REVOKE TRUNCATE ON legacy_migration.legacy_migration_guard_nonces
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner,
            legacy_note_verifier, legacy_migration_maintenance_runner, legacy_migration_owner;
        """
    )
    _sql(
        """
        CREATE FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(
          p_cutoff TIMESTAMPTZ, p_limit INTEGER
        ) RETURNS INTEGER LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE v_deleted INTEGER;
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_migration_maintenance_runner'
             OR p_cutoff IS NULL OR p_limit IS NULL OR p_limit < 1 OR p_limit > 10000 THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_NONCE_CLEANUP_NOT_AUTHORIZED';
          END IF;
          WITH doomed AS (
            SELECT nonce
              FROM legacy_migration.legacy_migration_guard_nonces
             WHERE consumed_at IS NOT NULL AND consumed_at < p_cutoff
             ORDER BY consumed_at, nonce
             FOR UPDATE SKIP LOCKED
             LIMIT p_limit
          )
          DELETE FROM legacy_migration.legacy_migration_guard_nonces n
           USING doomed d
           WHERE n.nonce=d.nonce;
          GET DIAGNOSTICS v_deleted = ROW_COUNT;
          RETURN v_deleted;
        END $$;
        """
    )
    _sql(
        """
        CREATE FUNCTION legacy_migration.set_legacy_transition_marker(
          p_op TEXT,p_table_schema TEXT,p_table_name TEXT,p_ledger_id UUID,
          p_source_note_id UUID,p_mapping_version VARCHAR(64),p_expected_source_hash TEXT,
          p_expected_from TEXT,p_expected_to TEXT,p_target_bundle_hash TEXT,p_event_id UUID,
          p_approval_kind TEXT,p_actor_id UUID,p_rollback_hash TEXT)
        RETURNS VOID LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE v_nonce TEXT; v_marker JSONB; v_payload_hash CHAR(64);
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
             OR NOT pg_catalog.pg_has_role(session_user,'legacy_note_adapter','member') THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_CALLER_NOT_AUTHORIZED';
          END IF;
          IF p_op NOT IN ('INSERT','UPDATE') OR p_table_schema<>'public'
             OR p_table_name NOT IN ('legacy_note_migrations','legacy_note_migration_events','legacy_migration_rollback_audits')
             OR p_expected_source_hash IS NULL OR octet_length(p_expected_source_hash)<>64
             OR p_expected_source_hash !~ '^[0-9a-f]{64}$' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_BINDING_INVALID';
          END IF;
          v_nonce:=pg_catalog.encode(public.gen_random_bytes(16),'hex');
          v_marker:=pg_catalog.jsonb_build_object(
            'nonce',v_nonce,'txid',pg_catalog.txid_current()::text,'op',p_op,
            'table_schema',p_table_schema,'table_name',p_table_name,
            'ledger_id',p_ledger_id::text,'source_note_id',p_source_note_id::text,
            'mapping_version',p_mapping_version,'expected_source_hash',p_expected_source_hash,
            'expected_from',p_expected_from,'expected_to',p_expected_to,
            'target_bundle_hash',p_target_bundle_hash,'event_id',p_event_id::text,
            'approval_kind',p_approval_kind,'actor_id',p_actor_id::text,'rollback_hash',p_rollback_hash);
          v_payload_hash:=pg_catalog.encode(public.digest(pg_catalog.convert_to(v_marker::text,'UTF8'),'sha256'),'hex');
          INSERT INTO legacy_migration.legacy_migration_guard_nonces(
            nonce,txid,"session_user",op,table_schema,table_name,ledger_id,source_note_id,
            mapping_version,expected_source_hash,expected_from,expected_to,target_bundle_hash,
            event_id,approval_kind,actor_id,rollback_hash,payload_hash)
          VALUES(v_nonce,pg_catalog.txid_current(),session_user,p_op,p_table_schema,p_table_name,
            p_ledger_id,p_source_note_id,p_mapping_version,p_expected_source_hash::char(64),
            p_expected_from,p_expected_to,p_target_bundle_hash::char(64),p_event_id,p_approval_kind,
            p_actor_id,p_rollback_hash::char(64),v_payload_hash);
          PERFORM pg_catalog.set_config('app.legacy_transition_guard',v_marker::text,true);
        END $$;
        CREATE FUNCTION legacy_migration.validate_and_consume_transition_marker(
          p_marker JSONB,p_tg_op TEXT,p_tg_table_schema TEXT,p_tg_table_name TEXT)
        RETURNS VOID LANGUAGE plpgsql SECURITY DEFINER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE r legacy_migration.legacy_migration_guard_nonces%ROWTYPE;
          keys TEXT[]:=ARRAY['nonce','txid','op','table_schema','table_name','ledger_id','source_note_id','mapping_version','expected_source_hash','expected_from','expected_to','target_bundle_hash','event_id','approval_kind','actor_id','rollback_hash'];
          v_hash CHAR(64);
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner'
             OR p_marker IS NULL OR jsonb_typeof(p_marker)<>'object'
             OR NOT (p_marker ?& keys)
             OR (SELECT count(*) FROM jsonb_object_keys(p_marker))<>cardinality(keys)
             OR EXISTS (SELECT 1 FROM jsonb_object_keys(p_marker) k WHERE NOT (k=ANY(keys)))
             OR p_marker->>'txid' IS DISTINCT FROM pg_catalog.txid_current()::text
             OR p_marker->>'op' IS DISTINCT FROM p_tg_op
             OR p_marker->>'table_schema' IS DISTINCT FROM p_tg_table_schema
             OR p_marker->>'table_name' IS DISTINCT FROM p_tg_table_name THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_CONTEXT_REJECTED';
          END IF;
          v_hash:=pg_catalog.encode(public.digest(pg_catalog.convert_to(p_marker::text,'UTF8'),'sha256'),'hex');
          SELECT * INTO r FROM legacy_migration.legacy_migration_guard_nonces
           WHERE nonce=p_marker->>'nonce' FOR UPDATE;
          IF NOT FOUND OR r.consumed_at IS NOT NULL OR r.txid<>pg_catalog.txid_current()
             OR r."session_user"<>session_user OR r.payload_hash<>v_hash
             OR r.op<>p_tg_op OR r.table_schema<>p_tg_table_schema OR r.table_name<>p_tg_table_name
             OR r.ledger_id::text<>p_marker->>'ledger_id' OR r.source_note_id::text<>p_marker->>'source_note_id'
             OR r.mapping_version<>p_marker->>'mapping_version' OR r.expected_source_hash<>p_marker->>'expected_source_hash' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_NONCE_REJECTED';
          END IF;
          UPDATE legacy_migration.legacy_migration_guard_nonces SET consumed_at=now()
           WHERE nonce=r.nonce AND consumed_at IS NULL;
          IF NOT FOUND THEN RAISE EXCEPTION 'LEGACY_MIGRATION_NONCE_REPLAY'; END IF;
        END $$;
        """
    )
    _sql(
        """
        CREATE FUNCTION legacy_migration.guard_legacy_note_migration()
        RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE m JSONB;
        BEGIN
          IF current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_DIRECT_LEDGER_MUTATION_REJECTED';
          END IF;
          IF TG_OP='DELETE' THEN RAISE EXCEPTION 'LEGACY_MIGRATION_LEDGER_DELETE_REJECTED'; END IF;
          BEGIN m:=pg_catalog.current_setting('app.legacy_transition_guard',true)::jsonb;
          EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_INVALID'; END;
          PERFORM legacy_migration.validate_and_consume_transition_marker(m,TG_OP,TG_TABLE_SCHEMA,TG_TABLE_NAME);
          IF TG_OP='UPDATE' AND NEW.canonical_payload IS DISTINCT FROM OLD.canonical_payload THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_CANONICAL_PAYLOAD_IMMUTABLE';
          END IF;
          RETURN COALESCE(NEW,OLD);
        END $$;
        CREATE FUNCTION legacy_migration.guard_legacy_note_migration_event()
        RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE m JSONB;
        BEGIN
          IF TG_OP <> 'INSERT' OR current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_EVENT_APPEND_ONLY';
          END IF;
          BEGIN m:=pg_catalog.current_setting('app.legacy_transition_guard',true)::jsonb;
          EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_INVALID'; END;
          PERFORM legacy_migration.validate_and_consume_transition_marker(m,TG_OP,TG_TABLE_SCHEMA,TG_TABLE_NAME);
          RETURN NEW;
        END $$;
        CREATE FUNCTION legacy_migration.guard_legacy_migration_rollback_audit()
        RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        DECLARE m JSONB;
        BEGIN
          IF TG_OP <> 'INSERT' OR current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_ROLLBACK_AUDIT_IMMUTABLE';
          END IF;
          BEGIN m:=pg_catalog.current_setting('app.legacy_transition_guard',true)::jsonb;
          EXCEPTION WHEN OTHERS THEN RAISE EXCEPTION 'LEGACY_MIGRATION_MARKER_INVALID'; END;
          PERFORM legacy_migration.validate_and_consume_transition_marker(m,TG_OP,TG_TABLE_SCHEMA,TG_TABLE_NAME);
          RETURN NEW;
        END $$;
        CREATE FUNCTION legacy_migration.guard_legacy_note_migration_rejection()
        RETURNS TRIGGER LANGUAGE plpgsql SECURITY INVOKER
        SET search_path=pg_catalog,legacy_migration
        AS $$
        BEGIN
          IF TG_OP <> 'INSERT' OR current_user IS DISTINCT FROM 'legacy_migration_owner'
             OR session_user IS DISTINCT FROM 'legacy_note_adapter_runner' THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_REJECTION_IMMUTABLE';
          END IF;
          RETURN NEW;
        END $$;
        """
    )
    _sql(
        """
        CREATE TRIGGER trg_lnm_guard BEFORE INSERT OR UPDATE OR DELETE
          ON public.legacy_note_migrations FOR EACH ROW
          EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration();
        CREATE TRIGGER trg_lnm_event_guard BEFORE INSERT OR UPDATE OR DELETE
          ON public.legacy_note_migration_events FOR EACH ROW
          EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_event();
        CREATE TRIGGER trg_lnm_event_no_truncate BEFORE TRUNCATE
          ON public.legacy_note_migration_events FOR EACH STATEMENT
          EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_event();
        CREATE TRIGGER trg_lnm_rollback_guard BEFORE INSERT OR UPDATE OR DELETE
          ON public.legacy_migration_rollback_audits FOR EACH ROW
          EXECUTE FUNCTION legacy_migration.guard_legacy_migration_rollback_audit();
        CREATE TRIGGER trg_lnm_rollback_no_truncate BEFORE TRUNCATE
          ON public.legacy_migration_rollback_audits FOR EACH STATEMENT
          EXECUTE FUNCTION legacy_migration.guard_legacy_migration_rollback_audit();
        CREATE TRIGGER trg_lnm_rejection_guard BEFORE INSERT OR UPDATE OR DELETE
          ON public.legacy_note_migration_rejections FOR EACH ROW
          EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_rejection();
        CREATE TRIGGER trg_lnm_rejection_no_truncate BEFORE TRUNCATE
          ON public.legacy_note_migration_rejections FOR EACH STATEMENT
          EXECUTE FUNCTION legacy_migration.guard_legacy_note_migration_rejection();
        """
    )
    _sql(
        """
        CREATE SCHEMA IF NOT EXISTS legacy_migration AUTHORIZATION legacy_migration_owner;
        REVOKE CREATE ON SCHEMA legacy_migration FROM PUBLIC;
        GRANT USAGE ON SCHEMA legacy_migration TO legacy_note_adapter,
          legacy_note_verifier, legacy_migration_maintenance_runner;
        GRANT USAGE ON SCHEMA public TO legacy_migration_owner;
        """
    )
    _sql(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname='legacy_note_migration_state') THEN
            CREATE TYPE public.legacy_note_migration_state AS ENUM
              ('pending_mapping','ready','migrated_active','migrated_paused',
               'retained_public_only','failed','rolled_back');
          END IF;
        END $$;
        """
    )

    # Existing draft/review tables retain their compatibility columns.  The
    # canonical successor columns are additive and are used by this adapter.
    _sql(
        """
        ALTER TABLE draft_items
          ADD COLUMN IF NOT EXISTS source_hash CHAR(64),
          ADD COLUMN IF NOT EXISTS approved_by UUID,
          ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
          ADD COLUMN IF NOT EXISTS conversion_sequence INTEGER,
          ADD COLUMN IF NOT EXISTS target_question_id UUID,
          ADD COLUMN IF NOT EXISTS target_mistake_id UUID;
        ALTER TABLE draft_items DROP CONSTRAINT IF EXISTS ck_draft_items_source;
        ALTER TABLE draft_items ADD CONSTRAINT ck_draft_items_source
          CHECK ((draft_type='question' AND source_type IN ('manual','legacy_note'))
              OR (draft_type='mistake' AND source_type IN ('question','question_draft','legacy_note')));
        ALTER TABLE draft_items ADD CONSTRAINT ck_legacy_draft_source_hash
          CHECK (source_hash IS NULL OR source_hash ~ '^[0-9a-f]{64}$');
        ALTER TABLE draft_items ADD CONSTRAINT ck_legacy_draft_conversion
          CHECK (conversion_sequence IS NULL OR conversion_sequence > 0);
        """
    )
    _sql(
        """
        ALTER TABLE public.question_sources DROP CONSTRAINT IF EXISTS ck_question_sources_type;
        ALTER TABLE public.question_sources ADD CONSTRAINT ck_question_sources_type
          CHECK (source_type IN ('manual','book','exam','note','url','other'));
        """
    )
    _sql(
        """
        ALTER TABLE review_items ADD COLUMN IF NOT EXISTS mistake_id UUID;
        DO $$
        BEGIN
          UPDATE review_items
             SET mistake_id = NULLIF(target_id,'')::uuid
           WHERE mistake_id IS NULL AND target_type='mistake'
             AND target_id ~ '^[0-9a-fA-F-]{36}$';
          IF EXISTS (SELECT 1 FROM review_items WHERE mistake_id IS NULL) THEN
            RAISE EXCEPTION 'LEGACY_MIGRATION_REVIEW_ITEM_CANONICAL_FK_REQUIRED';
          END IF;
        END $$;
        ALTER TABLE review_items ALTER COLUMN mistake_id SET NOT NULL;
        ALTER TABLE review_items ADD CONSTRAINT fk_review_items_mistake
          FOREIGN KEY (mistake_id) REFERENCES mistakes(id) ON DELETE RESTRICT;
        CREATE UNIQUE INDEX IF NOT EXISTS uq_review_items_mistake_id ON review_items(mistake_id);
        """
    )

    _sql(
        """
        CREATE TYPE legacy_migration.legacy_note_migration_target_bundle AS (
          target_question_draft_item_id UUID,
          target_question_draft_id UUID,
          target_question_id UUID,
          target_question_source_id UUID,
          target_mistake_draft_item_id UUID,
          target_mistake_draft_id UUID,
          target_mistake_id UUID,
          target_review_item_id UUID,
          target_qkp_ids INTEGER[],
          target_projection_ids INTEGER[]
        );
        """
    )
    _sql(
        """
        CREATE TABLE legacy_migration.allowed_legacy_note_migration_transitions (
          from_state public.legacy_note_migration_state NOT NULL,
          to_state public.legacy_note_migration_state NOT NULL,
          PRIMARY KEY (from_state,to_state)
        );
        INSERT INTO legacy_migration.allowed_legacy_note_migration_transitions VALUES
          ('pending_mapping','ready'),('pending_mapping','failed'),
          ('pending_mapping','retained_public_only'),
          ('ready','migrated_active'),('ready','migrated_paused'),('ready','failed'),
          ('migrated_paused','migrated_active'),('migrated_paused','rolled_back'),
          ('migrated_active','rolled_back'),('failed','pending_mapping');
        """
    )
    _sql(
        """
        CREATE TABLE public.legacy_note_migrations (
          id UUID PRIMARY KEY,
          source_note_id UUID NOT NULL REFERENCES public.notes(id) ON DELETE RESTRICT,
          source_slug VARCHAR(255) NOT NULL,
          source_title VARCHAR(500) NOT NULL,
          source_url VARCHAR(500) NOT NULL,
          source_status VARCHAR(20) NOT NULL,
          source_hidden BOOLEAN NOT NULL,
          source_revision INTEGER NOT NULL CHECK (source_revision > 0),
          source_hash CHAR(64) NOT NULL CHECK (source_hash ~ '^[0-9a-f]{64}$'),
          snapshot_ref VARCHAR(255) NOT NULL,
          mapping_version VARCHAR(64) NOT NULL,
          idempotency_key VARCHAR(128) NOT NULL,
          target_question_id UUID NULL REFERENCES public.questions(id) ON DELETE RESTRICT,
          target_question_source_id UUID NULL REFERENCES public.question_sources(id) ON DELETE RESTRICT,
          target_qkp_ids INTEGER[] NULL,
          target_mistake_id UUID NULL REFERENCES public.mistakes(id) ON DELETE RESTRICT,
          target_projection_ids INTEGER[] NULL,
          target_review_item_id UUID NULL REFERENCES public.review_items(id) ON DELETE RESTRICT,
          target_question_draft_item_id UUID NULL REFERENCES public.draft_items(id) ON DELETE RESTRICT,
          target_question_draft_id UUID NULL REFERENCES public.question_drafts(id) ON DELETE RESTRICT,
          target_mistake_draft_item_id UUID NULL REFERENCES public.draft_items(id) ON DELETE RESTRICT,
          target_mistake_draft_id UUID NULL REFERENCES public.mistake_drafts(id) ON DELETE RESTRICT,
          state public.legacy_note_migration_state NOT NULL,
          target_bundle_hash CHAR(64) NULL CHECK (target_bundle_hash IS NULL OR target_bundle_hash ~ '^[0-9a-f]{64}$'),
          manual_review_required BOOLEAN NOT NULL DEFAULT TRUE,
          legacy_ef DOUBLE PRECISION NOT NULL CHECK (legacy_ef::text NOT IN ('NaN','Infinity','-Infinity')),
          legacy_ef_bits CHAR(16) NOT NULL CHECK (legacy_ef_bits ~ '^[0-9a-f]{16}$'),
          legacy_interval INTEGER NOT NULL CHECK (legacy_interval >= 0),
          legacy_repetitions INTEGER NOT NULL CHECK (legacy_repetitions >= 0),
          legacy_next_review DATE NULL,
          legacy_last_reviewed TIMESTAMP NULL,
          mapped_next_review_at TIMESTAMPTZ NULL,
          mapped_last_reviewed_at TIMESTAMPTZ NULL,
          legacy_review_json JSONB NOT NULL CHECK (jsonb_typeof(legacy_review_json)='object'),
          canonical_payload JSONB NOT NULL CHECK (jsonb_typeof(canonical_payload)='object'),
          migration_notes JSONB NOT NULL CHECK (jsonb_typeof(migration_notes)='array'),
          approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          approved_at TIMESTAMPTZ NULL,
          source_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          source_approved_at TIMESTAMPTZ NULL,
          source_approval_sequence INTEGER NULL CHECK (source_approval_sequence > 0),
          question_conversion_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          question_conversion_approved_at TIMESTAMPTZ NULL,
          question_conversion_sequence INTEGER NULL CHECK (question_conversion_sequence > 0),
          mistake_conversion_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          mistake_conversion_approved_at TIMESTAMPTZ NULL,
          mistake_conversion_sequence INTEGER NULL CHECK (mistake_conversion_sequence > 0),
          schedule_approved_by UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          schedule_approved_at TIMESTAMPTZ NULL,
          schedule_approval_sequence INTEGER NULL CHECK (schedule_approval_sequence > 0),
          rollback_actor_id UUID NULL REFERENCES public.users(id) ON DELETE RESTRICT,
          rollback_reference CHAR(64) NULL CHECK (rollback_reference IS NULL OR rollback_reference ~ '^[0-9a-f]{64}$'),
          source_approval_event_id UUID NULL,
          question_approval_event_id UUID NULL,
          mistake_approval_event_id UUID NULL,
          schedule_approval_event_id UUID NULL,
          transition_event_id UUID NULL,
          rollback_event_id UUID NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE (source_note_id,mapping_version), UNIQUE (idempotency_key),
          UNIQUE (target_question_id), UNIQUE (target_question_source_id),
          UNIQUE (target_mistake_id), UNIQUE (target_review_item_id),
          UNIQUE (target_question_draft_item_id), UNIQUE (target_question_draft_id),
          UNIQUE (target_mistake_draft_item_id), UNIQUE (target_mistake_draft_id)
        );
        CREATE INDEX idx_legacy_note_migrations_state
          ON public.legacy_note_migrations(state,updated_at);
        CREATE INDEX idx_legacy_note_migrations_source_hash
          ON public.legacy_note_migrations(source_hash);
        """
    )
    _sql(
        """
        ALTER TABLE public.legacy_note_migrations
          ADD CONSTRAINT ck_legacy_note_migrations_retained_shape CHECK (
            state <> 'retained_public_only' OR (
              source_status='published' AND source_hidden=FALSE
              AND target_question_draft_item_id IS NULL AND target_question_draft_id IS NULL
              AND target_question_id IS NULL AND target_question_source_id IS NULL
              AND target_mistake_draft_item_id IS NULL AND target_mistake_draft_id IS NULL
              AND target_mistake_id IS NULL AND target_review_item_id IS NULL
              AND target_qkp_ids IS NULL AND target_projection_ids IS NULL
              AND target_bundle_hash IS NULL
              AND mapped_next_review_at IS NULL AND mapped_last_reviewed_at IS NULL
              AND rollback_actor_id IS NULL AND rollback_reference IS NULL AND rollback_event_id IS NULL
              AND source_approved_by IS NOT NULL AND source_approved_at IS NOT NULL
              AND source_approval_sequence IS NOT NULL AND source_approval_event_id IS NOT NULL
              AND approved_by IS NOT DISTINCT FROM source_approved_by
              AND approved_at IS NOT DISTINCT FROM source_approved_at
              AND question_conversion_approved_by IS NULL AND question_conversion_approved_at IS NULL
              AND question_conversion_sequence IS NULL AND question_approval_event_id IS NULL
              AND mistake_conversion_approved_by IS NULL AND mistake_conversion_approved_at IS NULL
              AND mistake_conversion_sequence IS NULL AND mistake_approval_event_id IS NULL
              AND schedule_approved_by IS NULL AND schedule_approved_at IS NULL
              AND schedule_approval_sequence IS NULL AND schedule_approval_event_id IS NULL
            )
          );
        """
    )
    _flush_deferred()
    _sql(
        """
        ALTER TYPE legacy_migration.legacy_note_migration_target_bundle OWNER TO legacy_migration_owner;
        ALTER TABLE legacy_migration.allowed_legacy_note_migration_transitions OWNER TO legacy_migration_owner;
        ALTER TABLE public.legacy_note_migrations OWNER TO legacy_migration_owner;
        ALTER TABLE public.legacy_note_migration_events OWNER TO legacy_migration_owner;
        ALTER TABLE public.legacy_migration_approval_authorizations OWNER TO legacy_migration_owner;
        ALTER TABLE public.legacy_migration_rollback_admins OWNER TO legacy_migration_owner;
        ALTER TABLE public.legacy_migration_rollback_audits OWNER TO legacy_migration_owner;
        ALTER TABLE public.legacy_note_migration_rejections OWNER TO legacy_migration_owner;
        REVOKE ALL ON public.legacy_note_migrations, public.legacy_note_migration_events,
          public.legacy_migration_approval_authorizations, public.legacy_migration_rollback_admins,
          public.legacy_migration_rollback_audits, public.legacy_note_migration_rejections
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner,
            legacy_migration_maintenance_runner, legacy_note_verifier;
        GRANT SELECT ON public.legacy_note_migrations, public.legacy_note_migration_events,
          public.legacy_migration_approval_authorizations, public.legacy_migration_rollback_admins,
          public.legacy_migration_rollback_audits, public.legacy_note_migration_rejections
          TO legacy_note_verifier;
        ALTER FUNCTION legacy_migration.legacy_uuid_or_null(TEXT) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.canonicalize_legacy_note(UUID) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.create_legacy_note_migration_pending(UUID,UUID,VARCHAR,TEXT,VARCHAR,VARCHAR,VARCHAR,VARCHAR,BOOLEAN,INTEGER,VARCHAR,VARCHAR,JSONB,JSONB,JSONB) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.record_legacy_note_migration_approval(UUID,TEXT,TEXT,public.legacy_note_migration_state,VARCHAR,UUID,TIMESTAMPTZ,INTEGER,INTEGER,TEXT,JSONB) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.transition_legacy_note_migration(UUID,public.legacy_note_migration_state,public.legacy_note_migration_state,UUID,TEXT,UUID,VARCHAR,TEXT,legacy_migration.legacy_note_migration_target_bundle,TEXT,TEXT,TIMESTAMPTZ,TIMESTAMPTZ,JSONB) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.load_legacy_migration_rollback_audit(UUID,UUID,VARCHAR,TEXT,TEXT,JSONB) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.record_legacy_note_migration_rejection(UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.legacy_question_options_normalize(JSONB) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.legacy_question_answer_data_expected(TEXT,TEXT) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.legacy_question_source_matches(UUID,UUID,VARCHAR,VARCHAR,VARCHAR,VARCHAR,TEXT) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.legacy_question_mirror_matches(UUID,UUID,UUID,VARCHAR,TEXT) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.guard_legacy_note_migration() OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.guard_legacy_note_migration_event() OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.guard_legacy_migration_rollback_audit() OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.guard_legacy_note_migration_rejection() OWNER TO legacy_migration_owner;
        REVOKE ALL ON FUNCTION legacy_migration.legacy_uuid_or_null(TEXT) FROM PUBLIC, app_role;
        GRANT EXECUTE ON FUNCTION legacy_migration.legacy_uuid_or_null(TEXT)
          TO legacy_note_adapter, legacy_note_verifier;
        REVOKE ALL ON FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
        GRANT EXECUTE ON FUNCTION legacy_migration.cleanup_legacy_migration_guard_nonces(TIMESTAMPTZ,INTEGER)
          TO legacy_migration_maintenance_runner;
        REVOKE ALL ON FUNCTION legacy_migration.canonicalize_legacy_note(UUID),
          legacy_migration.create_legacy_note_migration_pending(UUID,UUID,VARCHAR,TEXT,VARCHAR,VARCHAR,VARCHAR,VARCHAR,BOOLEAN,INTEGER,VARCHAR,VARCHAR,JSONB,JSONB,JSONB),
          legacy_migration.record_legacy_note_migration_approval(UUID,TEXT,TEXT,public.legacy_note_migration_state,VARCHAR,UUID,TIMESTAMPTZ,INTEGER,INTEGER,TEXT,JSONB),
          legacy_migration.transition_legacy_note_migration(UUID,public.legacy_note_migration_state,public.legacy_note_migration_state,UUID,TEXT,UUID,VARCHAR,TEXT,legacy_migration.legacy_note_migration_target_bundle,TEXT,TEXT,TIMESTAMPTZ,TIMESTAMPTZ,JSONB),
          legacy_migration.load_legacy_migration_rollback_audit(UUID,UUID,VARCHAR,TEXT,TEXT,JSONB),
          legacy_migration.record_legacy_note_migration_rejection(UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID),
          legacy_migration.legacy_question_options_normalize(JSONB),
          legacy_migration.legacy_question_answer_data_expected(TEXT,TEXT),
          legacy_migration.legacy_question_source_matches(UUID,UUID,VARCHAR,VARCHAR,VARCHAR,VARCHAR,TEXT),
          legacy_migration.legacy_question_mirror_matches(UUID,UUID,UUID,VARCHAR,TEXT)
          FROM PUBLIC, app_role, legacy_note_verifier;
        GRANT EXECUTE ON FUNCTION legacy_migration.canonicalize_legacy_note(UUID),
          legacy_migration.create_legacy_note_migration_pending(UUID,UUID,VARCHAR,TEXT,VARCHAR,VARCHAR,VARCHAR,VARCHAR,BOOLEAN,INTEGER,VARCHAR,VARCHAR,JSONB,JSONB,JSONB),
          legacy_migration.record_legacy_note_migration_approval(UUID,TEXT,TEXT,public.legacy_note_migration_state,VARCHAR,UUID,TIMESTAMPTZ,INTEGER,INTEGER,TEXT,JSONB),
          legacy_migration.transition_legacy_note_migration(UUID,public.legacy_note_migration_state,public.legacy_note_migration_state,UUID,TEXT,UUID,VARCHAR,TEXT,legacy_migration.legacy_note_migration_target_bundle,TEXT,TEXT,TIMESTAMPTZ,TIMESTAMPTZ,JSONB),
          legacy_migration.load_legacy_migration_rollback_audit(UUID,UUID,VARCHAR,TEXT,TEXT,JSONB),
          legacy_migration.record_legacy_note_migration_rejection(UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID),
          legacy_migration.legacy_question_options_normalize(JSONB),
          legacy_migration.legacy_question_answer_data_expected(TEXT,TEXT),
          legacy_migration.legacy_question_source_matches(UUID,UUID,VARCHAR,VARCHAR,VARCHAR,VARCHAR,TEXT),
          legacy_migration.legacy_question_mirror_matches(UUID,UUID,UUID,VARCHAR,TEXT)
          TO legacy_note_adapter;
        REVOKE ALL ON FUNCTION legacy_migration.guard_legacy_note_migration(),
          legacy_migration.guard_legacy_note_migration_event(),
          legacy_migration.guard_legacy_migration_rollback_audit(),
          legacy_migration.guard_legacy_note_migration_rejection()
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner,
            legacy_migration_maintenance_runner, legacy_note_verifier;
        GRANT SELECT ON public.legacy_note_migrations, public.legacy_note_migration_events,
          public.legacy_migration_approval_authorizations, public.legacy_migration_rollback_admins,
          public.legacy_migration_rollback_audits, public.legacy_note_migration_rejections
          TO legacy_note_adapter;
        GRANT SELECT, INSERT, UPDATE ON public.draft_items, public.question_drafts,
          public.questions, public.question_sources, public.question_knowledge_points,
          public.knowledge_point_links, public.mistake_drafts, public.mistakes,
          public.review_items TO legacy_note_adapter;
        GRANT USAGE, SELECT ON SEQUENCE public.knowledge_point_links_id_seq,
          public.knowledge_points_id_seq TO legacy_note_adapter;
        GRANT SELECT ON public.notes, public.note_tags, public.tags, public.users, public.subjects
          TO legacy_migration_owner;
        GRANT UPDATE ON public.notes TO legacy_migration_owner;
        GRANT DELETE ON public.draft_items, public.question_drafts, public.questions,
          public.question_sources, public.question_knowledge_points, public.mistake_drafts,
          public.mistakes, public.review_items TO legacy_migration_owner;
        REVOKE DELETE ON public.knowledge_point_links
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner,
            legacy_migration_maintenance_runner, legacy_note_verifier;
        GRANT DELETE ON public.knowledge_point_links TO legacy_migration_owner;
        GRANT SELECT ON public.capture_items, public.attempts TO legacy_migration_owner;
        GRANT SELECT ON public.draft_items, public.question_drafts, public.questions,
          public.question_sources, public.question_knowledge_points, public.mistake_drafts,
          public.mistakes, public.review_items TO legacy_migration_owner;
        GRANT SELECT ON public.subjects, public.knowledge_points TO legacy_note_adapter;
        ALTER FUNCTION legacy_migration.set_legacy_transition_marker(TEXT,TEXT,TEXT,UUID,UUID,VARCHAR,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,UUID,TEXT) OWNER TO legacy_migration_owner;
        ALTER FUNCTION legacy_migration.validate_and_consume_transition_marker(JSONB,TEXT,TEXT,TEXT) OWNER TO legacy_migration_owner;
        REVOKE ALL ON FUNCTION legacy_migration.set_legacy_transition_marker(TEXT,TEXT,TEXT,UUID,UUID,VARCHAR,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,UUID,TEXT)
          FROM PUBLIC, app_role, legacy_note_adapter_runner, legacy_note_verifier;
        GRANT EXECUTE ON FUNCTION legacy_migration.set_legacy_transition_marker(TEXT,TEXT,TEXT,UUID,UUID,VARCHAR,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,UUID,TEXT)
          TO legacy_note_adapter;
        REVOKE ALL ON FUNCTION legacy_migration.validate_and_consume_transition_marker(JSONB,TEXT,TEXT,TEXT)
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
        REVOKE ALL ON FUNCTION public.gen_random_uuid() FROM PUBLIC, app_role, legacy_note_adapter,
          legacy_note_adapter_runner, legacy_note_verifier;
        REVOKE ALL ON FUNCTION public.gen_random_bytes(integer) FROM PUBLIC, app_role, legacy_note_adapter,
          legacy_note_adapter_runner, legacy_note_verifier;
        GRANT EXECUTE ON FUNCTION public.gen_random_uuid(), public.gen_random_bytes(integer)
          TO legacy_migration_owner;
        REVOKE ALL ON FUNCTION public.digest(bytea,text) FROM PUBLIC, app_role, legacy_note_adapter,
          legacy_note_adapter_runner;
        GRANT EXECUTE ON FUNCTION public.digest(bytea,text) TO legacy_migration_owner, legacy_note_verifier, legacy_note_adapter;
        REVOKE ALL ON FUNCTION public.digest(text,text)
          FROM PUBLIC, app_role, legacy_note_adapter, legacy_note_adapter_runner, legacy_note_verifier;
        GRANT EXECUTE ON FUNCTION public.digest(text,text) TO legacy_migration_owner;
        """
    )


def downgrade() -> None:
    raise RuntimeError(
        "026_legacy_system_retirement is intentionally irreversible: it provisions "
        "cluster-level roles and extensions and restructures function privileges. "
        "Automated 'alembic downgrade' is not supported; rollback requires the "
        "documented DBA procedure (see docs/workflows/legacy-system-retirement/ "
        "and the legacy_note_migration transition rollback functions)."
    )
