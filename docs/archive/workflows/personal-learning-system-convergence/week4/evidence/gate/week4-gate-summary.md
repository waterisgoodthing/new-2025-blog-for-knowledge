# Week 4 Gate Summary — RELEASE GATE (M4)

Date: 2026-09-26
Execution mode: WORKER (main agent = primary_owner / final code acceptor)
Authorization: local implementation + isolated scratch DB verification only.

## Overall outcome

**PARTIAL (fix round 2026-09-26)** — all reassessment defects F01–F08 are fixed and independently
reviewed; every locally-verifiable criterion PASSes, including the restored R22b business E2E and a
fully green backend suite with **no deselects** (fresh and reused DB). PARTIAL remains only for two
`NOT_VERIFIED` acceptance items that require authorization this run did not have: remote GitHub
Actions (no push) and a real-provider OCR baseline (no credentials). See the fix-round table in
`week4-gate-matrix.md`.

Supersedes the prior FAIL (F01–F08) and the earlier PARTIAL.

## Superseded statements

The `Completed work packages` / `Verified baseline` tables below are the pre-fix state. Current
numbers: frontend 522; backend 922 passed / 0 failed / 9 skipped (no deselect); E2E 5/5 business;
smoke 20/0; single head 033.


## Completed work packages

| WP | Risk | Outcome | Independent review |
|---|---|---|---|
| W4-00 preflight | MEDIUM | PASS | inventories + guard (37 tests) |
| PR-14 OCR diagnostic/UI | MEDIUM | PASS_WITH_NOTES | `pr-14-review.md` (F1/F2 HIGH closed) |
| PR-15 WebAuthn challenge (033) | HIGH | PASS | `pr-15-review.md` (F1 BLOCKER + F2 HIGH closed; W4-E08) |
| PR-19 AI governance | MEDIUM | PASS | `pr-19-review.md` (F1 HIGH closed) |
| PR-16 login throttling | HIGH | PASS | `pr-16-review.md` (F1 MEDIUM IP-TTL bug closed) |
| PR-17 CI four jobs | MEDIUM | PASS_WITH_NOTES | `pr-17-review.md` (R01–R03 closed) |
| PR-18 legacy cleanup | MEDIUM | PASS_WITH_NOTES | `pr-18-review.md` (R-01 reconciled) |

## Verified baseline (gate DB `astra_week4_gate`, head 033)

| Check | Result |
|---|---|
| Frontend | 70 files / 522 passed |
| Backend | 883 passed / 0 failed / 9 skipped / 3 deselected (pre-existing isolation debt, W4-E11) |
| `npx tsc --noEmit` / `npm run test:typecheck` | exit 0 / exit 0 |
| Migration | fresh 001→033; 033↔032 replay; single head **033** |
| `build:cf` | exit 0 |
| Runtime smoke | referenced=20 ok=20 failed=0; `/api/health` 200 |

## Deferred / NOT_VERIFIED (honest)

1. **OCR real-provider success rate** — NOT_VERIFIED (no credentials; external calls out of local scope). Entry-point intentionally not disabled on unverified data (W4-E02).
2. **Remote CI green + intentional-break** — NOT_AUTHORIZED (push not authorized).
3. **E2E-01..04 local end-to-end** — NOT_VERIFIED (local cross-site cookie topology; selectors statically verified). E2E-05 passes.
4. **PR-19 production backfill wiring** — `backfill_ai_run_target` exists and is tested, but no confirmation endpoint calls it yet (documented, prospective).
5. **PR-18 net reduction** — 124 lines, below the ≥500 secondary metric (only 5 items provably dead).

## Known limitations

- Backend suite is **non-hermetic**: the `883 passed / 0 failed / 9 skipped / 3 deselected` result is only valid on a **fresh** scratch DB. Re-running the full suite against a **reused/dirty** scratch DB yields many spurious failures (the final gate review observed ~19 failed + 21 errors on a reused DB). CI must therefore provision a fresh DB per run (as `.github/workflows/ci.yml` does). The 3 deselected tests are pre-existing isolation debt (W4-E11); fixing isolation is follow-up.
- Login throttling is **process-local** (restart/multi-worker resets counters); `request.client.host` only (no `X-Forwarded-For`).
- WebAuthn raw challenge is stored (required by the library) — W4-E08; never logged; single-use, TTL 300s.
- W4-E09: CI Job 2 has no ruff/mypy (repo has no such toolchain); W4-E10: reserved ui-v2 tree excluded from `test:typecheck` only.
- PR-17 E2E-01..04 were not browser-run post-rework (local cross-site cookie topology); post-rework locators were verified via `playwright test --list` and source audit only.

## Required follow-ups (Week 5+ candidates, NOT authorized here)

1. Authorized push to run remote CI (all four jobs) and the intentional-break check; validate Job 3/4 on ubuntu-latest.
2. Fix the 3 backend test-isolation failures and remove the `--deselect` debt.
3. Wire `backfill_ai_run_target` into a real confirmation endpoint.
4. Coordinated `/api/review` retirement unlocking `sm2.py` + `review_planner.py` + legacy `review.ts`; access-log proof for `/api/admin/diagnostics` and `/api/admin/workspace/files`; client-contract decision on orphan helpers.
5. OCR: run a real 10-sample provider baseline once credentials are available and revisit the entry-point decision.

## Decision needed

Week 4 Gate is **PARTIAL** only because remote CI and real-provider OCR cannot be verified under the
local-only authorization. Decide whether M4 is accepted with these documented `NOT_VERIFIED` items,
or whether an authorized remote CI run is required before closing the 30-day plan.
