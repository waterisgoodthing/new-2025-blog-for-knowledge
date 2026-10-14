# Independent Review — Week 4 Rework (F05 draft path, CI deselect debt removal, pr09 idempotency)

- Reviewer role: independent reviewer (no implementation ownership; did NOT implement these changes)
- Mode: READ-ONLY source inspection + scratch-DB reproduction; no source modified; no git write; only this evidence file created
- Date: 2026-09-27
- Scratch DB: `astra_week4_fix2` (dropped/recreated fresh, migrated via `scripts/week4-scratch-guard.py`); `blog_db` / `blog_v2` untouched
- Guard: `python3 scripts/week4-scratch-guard.py check --db-name astra_week4_fix2` → `PASS`
- Changed set verified present:
  - `backend/app/services/capture_ai_draft.py` (tracked; `git diff HEAD` shows F05 wiring)
  - `backend/tests/test_ai_error_chain.py` (untracked/new; `DraftCrossLayerClassificationTest`)
  - `backend/tests/test_pr09_verify_http.py` (untracked; transaction-scoped `get_db` empty view)
  - `backend/tests/test_pr11_dashboard_service.py` (untracked; per-test `_CANONICAL_ISOLATION`)
  - `backend/tests/test_pr09_verify_api_contract.py` (untracked; `_isolated_public_view` idempotency)
  - `.github/workflows/ci.yml` (tracked; backend job has no `--deselect`)
  - `docs/ci-local-reproduction.md` (untracked; "Deselected backend debt (R03) — RESOLVED")

## VERDICT: PASS_WITH_NOTES

All three rework goals hold on reproduction. The F05 draft path now prefers the structured
`GatewayCallResult.failure_category` (recognition-identical mapping) with a string-sniff fallback, so
`httpx.ReadTimeout → provider_timeout → error_code="timeout"` and a non-JSON body →
`invalid_response → error_code="parse_error"` through `draft_mistake`. The four modified tests still
assert their invariants with no skip/xfail/deselect added, and the isolation techniques scope rows
inside rolled-back transactions rather than disabling any check. CI Job 2 contains no `--deselect`.
On reused scratch DB `astra_week4_fix2` the full suite is green twice in a row
(`922 passed, 9 skipped, 0 failed`, first fresh and then reused). Notes below are LOW/INFO only; no
BLOCKER/HIGH/MEDIUM. **No isolation change weakened a test.**

## Findings

| id | severity | problem | evidence (file:line) | required action |
|----|----------|---------|----------------------|-----------------|
| R1 | LOW (process/traceability) | The "3 `--deselect` removed" delta cannot be shown as a git diff: the committed baseline `HEAD:.github/workflows/ci.yml` already had a plain `pytest tests/ -v --tb=short` with no deselect, because the deselect policy lived only in the uncommitted pre-rework working tree. Removal is confirmed by comparing the pre-rework recorded evidence to the current file, not by `git diff HEAD`. | pre-rework: `docs/.../week4/evidence/gate/ci/job2-backend.txt:108-109` (three `--deselect`); `docs/.../week4/evidence/pr-17-ci-run-local.txt:41-47`; current: `.github/workflows/ci.yml:107-110` (no deselect) | No code action. Record in TRACKING that the deselect debt was worktree-only (never committed); keep the current no-deselect file as the baseline. |
| R2 | LOW (test fragility) | In `test_partial_service_failure_degrades_without_raising`, the service's internal `await session.rollback()` fires before the summary finishes, discarding the per-test `_CANONICAL_ISOLATION` and the test's own inserts mid-test. All asserted fields (`review_today_count`, `practice_today_count`, `section_actions`, `weak_top3`, `today_first_action`) are computed before or by the injected failure, so the assertions stay genuine; the only post-rollback field (`recently_mastered_4`) is computed unisolated but is not asserted. | `backend/tests/test_pr11_dashboard_service.py:289-312`; `backend/app/services/dashboard_service.py:227,238,249,265,272` (rollbacks), `:276` (`recently_mastered`) | Optional: move `recently_mastered` before the failing calls or re-apply isolation after a service rollback if that field is ever asserted here. Not required for current assertions. |
| R3 | INFO | `DraftResult` still has no `failure_category` field, so the adapter-level category is only recoverable through `error_code`. The end-to-end DTO category is nonetheless correct because `CaptureOut.failure_category` is a computed field derived from `error_code`. | `backend/app/services/capture_ai_draft.py:40-47` (DraftResult), `:206-223` (error_code mapping); `backend/app/schemas/capture.py:162-168` (computed `failure_category`); `backend/app/services/capture_service.py:297` | No action. The task acceptance was the `error_code` mapping; verified correct end-to-end. |
| R4 | INFO | The draft path can now emit `provider_auth` / `invalid_model` error codes it previously never produced (it collapsed them to `provider_error`). These match the recognition vocabulary and `_ERROR_CODE_CATEGORY`; no existing test or caller asserted the old value for those classes. | `backend/app/services/capture_ai_draft.py:217-223`; `backend/app/services/capture_failure_taxonomy.py:26-36`; recognition parity `backend/app/services/capture_recognition.py:204-212` | No action. Intentional parity with recognition; full suite green. |

