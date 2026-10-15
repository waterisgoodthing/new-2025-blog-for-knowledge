# PR-09 DB/Migration/Ledger Independent Verification Findings

- agent_id: PR-09-db-verify-db
- role: verifier (database / migration / ledger only)
- date: 2026-09-24
- scope: migration 031 matrix + `wk3-mistake-visibility-v1` ledger runner evidence
- product code: unmodified (findings only)

## Summary

**PARTIAL** — A matrix fully PASS. B matrix PASS except **B5 `next_due` mapping FAIL** (W3-D08 violation). One MEDIUM report-integrity defect. B6 left unresolved (design not pinned).

---

## Findings

### F-1 HIGH — `next_due` is not mapped from source `next_review` (W3-D08)

- **Where**: `backend/app/services/wk3_mistake_visibility_migration.py:300`
  ```python
  has_next_review = next_review_raw is not None
  mapped_next_review_at = _now_utc()   # always run-time; source value discarded
  ```
- **Contract**: W3-D08 / pr-09.md 约束 7 — "`next_review` 存在时映射为 `next_due`（保留用户既定到期日）".
- **Evidence**: `sql/pr-09-db-recon-b5-next-due-vs-source.txt`
  - `pr09-published_visible` source `next_review=2026-12-15` → `review_items.next_review_at=2026-09-24 08:11:36` (`next_due_matches_source=f`)
  - `pr09-unpublished_visible` source `next_review=2027-01-20` → `next_review_at=2026-09-24 08:11:36` (`next_due_matches_source=f`)
- **Report lie**: `review_items.next_due_from_source=2` counts presence of source `next_review`, not the mapped value. Value written is always `_now_utc()`.
- **Impact**: user-set due dates are lost; all migrated ReviewItems become immediately due.

### F-2 MEDIUM — reconciliation `checks` are hardcoded `True`

- **Where**: `backend/app/services/wk3_mistake_visibility_migration.py` `Wk3MigrationReport.to_json_dict()`
  ```python
  "provenance_match": True,
  "visibility_matrix_match": True,
  "public_field_allowlist_match": True,
  ```
- Only `count_match` and `replay_noop` are computed. W3F-08 implies these are real gates.
- **Note**: verifier independently checked provenance + W3-D06 matrix on this fixture set and they **do** pass; the defect is that the report cannot fail them.

### F-3 MEDIUM — dry-run report under-counts `review_items` (not a faithful plan)

- `migrate(dry_run=True)` returns immediately after `create_legacy_note_migration_pending`, before target creation.
- Result: dry-run report `targets.created=5` but `review_items.created_v2=0`, `next_due_from_source=0` (`migrations/pr-09-db-ledger-b1-dry-run-report.json`).
- Dry-run **zero-persistence itself PASS** (post-run: ledger=0, pending=0, mistakes=0).

### F-4 LOW — dry-run first pass reports `replay_noop=false`

- Any `targets_created>0` flips `replay_noop` to `false`, including a first planning pass that is not a replay.
- Semantics of `checks.replay_noop` on `dry_run=true` are misleading.

### F-5 LOW (informational) — published×visible mapping failures become `retained_public_only`, counted as `skipped`

- A published×visible note with `SUBJECT_UNMAPPED` is transitioned to `retained_public_only` (adapter `should_retain_public_only`) and reported as `skipped_already_migrated`, not `rejected`.
- Matches adapter design; consumers of `targets.rejected` will not see these.

---

## Unresolved

### U-1 — source change conflict after migration (B6)

- **Observed**: after migration, mutating source note `title` + `revision` then re-running → `created=0 reconciled=0 skipped=5 rejected=0 replay_noop=true`. Silent no-op. No `SOURCE_DRIFT`, no ledger `source_hash` re-check on the terminal-state reconcile path.
- **Related**: `status`/`hidden` **are** re-read live (visibility would reconcile if those change); title/revision drift is ignored.
- **Why unresolved**: W3-D06~D08 do not pin post-migration source-drift behavior on the reconcile path. Per instructions, product not modified.
- **Evidence**: `migrations/pr-09-db-ledger-b6-*.log`, `migrations/pr-09-db-ledger-b6-run-report.json`

---

## Scope notes

- Session-auth leak (`SET SESSION AUTHORIZATION` + `commit` + `RESET` + `rollback`) hypothesized from code shape was **NOT reproduced** on current code: mixed-failure run rejected 1 note (`633818c7…`, 2nd in `ORDER BY id`) and the 5 later notes still processed as `skipped` (`migrations/pr-09-db-ledger-b7-reject-path.log`). Prior self-evidence `pr-09-wk3-run-report.json` showed `permission denied for table notes` after the first rejection; not reproduced now. Not filed as a finding.
- Direct `INSERT` into `legacy_note_migrations` is correctly blocked by `guard_legacy_note_migration()` (`LEGACY_MIGRATION_DIRECT_LEDGER_MUTATION_REJECTED`). B3 v1-* rows were therefore created via adapter `migrate(mapping_version='v1-manual-026')` then target visibility forced to `'private'` to simulate migration-026 output.
- No product code, `src/**`, `scripts/**`, or git state modified. All SQL via `scripts/week3-scratch-guard.py` against `astra_week3_pr09_db1`–`db5` on local PostgreSQL 16.14 (port 5432).
