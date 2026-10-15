-- Week 3 Gate Q4: public mistakes canonical ownership (negative + Empty honesty)
-- agent_id: GATE-seed-verify (senior-qa-sdet)  DB: astra_week3_gate (guarded)

-- 1. Canonical public rows = exactly the 2 active+public canonical Mistakes.
SELECT count(*) AS public_canonical
FROM mistakes
WHERE status = 'active' AND visibility = 'public';
-- => 2

-- 2. Private canonical rows exist but must NOT be served.
SELECT count(*) AS private_canonical
FROM mistakes
WHERE status = 'active' AND visibility = 'private';
-- => 4

-- 3. Legacy Note mistakes exist (frozen path) but must NOT be served publicly.
SELECT count(*) AS legacy_note_mistakes
FROM notes
WHERE type = 'mistake';
-- => 2

-- 4. Empty honesty: with 0 public rows the public endpoint must report
--    empty=true + message (verified via API after UPDATE visibility='private'):
--    {"items":[],"total":0,"page":1,"size":20,"empty":true,
--     "message":"No published mistakes yet."}
--    Restored afterwards; empty=false, total=2 again.

-- 5. Canonical Note<->KP persisted via migration 032:
SELECT count(*) AS note_kp_links
FROM note_knowledge_points
WHERE note_id = (SELECT id FROM notes WHERE slug = 'gate-canonical-note');
-- => 1 (pre-linked to GATE Alpha)