Severity counts: BLOCKER 0, HIGH 0, MEDIUM 0, LOW 2, INFO 2.

## Verification detail

### 1. F05 draft-path category wiring — PASS
- `capture_ai_draft` now calls `_resolve_provider_category(gw.failure_category, err)` on the
  `not gw.success` branch and `_resolve_provider_category(getattr(e, "category", None), str(e))` on
  the `RuntimeError` branch; `_resolve_provider_category` tries `categorize_provider_category`
  first and only then `categorize_provider_error` (string sniff) — identical ordering to
  `capture_recognition._resolve_provider_category`
  (`backend/app/services/capture_ai_draft.py:108,158,177-184`;
  `backend/app/services/capture_recognition.py:101,147,166-173`).
- Mapping is recognition-identical: `PROVIDER_TIMEOUT→"timeout"`, `PROVIDER_AUTH→"provider_auth"`,
  `INVALID_MODEL→"invalid_model"`, `INVALID_RESPONSE→"parse_error"`, else `"provider_error"`
  (`capture_ai_draft.py:206-223` vs `capture_recognition.py:196-212`).
- Chain confirmed: `ai_service.AIProviderError(RuntimeError)` carries `.category`
  (`ai_service.py:27`, `ALLOWED_ERROR_CATEGORIES` `:15`) → `_build_failure_result` sets
  `failure_category=getattr(exc,"category",None)` (`ai_gateway.py:204-220`) → draft consumes it →
  `CaptureOut.failure_category` recomputes from `error_code` (`schemas/capture.py:162-168`).
- New cross-layer test proves it with the real gateway (only transport mocked), not a mocked
  gateway: `DraftCrossLayerClassificationTest::test_native_read_timeout_surfaces_provider_timeout`
  asserts `error_code=="timeout"`, `error_message_safe=="AI draft timed out"`, and
  `category=provider_timeout code=timeout` in the WARNING log;
  `test_non_json_body_surfaces_invalid_response` asserts `parse_error` /
  `category=invalid_response` and that the synthetic secret never appears
  (`backend/tests/test_ai_error_chain.py:260-315`). Both PASS.
- Genuine regression coverage (not vacuous): on the pre-rework logic, `gw.error` is always the
  constant `"All AI providers failed"` (`_call_with_fallback` exhaustion,
  `ai_service.py:260-267`), so the old `is_timeout` sniff yielded `provider_error`; the new test
  asserts `timeout`/`parse_error`, which the old code could not satisfy.
- Existing contracts preserved: generic provider failure with no structured category still falls
  back to `provider_error` (`test_i6_capture_failure_matrix.py:102-123`), `no_provider`
  (`:76-86`), and `schema_error` (`:125-146`) still PASS. The recognition path is untouched by the
  draft change.

### 2. Isolation correctness without weakening — PASS
- No `skip` / `xfail` / `pytest.mark` / `unittest.skip` / `--deselect` in any of the four modified
  test files (grep over `test_ai_error_chain.py`, `test_pr09_verify_http.py`,
  `test_pr11_dashboard_service.py`, `test_pr09_verify_api_contract.py` → no matches). Test counts
  remain: `test_ai_error_chain` 18, `test_pr09_verify_http` 27,
  `test_pr09_verify_api_contract` 24, `test_pr11_dashboard_service` 9.
- Empty-envelope honesty (`test_pr09_verify_http.py:164-206`): the override
  `_isolated_empty_db` runs an `UPDATE public.mistakes SET visibility='private' WHERE
  status='active' AND visibility='public'` on a transaction-scoped session and rolls back in
  `finally`; the endpoint genuinely computes `empty=True` for a zero-row view. The assertion set is
  unchanged (`empty`, `message`, `items==[]`, exact envelope keys).
