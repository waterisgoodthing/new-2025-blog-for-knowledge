-- Week 3 Gate — migration 032 schema/integrity queries
-- agent_id: GATE-seed-verify  DB: astra_week3_gate_mig (fresh, 030->032->downgrade->re-upgrade)

-- 1. note_knowledge_points schema shape (W3-D04: note_id UUID PK, knowledge_point_id INTEGER PK)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'note_knowledge_points'
ORDER BY ordinal_position;

-- 2. composite PK + FK constraints + cascade
SELECT con.conname, pg_get_constraintdef(con.oid)
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname = 'note_knowledge_points'
ORDER BY con.contype, con.conname;

-- 3. mistakes visibility CHECK now allows 'public' (031)
SELECT pg_get_constraintdef(con.oid)
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname = 'mistakes' AND con.conname = 'ck_mistakes_visibility';

-- 4. one alembic head at 032 (verified via alembic heads; not a SQL query)

-- 5. cascade proof: deleting a KP cascades to note_knowledge_points (raw FK check below is
--    performed by the Q5 script on astra_week3_gate: duplicate PK + FK IntegrityError).