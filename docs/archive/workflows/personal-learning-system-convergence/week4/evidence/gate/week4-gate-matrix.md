# Week 4 Gate Matrix — RELEASE GATE (M4)

Date: 2026-09-26
Scope: local + isolated scratch DB only. Production/remote/commit/push are out of the authorized scope.

Legend: `PASS` | `PARTIAL` | `NOT_VERIFIED` | `NOT_AUTHORIZED` | `FAIL`

| Criterion | Target | Status | Evidence |
|---|---|---|---|
| **PR-14 OCR** | | | |
| Failure taxonomy | 8 categories, exhaustive mapping | PASS | `capture_failure_taxonomy.py`; `test_capture_taxonomy.py` |
| 10-sample baseline | ≥8/10 OR entry marked/disabled | PARTIAL | local deterministic harness only; real-provider rate **NOT_VERIFIED**; entry not disabled (W4-E02) |
| UI states | loading/success/error(+category)/empty + retry | PASS | `capture-workspace.tsx`; vitest; `pr-14-review.md` |
| **PR-15 WebAuthn** | | | |
| Migration 033 | fresh + incremental replay PASS | PASS | `gate/migrations/gate-migration-replay-v2.log` |
| Challenge lifecycle | generate/store/verify/consume correct | PASS | `pr-15-unit-tests.txt` (10 passed) |
| Three ceremonies | registration/auth/operator preserved | PASS | `pr-15-integration-tests.txt` (4 passed) |
| Security cases | concurrent/expired/consumed/cross-purpose rejected | PASS | `pr-15-unit-tests.txt` |
| **PR-19 AI governance** | | | |
| Polish classification | decision documented | PASS | `docs/architecture/ai-governance.md` |
| Target linkage | persisted calls write target_id | PASS | gateway + capture threading; `test_ai_governance.py` |
| Creation backfill | confirmation→target_id, abandon→NULL | PARTIAL | `backfill_ai_run_target` exists + tested; **no production confirmation endpoint calls it** (F08, documented NOT_YET_WIRED) — not scored PASS |
| **PR-16 Login throttling** | | | |
| Delay schedule | 0/0/0/2s/5s/15s (capped) | PASS | `pr-16-unit-tests.txt` |
| Account reset | success clears counter | PASS | `pr-16-unit-tests.txt` |
| Real timing | 4th attempt ≈2s (±0.5s) | PASS | `pr-16-integration-timing.txt` (2.005s) |
| Dual dimension | account + IP enforced; IP TTL decay | PASS | `pr-16-review.md` recheck; `pr-16-unit-tests.txt` |
| **PR-17 CI** | | | |
| Four jobs defined | frontend/backend/smoke/e2e | PASS | `.github/workflows/ci.yml` (all DB jobs use `astra_week4_ci`) |
| Job 1 frontend local | tsc + test:typecheck + vitest + build | PASS | `gate/tests/gate-frontend-v2.txt` (522 passed) |
| Job 2 backend local | alembic + pytest (fresh, no deselect) | PASS | `gate/tests/gate-backend-v2.txt` (922 passed, 0 failed, 9 skipped) |
| Job 3 runtime smoke local | build:cf + full stack + smoke | PASS | `gate/ci/gate-buildcf-v2.txt`, `gate/browser/gate-runtime-smoke-v2.txt` (ok=20 failed=0) |
| Job 4 E2E local | 5 tests workers=1 (incl. R22b business) | PASS | `gate/ci/gate-e2e-v2.txt` (5/5); `pr-17-e2e-business.md` |
| CI green on push / intentional break | all jobs pass remotely | NOT_AUTHORIZED / NOT_VERIFIED | push not authorized |
| **PR-18 Cleanup** | | | |
| Three-part evidence per item | grep + test + no-surface | PASS | `pr-18-cleanup-components.md` |
| Deletion safety | no new test failures | PASS | `pr-18-review.md`; 522 passed after |
| Net reduction | ≥500 lines (secondary) | PARTIAL (NOT MET) | 124 lines removed (5 dead items only) |
| **Baseline health** | | | |
| Frontend tests | 69 files / 516+ PASS | PASS | 70 files / 522 passed |
| Backend tests | 821+ passed / ≤4 failed / ≤9 skipped | PASS | 922 passed / 0 failed / 9 skipped (no deselect) |
| Type checks | `tsc --noEmit` exit 0; `test:typecheck` exit 0 | PASS | `gate/tests/gate-frontend-v2.txt` |
| Migration head | single head 033 | PASS | `gate/migrations/gate-migration-replay-v2.log` |
| Runtime smoke | 0 failures, health 200 | PASS | `gate/browser/gate-runtime-smoke-v2.txt` |
| Build | `build:cf` exit 0 | PASS | `gate/ci/gate-buildcf-v2.txt` |
| `git diff --check` | clean | PASS | review evidence |