- Partial-service-failure honesty (`test_pr11_dashboard_service.py:289-312`): asserts
  `review_today_count==1` (computed before the injected failures), `practice_today_count==0`,
  `section_actions.practice.available is False`,
  `reason==PRACTICE_REASON_UNAVAILABLE`, `weak_top3==[]`, and `today_first_action.kind=="review"`.
  The injected `SQLAlchemyError` still reaches the real service degradation path — the check is not
  bypassed.
- Public-read allowlist / leakage (`test_pr09_verify_http.py:209-233`): seeds public + private +
  archived rows, keeps only the public row visible, asserts the exact key allowlist and that
  `LEAK_MARKER` / `PRIVATE_ROW_MUST_HIDE` / `ARCHIVED_MUST_HIDE` / `"my_answer"` never appear while
  `CA-VALUE` does. Unchanged and exact.
- pr09 contract shapes (`test_pr09_verify_api_contract.py:271-298`): `_isolated_public_view(keep_id=pub_id)`
  hides every other active public row inside a rolled-back transaction, then asserts
  `total==1`, `len(items)==1`, exact `PUBLIC_ALLOWLIST`, forbidden fields absent, and no forbidden
  JSON key names. Assertions remain exact, not weakened.
- **Non-vacuousness proof (reused DB):** after two full suite runs the scratch DB holds
  `active_public_mistakes=8`, `active_questions=56`, `active_review_items=52`,
  `private_or_archived_mistakes=48` committed rows — yet the empty-envelope and empty-dashboard
  tests still passed on run 2. That is only possible if the isolation genuinely scopes those rows
  away; if it had disabled the filters, the endpoints would have returned the committed rows and
  the exact assertions (`empty=True`, `total==1`, `count==0`) would have failed. Even on a fresh CI
  DB the empty-envelope test is non-vacuous because the alphabetically-earlier sibling module
  `test_pr09_verify_api_contract.py` commits active public rows (via `_seed_mistake`).

### 3. CI — PASS
- The backend job runs the full suite with no deselect/ignore/`-k`:
  `.github/workflows/ci.yml:107-110` → `pytest tests/ -v --tb=short`.
- Repo-wide grep for `deselect` finds it only in explanatory comments
  (`ci.yml:101,104`) — not in any command. No `collect_ignore`, `pytest_ignore_collect`, or
  `addopts` exists in `backend/tests/conftest.py` (which only installs the connection guard) and
  there is no `pytest.ini` / `pyproject.toml` / `setup.cfg` / `tox.ini`.
- The 9 skips observed locally are pre-existing environment gates, not new blanket skips:
  6× `LSR03_DATABASE_URL is required for isolated database/fixture tests`
  (`test_legacy_note_migration_contract.py:35,105,165,186`;
  `test_lsr03_fixture_rehearsal.py:76,87`) and 3× `scratch DB only` from a pre-existing
  `skipUnless` that only accepts `astra_week2_*`/`opencode_week2_*`
  (`test_review_schema_v2.py:42-44,290`). None of those files are in the rework's changed set, and
  the reassessment already recorded the same 9 skips.

### 4. Full suite twice on scratch `astra_week4_fix2`, no deselect — PASS
Both runs executed the exact CI backend command shape via the guard, no `--deselect`:

```
python3 scripts/week4-scratch-guard.py run --db-name astra_week4_fix2 -- \
  bash -c 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/ -q -p no:cacheprovider'
```

- Run 1 (fresh DB: dropped, recreated, `alembic upgrade head`): exit 0 —
  `922 passed, 9 skipped, 2 warnings, 47 subtests passed in 31.14s`
- Run 2 (same/reused DB, no reseed/reset): exit 0 —
  `922 passed, 9 skipped, 2 warnings, 47 subtests passed in 31.94s`

This matches `docs/ci-local-reproduction.md:97-98` (`922 passed, 9 skipped, 0 deselected`). Note the
prior gate summary warned the suite was non-hermetic on a reused DB
(`evidence/gate/week4-gate-summary.md:54`); the rework's isolation removes that dependency, and the
identical reused-run result is the idempotency proof for the `test_pr09_verify_api_contract.py` fix.

### 5. Side effects / dependency of the `get_db` override — PASS (with note)
- `public_mistakes` imports the same object the test overrides:
  `from app.database import get_db` and `db: AsyncSession = Depends(get_db)`
  (`backend/app/routers/public_mistakes.py:8,19`); the tests override
  `main.app.dependency_overrides[get_db]` with that same `app.database.get_db` function
  (`test_pr09_verify_api_contract.py:219-257`; `test_pr09_verify_http.py:175-199`). The key matches,
  so the override applies.
