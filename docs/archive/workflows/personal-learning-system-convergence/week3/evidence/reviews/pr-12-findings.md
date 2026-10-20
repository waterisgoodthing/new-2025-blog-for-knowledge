# PR-12 findings — independent verification (PR-12-verify)

Date: 2026-09-25 · agent_id: PR-12-verify · profile: senior-qa-sdet · role: verifier
Scratch DB: `astra_week3_pr12_verify` (fresh, via `scripts/week3-scratch-guard.py`).
Conclusion: **no product defects at BLOCKER/HIGH/MEDIUM**. Items below are process / informational.

| id | severity | area | finding | evidence |
| --- | --- | --- | --- | --- |
| PR12V-01 | LOW (process) | evidence layout | PR-12 client evidence was written to the repo-root `week3/evidence/tests/pr-12-client-*.txt`, but the canonical Week 3 evidence index used by PR-09/PR-10 (and referenced by `pr-12.md` write_scope) is `docs/workflows/personal-learning-system-convergence/week3/evidence/`. Root `week3/evidence/` currently contains only those two client files. This verification wrote to the canonical docs path. Fragmented evidence can be missed by the gate/reviewer index. | `ls week3/evidence/tests`, `ls docs/.../week3/evidence` |
| PR12V-02 | LOW | client DTO narrowing | Client `KnowledgePointNoteItem.type` / `.status` are narrowed unions (`"note"\|"blog"\|"mistake"`, `"draft"\|"published"`) while the backend schema types both as plain `str`. Response shape is field-identical and compatible for current `Note` values, but the client over-trusts the domain. | `src/lib/api/notes.ts:63-70` vs `backend/app/schemas/note_knowledge_point.py:17-22` |
| PR12V-03 | INFO | API semantics | `POST .../link` returns `linked: true` even when the relation already existed: the service returns `False` for a duplicate but `admin_notes.link_note_knowledge_point` discards it and always builds `linked=True` (`backend/app/routers/admin_notes.py:70-77`). This is the documented idempotent contract, but callers must not read `linked=true` as "newly created". | `pr-12-verify-api.txt` (duplicate POST → 200 `linked:true`) |
| PR12V-04 | INFO | verifier process | First migration-matrix run reported a false FAIL for "knowledge_point_id INTEGER" caused by the verifier script checking `udt_name` instead of `data_type`; corrected, rerun ALL_PASS. Not a product issue. | `pr-12-verify-migration-matrix.txt` (ALL_PASS after fix) |

## Explicit non-findings (verified clean)

- Migration 032 does not alter the legacy polymorphic `knowledge_point_links` table; its full structure snapshot is byte-identical at 031 and 032.
- No `subject`/学科 consistency logic anywhere in the PR-12 service, router, model or schema (only a docstring recording the deferral).
- No 500 under a real parallel admin double-POST racing the composite PK, nor under a deterministic direct `IntegrityError` path.
- `npx tsc --noEmit` exits 0 (no new type errors); targeted client vitest 6/6.

## Residual / unverified (not defects)

- Concurrent `unlink` of the same row was not raced in this pass; `unlink` intentionally has no savepoint (unlike `link`). Expected benign (DELETE of an already-deleted row), but not directly evidenced here.
- Subject/学科 normalisation remains deferred by design (PR-12 excluded scope).
