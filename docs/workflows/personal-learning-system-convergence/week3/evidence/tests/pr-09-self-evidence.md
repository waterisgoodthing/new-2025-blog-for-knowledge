# PR-09 Evidence — canonical public mistakes (backend slice)

agent: PR-09-impl-backend · date: 2026-09-23
scratch DB: `astra_week3_pr09_main` @ `127.0.0.1:49621` via `scripts/week3-scratch-guard.py`

---

## 1. Contract tests (test_week3_contracts.py)

```
$ cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_week3_contracts.py -q
53 passed in 0.17s
```

## 2. New tests + regressions (via guard)

```
$ python3 scripts/week3-scratch-guard.py run --db-name astra_week3_pr09_main --url "postgresql+asyncpg://postgres@127.0.0.1:49621/astra_week3_pr09_main" -- env DATABASE_URL=... .venv/bin/python -m pytest tests/test_week3_contracts.py tests/test_pr09_migration.py tests/test_pr09_legacy_mistake_freeze.py tests/test_pr09_wk3_runner.py tests/test_pr09_routes.py -q
125 passed in 0.43s

$ ... pytest tests/test_pr09_permissions.py -q
7 passed in 0.41s

$ ... pytest tests/test_mistake_review_service.py tests/test_legacy_note_migration_contract.py tests/test_security_settings_guards.py -q
25 passed, 4 skipped in 0.54s
  (4 skipped = pre-existing DB-setup-dependent tests; no new failures)

$ ... pytest tests/test_batch7_compatibility.py tests/test_manage_write_permissions.py -q
10 passed in 0.36s
```

## 3. Migration 031 matrix (via guard + psql)

### 3.1 fresh → 031
```
$ ... alembic upgrade head
INFO  Running upgrade 030 -> 031, Widen ck_mistakes_visibility to allow 'public'
PASS
```

### 3.2 Single head = 031
```
$ ... alembic heads
031 (head)
```

### 3.3 Constraint shapes (psql)
```
ck_mistakes_visibility    | CHECK (((visibility)::text = ANY ((ARRAY['private','public'])::text[])))
ck_questions_visibility   | CHECK (((visibility)::text = 'private'::text))
ck_attachments_visibility | CHECK (((visibility)::text = 'private'::text))
version_num = 031
```

### 3.4 Constraint rejection: visibility='x'
```
PASS: visibility=x rejected (IntegrityError)
CURRENT_VISIBILITY=public   (a valid 'public' row was accepted)
```

### 3.5 Downgrade fail-closed (public row present)
```
$ ... alembic downgrade 030
RuntimeError: downgrade fail-closed: 1 mistake row(s) have visibility='public';
  re-narrowing ck_mistakes_visibility to private-only would violate data.
```
→ version stays at 031, constraint remains `IN ('private','public')`.

### 3.6 Downgrade succeed (after clearing public rows)
```
$ UPDATE mistakes SET visibility='private' WHERE visibility='public';
$ ... alembic downgrade 030
INFO  Running downgrade 031 -> 030
PASS
$ ... alembic upgrade head
INFO  Running upgrade 030 -> 031
PASS
```

## 4. Ledger runner (wk3-mistake-visibility-v1)

### 4.1 Dry-run zero persistence
```
$ ... wk3_mistake_visibility_runner.py --report-out dry-run-report.json --dry-run
wk3-mistake-visibility-v1 dry_run=True created=4 reconciled=0 skipped=0 rejected=0 replay_noop=False

$ psql: SELECT count(*) FROM legacy_note_migrations  →  0
$ psql: SELECT count(*) FROM mistakes               →  0
```
→ **Zero persistence confirmed** (no ledger rows, no mistake rows after dry-run).

### 4.2 Reconciliation report JSON
Full JSON at `pr-09-wk3-dry-run-report.json` and `pr-09-wk3-run-report.json`.
Schema keys verified by `test_pr09_wk3_runner.py::test_report_json_schema_keys`.

### 4.3 Source matrix
```json
"source": {"total_legacy_mistakes": 4,
  "by_mapping": {"published_visible": 1, "published_hidden": 1,
                 "unpublished_visible": 1, "unpublished_hidden": 1}}
```
→ 4 fixture notes across all four W3-D06 matrix cells.

### 4.4 Unmapped fields
```json
"unmapped_source_fields": ["ef", "interval", "repetitions", "last_reviewed"]
```

### 4.5 Real run (fixture notes lack canonicalize structure)
```
wk3-mistake-visibility-v1 dry_run=False created=0 reconciled=0 skipped=0 rejected=4
```
→ Rejected with `SUBJECT_UNMAPPED` (expected: minimal seed notes don't satisfy
  `validate_legacy_mapping_payload`). Full end-to-end creation with realistic
  canonical-izable fixtures deferred to PR-09-verify (needs richer seed data
  matching `canonicalize_legacy_note` expectations).

## 5. git status --short (PR-09 files only)

```
M  backend/app/models/mistake.py
M  backend/app/routers/admin_mistakes.py
M  backend/app/routers/notes.py
M  backend/app/routers/review.py
M  backend/app/schemas/mistake.py
M  backend/app/services/legacy_note_migration_adapter.py
M  backend/app/services/mistake_service.py
M  backend/main.py
M  backend/tests/lsr03_final_verifier_harness.py
M  backend/tests/test_security_settings_guards.py
M  backend/tests/test_week3_contracts.py
?? backend/alembic/versions/031_mistake_visibility_public.py
?? backend/app/routers/public_mistakes.py
?? backend/app/services/legacy_mistake_freeze.py
?? backend/app/services/wk3_mistake_visibility_migration.py
?? backend/tests/test_pr09_migration.py
?? backend/tests/test_pr09_legacy_mistake_freeze.py
?? backend/tests/test_pr09_permissions.py
?? backend/tests/test_pr09_routes.py
?? backend/tests/test_pr09_wk3_runner.py
?? backend/tests/_pr09_evidence_constraint.py
?? backend/tests/_pr09_evidence_seed.py
?? scripts/wk3_mistake_visibility_runner.py
```
