-- B02 read-only historical candidate report (KP accounting for existing rows).
--
-- Purpose: prove-or-list the persisted-truth facts for repositories that never
-- saw the automatic KP-snapshot fix, WITHOUT backfilling or mutating anything.
-- It lists every active canonical Mistake, where it came from, which draft
-- carried it, via which Attempt (if any), and the actual KP set attached NOW.
--
-- Important semantics:
-- 1. An empty KP set is NOT reported as "lost" — a manual entry that sends an
--    explicit [] is authoritative; the report only makes the source provable.
-- 2. auto_from_attempt proves the snapshot source (attempt -> question); the
--    question's CURRENT KP links are listed for comparison so a human can see
--    whether the snapshot still matches the question today.
-- 3. Never automatically refills anything here; run with an explicit target
--    database and authorization, as a plain SELECT (no writes).
--
-- Read-only: run with `psql -f` against an explicitly authorized database.

SELECT
    m.id                          AS mistake_id,
    m.subject_id,
    md.draft_item_id,
    di.status                     AS draft_status,
    CASE
        WHEN md.attempt_id IS NOT NULL THEN 'auto_from_attempt'
        WHEN md.question_draft_id IS NOT NULL THEN 'manual_from_question_draft'
        ELSE 'manual_from_question'
    END                           AS origin_kind,
    md.attempt_id                 AS source_attempt_id,
    md.question_id                AS source_question_id,
    q.version                     AS question_version_now,
    -- current attached KP set on the mistake
    COALESCE(m_kp.kp_ids, '{}')   AS mistake_kp_ids_now,
    -- the question's CURRENT KP links, for comparison only
    COALESCE(q_kp.kp_ids, '{}')   AS question_kp_ids_now,
    -- provenance columns from the migration-026 draft extension (nullable)
    di.source_hash,
    di.approved_by,
    di.approved_at,
    m.updated_at
FROM mistakes m
JOIN draft_items di
     ON di.id = m.source_draft_item_id
LEFT JOIN mistake_drafts md
     ON md.draft_item_id = di.id
LEFT JOIN questions q
     ON q.id = md.question_id
JOIN LATERAL (
    SELECT ARRAY_AGG(l.knowledge_point_id ORDER BY l.knowledge_point_id) AS kp_ids
    FROM knowledge_point_links l
    WHERE l.target_type = 'mistake' AND l.target_id::uuid = m.id
) m_kp ON TRUE
JOIN LATERAL (
    SELECT ARRAY_AGG(kp.knowledge_point_id ORDER BY kp.knowledge_point_id) AS kp_ids
    FROM question_knowledge_points kp
    WHERE kp.question_id = md.question_id
) q_kp ON md.question_id IS NOT NULL
WHERE m.status = 'active'
ORDER BY m.updated_at DESC
;