## Overall

**PARTIAL (fix round 2026-09-26)** — the reassessment's F01–F08 defects have been fixed and
independently reviewed; all locally-verifiable criteria now PASS. The status is PARTIAL **only**
because two acceptance items remain `NOT_VERIFIED` under the granted local-only authorization
(no push, no provider credentials): remote GitHub Actions (all four jobs) and a real-provider OCR
baseline. This is no longer due to any known defect.

### Fix round — reassessment F01–F08 resolution

| ID | Was | Fix | Review |
|---|---|---|---|
| F01 CI blocker | HIGH | 3 DB jobs → `astra_week4_ci` (guard-compatible); no `blog_db` target | `fix-F06-F01-review.md` PASS |
| F02 CLI cross-loop | HIGH | `cli.py` single `_ServerEventLoop`; two options requests 200/200 | `fix-F02-F03-review.md` PASS |
| F03 ceremony interference | HIGH | verify locates challenge by `clientDataJSON` hash + purpose + binding (no latest fallback) | `fix-F02-F03-review.md` PASS |
| F04 business E2E gap | HIGH | E2E-03/E2E-04 real R22b flows + API readback + deterministic seed | `pr-17-e2e-business.md`; independently re-run 5/5 |
| F05 wrapped OCR errors | MEDIUM | typed `AIProviderError.category` threaded gateway→recognition→draft | `fix-F05-F07-review.md`, `fix-rework-review.md` PASS |
| F06 unbounded throttle | MEDIUM | length-bounded keys + capacity LRU + username max_length | `fix-F06-F01-review.md` PASS |
| F07 full-chain sanitization | HIGH debt | raw `response.text` removed at source; logs/persisted fields body-free | `fix-F05-F07-review.md` PASS |
| F08 backfill overclaim | MEDIUM | matrix row corrected to PARTIAL (NOT_YET_WIRED) | this file |
| Test isolation | P1 | 3 deselects removed; `test_pr09_verify_api_contract` idempotent | `fix-rework-review.md` PASS |

### Gate baseline after fixes (independently re-run)

| Check | Result | Evidence |
|---|---|---|
| Frontend | 70 files / 522 passed; tsc + test:typecheck exit 0 | `gate/tests/gate-frontend-v2.txt` |
| Backend (fresh, **no deselect**) | 922 passed / 0 failed / 9 skipped | `gate/tests/gate-backend-v2.txt` |
| Backend (reused DB, no deselect) | 922 passed / 0 failed / 9 skipped | `fix-rework-review.md` |
| Migration | fresh 001→033; 033↔032 (clean DB); single head 033 | `gate/migrations/gate-migration-replay-v2.log` |
| `build:cf` | exit 0 | `gate/ci/gate-buildcf-v2.txt` |
| Runtime smoke | referenced=20 ok=20 failed=0 | `gate/browser/gate-runtime-smoke-v2.txt` |
| E2E business (same-site, local) | 5/5 incl. E2E-03 wrong answer→draft, E2E-04 re-answer→ReviewRecord | `gate/ci/gate-e2e-v2.txt` |
| Remote CI | NOT_VERIFIED | push NOT_AUTHORIZED |
| Real OCR provider baseline | NOT_VERIFIED | no credentials; external calls out of scope |


