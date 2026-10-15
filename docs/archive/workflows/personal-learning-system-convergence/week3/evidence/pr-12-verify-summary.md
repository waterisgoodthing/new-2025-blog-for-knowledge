# PR-12 verification summary — PR-12-verify (independent)

agent_id: PR-12-verify · profile: senior-qa-sdet · role: verifier · date: 2026-09-25
Scope verified: migration 032, `models/note_knowledge_point.py`,
`services/note_knowledge_point_service.py`, `routers/admin_notes.py`,
`schemas/note_knowledge_point.py`, `src/lib/api/notes.ts`, `main.py` wiring.
No product code changed. Scratch DB `astra_week3_pr12_verify` only, via
`scripts/week3-scratch-guard.py`. No git writes.

## Conclusion: PASS

All four verification groups pass. No product defects (see findings for LOW/INFO process notes).

## A. Migration matrix — PASS

`scripts/week3-scratch-guard.py run --db-name astra_week3_pr12_verify -- backend/.venv/bin/python <temp>/pr12_verify_matrix.py`

| # | check | result |
| --- | --- | --- |
| A1 | fresh DB has no notes / note_knowledge_points / knowledge_point_links | PASS |
| A2 | fresh → 032 upgrade exits 0, revision 032 | PASS |
| A3 | `alembic heads` single head = 032 | PASS |
| A4 | note_id UUID NOT NULL, knowledge_point_id int4 NOT NULL, created_at NOT NULL | PASS |
| A4 | composite PK (note_id, knowledge_point_id); duplicate rejected by PK | PASS |
| A4 | two FKs (`notes`, `knowledge_points`) both `confdeltype='c'` (ON DELETE CASCADE) | PASS |
| A4 | `idx_note_knowledge_points_kp (knowledge_point_id, note_id)` + PK index | PASS |
| A5 | delete note → link rows cascade away; delete kp → link rows cascade away | PASS |
| B | 032 → 031 downgrade exits 0, table/index dropped, current 031 | PASS |
| C | 031 → 032 re-upgrade exits 0, table/index restored | PASS |
| D | `knowledge_point_links` full snapshot (columns/PK/FK/indexes) identical at 031 vs 032 | PASS |

Evidence: `evidence/migrations/pr-12-verify-migration-matrix.txt`

## B. API contract & permissions — PASS

`backend/tests/test_pr12_verify_api.py` (5) + `backend/tests/test_pr12_verify_concurrency.py` (1), guarded.

| # | check | result |
| --- | --- | --- |
| B1 | admin link 200; duplicate link 200 (idempotent); unlink 204; repeat unlink 204 | PASS |
| B2 | missing note / missing KP → 404 on link, unlink and both list routes | PASS |
| B2 | anonymous on all four routes → 401/403 | PASS |
| B3 | concurrent duplicate link: deterministic service race + direct `IntegrityError` branch → no 500, idempotent | PASS |
| B3 | real parallel admin double-POST (httpx ASGITransport, isolated process) → both 200, no 500 | PASS |
| B4 | note→KP list returns the linked KP; KP→note list returns the linked note (correct direction) | PASS |
| B5 | client paths/methods match router: link/unlink `/{note_id}/knowledge-points/{kp_id}` POST/DELETE, note→KP GET `/{note_id}/knowledge-points`, KP→notes GET `/knowledge-points/{kp_id}/notes` | PASS |
| B5 | client DTO fields == backend schemas (`NoteKnowledgePointLinkOut`, `KnowledgePointNoteItem`) | PASS |
| B5 | client vitest 6/6; `npx tsc --noEmit` exit 0 | PASS |

Evidence: `evidence/tests/pr-12-verify-api.txt`, `pr-12-verify-client-vitest.txt`, `pr-12-verify-tsc.txt`, `pr-12-verify-source-search.txt`

## C. Regression — PASS

Guarded pytest, 145 passed:
`test_week3_contracts.py`, `test_security_settings_guards.py`, `test_pr09_migration.py`,
`test_batch7_compatibility.py`, `test_manage_write_permissions.py`,
`test_pr09_verify_api_contract.py` (note-type create still allowed, reads OK),
`test_taxonomy_service.py`, `test_question_domain.py` (legacy KnowledgePointLink writes),
`test_pr10_kp_analytics_service.py` (legacy KnowledgePointLink reads),
`test_pr10_kp_analytics_contract.py`.

| # | check | result |
| --- | --- | --- |
| C1 | Note writing path (create/update/delete auth + successful create) no regression | PASS |
| C2 | legacy `knowledge_point_links` read/write behavior no regression | PASS |
| C3 | `test_week3_contracts.py` still green | PASS (in 145-passed batch) |

Evidence: `evidence/tests/pr-12-verify-regression.txt`

## D. Source search — PASS

- No PR-12 file touches `knowledge_point_links`; migration 032 only creates/drops `note_knowledge_points`.
- No subject/学科 enforcement in PR-12 service/router/model/schema (docstring-only deferral note).
- Client DTO fields match backend schema fields; response-contract fields identical.

Evidence: `evidence/tests/pr-12-verify-source-search.txt`

## Findings

`evidence/reviews/pr-12-findings.md` — PR12V-01 (LOW, evidence layout), PR12V-02 (LOW, client union narrowing), PR12V-03/04 (INFO). No BLOCKER/HIGH/MEDIUM.

## Unresolved / boundaries

- Subject normalisation deferred by design (out of PR-12 scope).
- Concurrent `unlink` was not raced in this pass (benign expected; not directly evidenced).
- Production migration / data / commit / push remain NOT_AUTHORIZED and were not performed.
- Evidence-location split (root `week3/evidence/` vs canonical docs path) needs a main-agent decision.

## New verifier test files (only additions)

- `backend/tests/test_pr12_verify_api.py`
- `backend/tests/test_pr12_verify_concurrency.py`