- The override does not disable the route filter: it flips competing rows to `private` (or absent)
  inside its own transaction and rolls back. If the visibility/status filter were removed, the
  hidden rows would be returned and the exact assertions would fail (see §2 non-vacuousness).
- Residual risk: as noted in R2, the pr11 suite relies on the transaction surviving the service
  call; `get_dashboard_summary` rolls back on caught `SQLAlchemyError`, which ends the per-test
  isolation. This does not hide a bug in any asserted invariant today, but it is fragile if new
  assertions are added after a failure branch. No production behavior is affected (test-only).

## Raw results

### Full suite — run 1 (fresh), tail
```
922 passed, 9 skipped, 2 warnings, 47 subtests passed in 31.14s
PASS: db_name='astra_week4_fix2' source=explicit:--db-name; executing ['bash', '-c', 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/ -q -p no:cacheprovider']
```

### Full suite — run 2 (reused), tail
```
922 passed, 9 skipped, 2 warnings, 47 subtests passed in 31.94s
PASS: db_name='astra_week4_fix2' source=explicit:--db-name; executing ['bash', '-c', 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/ -q -p no:cacheprovider']
```

### 9 skips enumerated (`-rs`)
```
SKIPPED [1] tests/test_legacy_note_migration_contract.py:164: LSR03_DATABASE_URL is required for isolated database tests
SKIPPED [1] tests/test_legacy_note_migration_contract.py:103: LSR03_DATABASE_URL is required for isolated database tests
SKIPPED [1] tests/test_legacy_note_migration_contract.py:33: LSR03_DATABASE_URL is required for isolated database tests
SKIPPED [1] tests/test_legacy_note_migration_contract.py:185: LSR03_DATABASE_URL is required for isolated database tests
SKIPPED [1] tests/test_lsr03_fixture_rehearsal.py:76: LSR03_DATABASE_URL is required for isolated fixture tests
SKIPPED [1] tests/test_lsr03_fixture_rehearsal.py:87: LSR03_DATABASE_URL is required for isolated archive tests
SKIPPED [1] tests/test_review_schema_v2.py:504: scratch DB only
SKIPPED [1] tests/test_review_schema_v2.py:393: scratch DB only
SKIPPED [1] tests/test_review_schema_v2.py:471: scratch DB only
```

### Targeted rework modules (4 files) — PASS
```
python3 scripts/week4-scratch-guard.py run --db-name astra_week4_fix2 -- \
  bash -c 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest \
    tests/test_ai_error_chain.py tests/test_pr09_verify_http.py \
    tests/test_pr11_dashboard_service.py tests/test_pr09_verify_api_contract.py -q -p no:cacheprovider'
```
```
78 passed in 2.41s
EXIT=0
```

### F05 cross-layer test file (18 tests) — PASS
```
tests/.../DraftCrossLayerClassificationTest::test_native_read_timeout_surfaces_provider_timeout PASSED
tests/.../DraftCrossLayerClassificationTest::test_non_json_body_surfaces_invalid_response PASSED
...
18 passed in 0.21s
EXIT=0
```

### Reused-DB committed-row probe (non-vacuousness)
```
active_public_mistakes=8
active_questions=56
active_review_items=52
private_or_archived_mistakes=48
```
(passed `test_public_empty_envelope_explicit` and `test_all_empty_answers_are_honest` on run 2
despite these committed rows — the isolation, not a disabled check, produced the zero/empty views.)

## Unresolved questions / remaining

1. R1 is a traceability nuance only: because the deselect debt was never committed, a future
   reader comparing `git diff HEAD` cannot see the removal. Recommend recording it in
   `week4/TRACKING.md` (W4-E11) as "worktree-only deselect policy removed in rework".
2. R2/R3/R4 are non-blocking; no approval or follow-up is required to accept this rework.
3. Remote GitHub Actions remains NOT_VERIFIED (push not authorized); the CI claim was verified by
   source inspection of `.github/workflows/ci.yml` plus local reproduction of the identical pytest
   command, not by a live Actions run.

Status: F05 draft wiring PASS (reproduced); isolation-without-weakening PASS (no skip/deletion, no
vacuous assertion change); CI deselect removal PASS; full-suite-twice idempotency PASS (0 failures
both runs); `get_db` override dependency PASS. No source modified; this evidence file only.
