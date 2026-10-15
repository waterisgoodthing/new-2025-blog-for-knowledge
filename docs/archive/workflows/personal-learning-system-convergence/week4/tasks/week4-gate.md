# Week 4 Gate — Final Verification

Status: **NOT_STARTED**  
Risk: HIGH  
Gates: G0, G2, G3, G4  
Dependencies: PR-14, PR-15, PR-19, PR-16, PR-17, PR-18

## Objective

Verify all Week 4 work packages pass their acceptance criteria and the system meets M4 (RELEASE GATE) milestone requirements before closing the 30-day convergence plan.

## Gate Matrix

| Criterion | Target | Evidence | Status |
|---|---|---|---|
| **PR-14: OCR Diagnostic** | | | |
| 10-sample baseline | ≥8/10 success OR entry marked/disabled | `evidence/pr-14-ocr-baseline-report.md` | |
| Failure taxonomy | All categories mapped, no unhandled exceptions | Unit tests PASS | |
| UI states | Loading/success/error/retry all functional | Chromium walkthrough | |
| **PR-15: WebAuthn Challenge** | | | |
| Migration 033 | Fresh + incremental replay PASS | `evidence/pr-15-migration-replay.log` | |
| Challenge lifecycle | Generate/store/verify/consume correct | Unit tests PASS | |
| Three ceremonies | Registration/auth/operator all work | Integration tests PASS | |
| Security | Concurrent/expired/consumed/cross-purpose rejected | Unit tests PASS | |
| **PR-19: AI Governance** | | | |
| Polish classification | Decision documented | `docs/architecture/ai-governance.md` | |
| Target linkage | Modification-type calls write target_id | Spot-check audit PASS | |
| Creation backfill | Confirmation updates target_id, abandonment → NULL | Integration tests PASS | |
| **PR-16: Login Throttling** | | | |
| Delay schedule | 0→0→0→2s→5s→15s for attempts 1-6+ | Unit tests PASS | |
| Account reset | Success clears counter | Unit tests PASS | |
| Real timing | Delay ≈ expected (±0.5s) | Integration test timing | |
| Dual dimension | Account + IP both enforced | Integration tests PASS | |
| **PR-17: CI Four Jobs** | | | |
| Job 1: Frontend | tsc, test:typecheck, vitest, build all PASS | CI run log | |
| Job 2: Backend | ruff, mypy, pytest (821+/≤4/≤9) PASS | CI run log | |
| Job 3: Runtime Smoke | build:cf + smoke 0 failures | CI run log | |
| Job 4: E2E | 5 tests PASS at workers=1 | CI run log | |
| **PR-18: Legacy Cleanup** | | | |
| Evidence completeness | 3-part proof for each deletion | Evidence docs | |
| Deletion safety | No new test failures | Test output | |
| Net reduction | ≥500 lines removed (secondary metric) | `git diff --stat` | |
| **Baseline Health** | | | |
| Frontend tests | 69 files / 516+ PASS | `npm test` | |
| Backend tests | 821+ passed / ≤4 failed / ≤9 skipped | `pytest` | |
| Type checks | exit 0 | `tsc --noEmit`, `mypy` | |
| Migration head | Single head at 033 | `alembic heads` | |
| Runtime smoke | 0 failures, all health 200 | `runtime-smoke.mjs` | |
| Build | `build:cf` exit 0 | Build log | |

## Verification Steps

### 1. Individual PR review

For each PR-14 through PR-18:

- [ ] Read PR task file
- [ ] Locate evidence files
- [ ] Verify acceptance criteria met
- [ ] Check independent review checklist items
- [ ] Note any PARTIAL or deferred items

### 2. Integration verification

- [ ] **Migration replay**: Fresh DB 000→033, downgrade 033→032, upgrade 032→033
- [ ] **Full test suite**:
  - Frontend: `npm ci && npm test` → record pass/fail counts
  - Backend: `cd backend && pytest` → record pass/fail/skip counts
  - Type checks: `npx tsc --noEmit && cd backend && mypy app` → exit codes
- [ ] **Runtime smoke**: `build:cf` → workerd + backend + PG → `node scripts/runtime-smoke.mjs` → 0 failures
- [ ] **Manual walkthrough**:
  - Login (verify throttling delay on 4th+ attempt)
  - Dashboard (verify data loads)
  - Create note (verify save)
  - OCR capture (verify error states and retry if failure)
  - Review flow (if due items exist)
  - WebAuthn registration (if test account allows)

### 3. CI verification

- [ ] Push test branch to trigger CI
- [ ] Verify all four jobs run
- [ ] Verify all four jobs PASS
- [ ] Intentional break (e.g., failing test) → verify CI catches it
- [ ] Fix break → verify CI passes

### 4. Evidence consolidation

- [ ] Collect all evidence files into `evidence/gate/`
- [ ] Create `evidence/gate/week4-gate-matrix.md` with filled-in Status column
- [ ] Create `evidence/gate/week4-gate-summary.md` with:
  - Overall outcome (PASS/FAIL/PARTIAL)
  - List of completed PRs
  - List of deferred items (if any)
  - Known limitations
  - Recommendations for Week 5+ (if plan continues)

### 5. Final report

- [ ] Create `week4-technical-report.md` following Week 1-3 format:
  - Conclusion
  - Status overview (table)
  - Key design and implementation
  - Execution record (if multi-agent)
  - Review findings and closure
  - Verification evidence
  - Known limitations and execution boundary
  - Risks/remaining/decisions

## Acceptance Criteria

### All PRs Complete
- [ ] PR-14: OCR diagnostic → PASS
- [ ] PR-15: WebAuthn challenge → PASS
- [ ] PR-19: AI governance → PASS
- [ ] PR-16: Login throttling → PASS
- [ ] PR-17: CI four jobs → PASS
- [ ] PR-18: Legacy cleanup → PASS

### Baseline Health
- [ ] Frontend tests: no new failures from Week 3 baseline
- [ ] Backend tests: 821+ passed, ≤4 failed, ≤9 skipped
- [ ] Type checks: exit 0
- [ ] Migration head: exactly 033
- [ ] Runtime smoke: 0 failures

### CI Green
- [ ] All four CI jobs pass on test push
- [ ] Intentional failure caught by CI
- [ ] Fix restores CI to passing

### Evidence Complete
- [ ] All evidence files in `evidence/gate/`
- [ ] Gate matrix fully filled
- [ ] Week 4 technical report written

## Stop Conditions

Stop and report FAIL if:

- Any PR's independent review finds a BLOCKER
- Migration 033 cannot replay cleanly
- Runtime smoke has >0 failures
- CI jobs consistently fail (not flake)
- Backend tests regress beyond Week 3 baseline (>4 failed)
- Any HIGH-risk PR (15, 16) introduces security vulnerability

## Decisions for User

If Week 4 Gate is PARTIAL (some PRs PASS, others deferred):

- Which PRs are mandatory for M4 milestone?
- Can deferred PRs be moved to Week 5+ (if plan extends)?
- Is M4 considered achieved with deferred items documented?

## Output Artifacts

- `evidence/gate/week4-gate-matrix.md` — filled gate matrix
- `evidence/gate/week4-gate-summary.md` — outcome and recommendations
- `evidence/gate/migrations/` — 033 replay logs
- `evidence/gate/tests/` — frontend and backend test outputs
- `evidence/gate/ci/` — CI run logs and screenshots
- `evidence/gate/browser/` — manual walkthrough screenshots
- `week4-technical-report.md` — comprehensive final report

## Estimated Duration

1-2 days
