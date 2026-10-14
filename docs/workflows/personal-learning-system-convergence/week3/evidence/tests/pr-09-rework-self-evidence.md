PR-09 Rework Self-Evidence (agent: PR-09-rework, role: implementer)
Date: 2026-09-24

## Regression comparison

Before: 59 failed, 555 passed, 10 skipped, 47 errors
After:  59 failed, 567 passed, 14 skipped, 51 errors

Delta:
  +12 passed  = 12 new pure tests in test_pr09_rework.py (PR9F-01..05, PR9U-01 pure)
  +4 skipped  = 4 new DB-backed tests in test_pr09_rework.py (need scratch PG via guard)
  +4 errors   = 4 new HTTP tests in test_pr09_verify_http.py (need scratch DB at alembic 031)
  0 change in failed = no regressions in pre-existing failures

## Per-item test coverage

PR9F-01 (next_due from source):
  test_map_next_review_date_to_utc_midnight  PASS (pure: date→UTC midnight)
  test_map_next_review_naive_datetime_assumes_utc  PASS
  test_map_next_review_aware_datetime_converts_to_utc  PASS
  Wk3ReworkDbTest::test_next_due_maps_from_source  SKIPPED (needs scratch PG)
    Assertion: review_items.next_due == source next_review (2026-12-15)

PR9F-02 (checks computed, not hardcoded):
  test_report_checks_use_instance_fields  PASS (pure: report uses instance fields)
  Wk3ReworkDbTest::test_checks_reflect_visibility_mismatch  SKIPPED (needs scratch PG)
    Assertion: compute_reconciliation_checks → False after breaking one visibility

PR9F-03 (dry-run planned values):
  test_dry_run_report_has_would_fields_and_zero_created  PASS
  test_real_run_report_created_fields_have_values  PASS
  Wk3ReworkDbTest::test_dry_run_reports_planned_values  SKIPPED (needs scratch PG)
    Assertion: would_create=1, created=0, would_create_v2=1, created_v2=0

PR9U-01 (source drift, W3-D10):
  test_report_rejected_count_includes_source_drift  PASS
  Wk3ReworkDbTest::test_source_drift_detected_and_target_not_overwritten  SKIPPED
    Assertion: rejected contains "source_drift", target title unchanged

PR9F-06 (MissingGreenlet fix):
  test_visibility_correct_version_toggles  (pre-existing, now targets admin_client fixture)
  test_put_mistake_success_200  NEW (HTTP: PUT → 200, version+1)
  test_delete_mistake_success_200  NEW (HTTP: DELETE → 200, status=archived)
  test_put_mistake_wrong_version_409  NEW (HTTP: wrong version → 409)
  test_delete_mistake_wrong_version_409  NEW (HTTP: wrong version → 409)

PR9F-04 (replay_noop on first dry-run):
  test_first_dry_run_replay_noop_is_true  PASS

PR9F-05 (retained_public_only → rejected):
  test_report_retained_public_only_maps_to_rejected_reason  PASS

PR9F-07 (test cleanup):
  Rewrote test_pr09_verify_http.py: unified admin_client fixture,
  removed global _logged_in state, _with_session fresh-engine pattern,
  fixed test_compat_read_search to use /api/admin/search.

## Targeted suite
115 passed, 5 skipped (test_pr09_rework + test_pr09_wk3_runner + test_pr09_migration
+ test_pr09_routes + test_week3_contracts)

## git status --short write-scope check
In scope (backend/app/services/**, backend/tests/**, week3/evidence/**):
  - backend/app/services/wk3_mistake_visibility_migration.py (untracked, modified)
  - backend/app/services/mistake_service.py (modified: +session.refresh after flush ×3)
  - backend/tests/test_pr09_rework.py (new)
  - backend/tests/test_pr09_verify_http.py (untracked, rewritten)
  - week3/evidence/tests/pr-09-rework-*.txt (new evidence)
Out of scope: no changes to src/** or backend/alembic/**
