PR-09 Rework-2 Self-Evidence (agent: PR-09-rework-2, role: implementer)
Date: 2026-09-25. Scope: R1-R4 only; R5 not done; R6/R7 untouched; R8 = migrations/README-stale.md.

## Fixes
- R1: `_reconcile_visibility(..., dry_run=False)` compares only in dry-run (no UPDATE), so a later
  create-path `session.commit()` cannot persist `mistakes.visibility`/`version`.
- R2: `_ensure_approval_actors(session, dry_run=False)` returns before INSERT/commit in dry-run.
- R3: `Wk3MigrationReport._count_match()` uses `would_create+would_reconcile` when `dry_run`.
- R4: dry-run reconcile increments only `would_reconcile`; `visibility_reconciled` stays 0.

## Evidence
- Targeted `test_pr09_rework.py`+`test_pr09_verify_http.py`: 46 passed (pr-09-rework-2-targeted-tests.txt).
- New tests: `test_dry_run_mixed_scenario_is_zero_persistence` (R1/R3/R4),
  `test_dry_run_does_not_persist_approval_actors` (R2), `test_dry_run_count_match_uses_would_fields` (R3).
- Full suite baseline (fresh astra_week3_pr09_rw2 @031): 2 failed, 680 passed, 9 skipped.
- Full suite after: 2 failed, 683 passed, 9 skipped (+3 new passed, failures unchanged)
  (pr-09-rework-2-regression-full.txt). Same 2 pre-existing failures.
- Write scope: only the 2 code files + week3/evidence new files (pr-09-rework-2-git-status.txt).

## Unresolved (not R1-R4)
- Pre-existing session-state quirk: a dry-run leaves `SET SESSION AUTHORIZATION legacy_note_adapter_runner`
  pending, so the new tests explicitly RESET+commit before counting. No data effect.
- Pre-existing full-suite failures: `test_lsr03_guarded_runner.py::test_asyncpg...` (env),
  `test_pr09_verify_http.py::test_public_empty_envelope_explicit` (cross-file DB ordering).

## Self-evaluation: ACCEPT
