# PR-12 — Canonical Note ↔ KnowledgePoint relation — self evidence

agent_id: PR-12-impl · profile: senior-backend-engineer · role: implementer · date: 2026-09-25

## Delivered

| File | Change |
| --- | --- |
| `backend/alembic/versions/032_note_knowledge_points.py` | New migration 032 (`revision="032"`, `down_revision="031"`): `note_knowledge_points` (note_id UUID FK→notes CASCADE, knowledge_point_id INTEGER FK→knowledge_points CASCADE, composite PK, `created_at`), index `idx_note_knowledge_points_kp`. Upgrade/downgrade symmetric; does not touch `knowledge_point_links`. |
| `backend/app/models/note_knowledge_point.py` | New `NoteKnowledgePoint` model (composite PK, cascade FKs, KP lookup index). |
| `backend/app/models/__init__.py`, `backend/app/models/registry.py` | Register the model for `SCHEMA_LIFECYCLE_METADATA`. |
| `backend/app/schemas/note_knowledge_point.py` | `NoteKnowledgePointLinkOut`, `KnowledgePointNoteItem`. |
| `backend/app/services/note_knowledge_point_service.py` | link/unlink/list service with 404 + idempotent duplicate/concurrent semantics. |
| `backend/app/routers/admin_notes.py` | New admin-only router `/api/admin/notes` (link/unlink/note→KP list/KP→note list). |
| `backend/main.py` | Register `admin_notes` router; pin `EXPECTED_ALEMBIC_REVISION = "032"`. |
| `backend/tests/test_security_settings_guards.py`, `backend/tests/test_pr09_migration.py` | Sync revision assertion to `032` (expectation only; PR-09 logic untouched). |
| `backend/tests/test_pr12_note_knowledge_points_contract.py` | 20 no-DB tests: migration shape, model shape, route/admin wiring, pin. |
| `backend/tests/test_pr12_note_knowledge_points_service.py` | 15 DB tests incl. cascade, duplicate/concurrent IntegrityError, polymorph untouched. |
| `backend/tests/test_pr12_note_knowledge_points_http.py` | 8 DB HTTP tests: anonymous 401/403, admin 200/204, 404 negatives. |
| `scripts/pr12_verify_migration_matrix.py` | Guard-run migration matrix (fresh/031↔032/cascade/shape). |

## API contract (admin-only, session auth via `get_current_admin`)

| Method | Path | Semantics |
| --- | --- | --- |
| POST | `/api/admin/notes/{note_id}/knowledge-points/{knowledge_point_id}` | Link. 200 `{note_id,knowledge_point_id,linked:true}`. Duplicate link (incl. concurrent unique-key race) → idempotent 200. Missing note/KP → 404. |
| DELETE | `/api/admin/notes/{note_id}/knowledge-points/{knowledge_point_id}` | Unlink. 204. Absent relation → idempotent 204. Missing note/KP → 404. |
| GET | `/api/admin/notes/{note_id}/knowledge-points` | Note → KP list (`KnowledgePointOut`). Missing note → 404. |
| GET | `/api/admin/notes/knowledge-points/{knowledge_point_id}/notes` | KP → note list (`KnowledgePointNoteItem`). Missing KP → 404. |
| — | any | Unauthenticated → 401/403 (router-level `get_current_admin`). |

No subject-consistency rule is enforced (`Note.subject` stays free text); recorded as deferred normalisation (PR-12 excluded scope).

## Evidence

- `evidence/tests/pr-12-targeted-pytest.txt` — **43 passed** (contract 20 + service 15 + http 8), guard-run.
- `evidence/tests/pr-12-regression-nodeb.txt` — **80 passed** (`test_week3_contracts.py` + `test_security_settings_guards.py` + `test_pr09_migration.py`).
- `evidence/tests/pr-12-regression-db.txt` — **42 passed** (taxonomy, PR-10 analytics, PR-09 permissions, manage write permissions).
- `evidence/migrations/pr-12-summary.log` — **MIGRATION_MATRIX_ALL_PASS**.
- `evidence/migrations/pr-12-migration-matrix-run.log` + `pr-12-{heads,fresh-032,schema-shape,downgrade-reupgrade}.log`.

Scratch DBs: `astra_week3_pr12_mig` (matrix, recreated fresh) and `astra_week3_pr12` (tests), both via
`scripts/week3-scratch-guard.py run --db-name astra_week3_pr12*`.

## Scope / unresolved

- Write scope respected: alembic/models/schemas/routers/services/tests/main/scripts/evidence only; no `src/**`, no git writes.
- `knowledge_point_links` untouched (matrix asserts its columns; service does not read/write it).
- Unresolved (deferred, explicit): subject/学科 consistency between `Note.subject` free text and canonical `Subject` is not enforced in this version.
- Unresolved (out of scope): `src/lib/api/notes.ts` client sync belongs to PR-12-impl-client / follow-up.
