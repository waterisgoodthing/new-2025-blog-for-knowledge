# Week 4 TRACKING — RELEASE GATE (M4)

**Status**: PARTIAL (Gate, fix round 2026-09-26) — reassessment F01–F08 all fixed and independently reviewed; every locally-verifiable criterion PASSes (frontend 522; backend 922/0/9 with no deselects; E2E 5/5 business; smoke 20/0; single head 033). PARTIAL remains only for remote CI + real-provider OCR, both `NOT_VERIFIED` by authorization.
**Start Date**: 2026-09-26
**Prepared**: 2026-09-26
**Expected Duration**: 5 working days (may compress by parallelizing PR-19)
**Execution Mode**: WORKER
**Primary Owner / Final Code Acceptor**: main agent
**Routing Reason**: multi-stage, cross-domain (OCR / migration / auth / CI / cleanup), HIGH-risk boundaries (migration 033, login throttling), requires independent review and named gates — not SOLO.

> Companion docs: [README.md](README.md) (plan) · [tasks/](tasks/) (per-PR detail) · [week4-gate.md](tasks/week4-gate.md) (gate).

---

## 0. Authorization

| Scope | State | Note |
|---|---|---|
| Week 4 planning | COMPLETE | 2026-09-26 |
| Week 4 implementation (code/tests/docs) | **AUTHORIZED** | user approved 2026-09-26, local-only |
| Isolated scratch DB (`astra_week4_*`) + local browser verification | **AUTHORIZED** | must pass Week 4 scratch guard |
| Production DB / migration execution | NOT_AUTHORIZED | — |
| Commit / stage / push / merge | NOT_AUTHORIZED | — |
| Deployment to any environment | NOT_AUTHORIZED | — |
| Week 5+ / beyond 30-day plan | NOT_AUTHORIZED | — |

**Hard constraints**: never touch `blog_db` or `blog_v2`; preserve all pre-existing dirty changes; do not revert/reformat/stage unrelated files; PR-17 remote CI push is NOT_AUTHORIZED → CI jobs validated by local reproduction only, status reported honestly.

---

## 1. Orchestration (assignment plan)

Real subagents are dispatched per work package. Independence rule: implementer ≠ independent reviewer ≠ verifier. Main agent investigates/integrates and owns final accept. Available real subagent types in this environment: `explore` (read-only), `general` (read/write). Actual agent ids are recorded in the Execution Log when dispatched; the table below is the **planned** structure.

| Work package | Implementer (write scope) | Independent reviewer | Verifier / gate | Gate(s) |
|---|---|---|---|---|
| W4-00 preflight | inv-ocr / inv-auth / inv-cleanup (read-only evidence) + main (guard/baseline) | rev-w4-00 | main | G0 |
| PR-14 OCR | impl-14 (`backend/app/services/capture*`, `backend/app/schemas/capture.py`, capture UI, tests) | rev-14 | verify-14 (real browser) | G0, G4 |
| PR-15 WebAuthn | impl-15 (migration 033, models, `passkey_service.py`, routers, tests) | rev-15 | gate-db-15, gate-sec-15 | G0, G2, G3 |
| PR-19 AI governance | impl-19 (`docs/architecture/`, AI call sites, tests) | rev-19 | verify-19 | G0, G4 |
| PR-16 throttling | impl-16 (`config.py`, throttle service, auth router, tests) | rev-16 | gate-sec-16 | G0, G3 |
| PR-17 CI | impl-17 (`.github/workflows/`, `tests/e2e/`, config, docs) | rev-17 | verify-17 (local repro) | G0 |
| PR-18 cleanup | impl-18 (dead-code removal, evidence docs) | rev-18 | verify-18 | G0 |
| Week 4 Gate | — | final-review | gate-db, gate-sec, verify-gate | G2/G3/G4 |

Non-simple results require a real separate reviewer with no implementation ownership. A persona switch is only a perspective pass.

---

## 2. Execution Order (serial, per W4-D01)

```text
W4-00 preflight
→ PR-14 OCR diagnostic + UI
→ PR-15 WebAuthn challenge table (033)
→ PR-19 AI governance (parallel-eligible) ‖ PR-16 login throttling
→ PR-17 CI four jobs
→ PR-18 legacy cleanup
→ Week 4 Gate
```

HIGH migrations (033) run serially and not in parallel with other migrations. PR-19 is MEDIUM and may run alongside PR-15/16.

---

## 3. Work Package Tracking

### W4-00 — Preflight and scope lock — `PASS`

| Item | Status | Evidence |
|---|---|---|
| Baseline snapshot (dirty worktree) | PASS | `evidence/w4-00-baseline.diff` (+status/diffstat) |
| Migration head = 032 verification | PASS | `evidence/w4-00-migration-head.txt` (single head 032) |
| OCR flow/failure inventory | PASS | `evidence/w4-00-ocr-inventory.md` |
| WebAuthn/login inventory | PASS | `evidence/w4-00-webauthn-inventory.md` |
| Legacy cleanup inventory | PASS | `evidence/w4-00-cleanup-candidates.md` |
| Week 4 scratch guard + tests | PASS | `scripts/week4-scratch-guard.py` + `.test.py` (37 OK); `scratch_db_safety.py` extended |
| Decision lock (W4-D + W4-E deltas) | PASS | `evidence/w4-00-decisions.md` |

> Plan-vs-reality deltas recorded as `W4-E01..W4-E07` in `evidence/w4-00-decisions.md`. Note: migration 027–032 are untracked in git; head is nonetheless a single 032, which is the operative fact for authoring 033.

### PR-14 — OCR diagnostic and UI — `PASS_WITH_NOTES`

| Item | Status | Evidence |
|---|---|---|
| Failure taxonomy enum + derived DTO field | PASS | `capture_failure_taxonomy.py`; `schemas/capture.py` (computed) |
| Service categorical instrumentation (sanitized) | PASS | `capture_recognition.py`, `capture_ai_draft.py` |
| Local 10-sample baseline report | PASS (local harness) | `evidence/pr-14-ocr-baseline-report.md` (real-provider rate NOT_VERIFIED) |
| UI loading/success/error/empty + retry + stage-aware | PASS | `capture-workspace.tsx`; `evidence/pr-14-chromium-states.md` (pending real browser) |
| Entry-point decision (no unproven disable) | PASS | `w4-00-decisions.md` W4-E02 |
| Tests (taxonomy, DTO, sanitization, states) | PASS | backend 37 passed; vitest 8 passed; review recheck |
| Independent review | PASS_WITH_NOTES | `evidence/pr-14-review.md` (F1–F5 closed; F6/F7 LOW open) |

### PR-15 — WebAuthn challenge table — `PASS` (fix round)

> Reassessment F02 (CLI cross-event-loop) and F03 (ceremony interference) fixed and independently
> reviewed (`evidence/fix-F02-F03-review.md` PASS). Migration/model/tests remain valid.

| Item | Status | Evidence |
|---|---|---|
| Migration 033 (`webauthn_challenges`) | PASS | single head 033; `evidence/pr-15-migration-replay.log` |
| Model + registry + startup pin reconciled to 033 | PASS | `models/webauthn_challenge.py`, `main.py:17`, test pins |
| DB-backed generate/store/verify+consume/gc | PASS | `webauthn_challenge_service.py`, `passkey_service.py` |
| Three ceremonies preserved | PASS | `evidence/pr-15-integration-tests.txt` (4 passed) |
| Isolation tests (concurrent/expired/consumed/cross-purpose) | PASS | `evidence/pr-15-unit-tests.txt` (10 passed) |
| Independent review | PASS | `evidence/pr-15-review.md` (F1 BLOCKER + F2 HIGH closed; W4-E08 amendment) |
| Design deviation (raw challenge retained) | ACCEPTED | `w4-00-decisions.md` §2b W4-E08; `pr-15-design-deviation.md` |

### PR-19 — AI governance closure — `PASS`

| Item | Status | Evidence |
|---|---|---|
| `docs/architecture/ai-governance.md` | PASS | doc (polish exempt; backfill helper NOT_YET_WIRED) |
| AI call-site audit | PASS | `evidence/pr-19-ai-call-audit.md` (15 gaps documented) |
| Modification-type target linkage | PASS | gateway + capture threads; tests |
| Creation-type backfill helper + contract | PASS | `ai_run_service.backfill_ai_run_target`; prospective |
| AiRun query spot-check | PASS | `evidence/pr-19-airun-query.txt` (linked 1/3→2/3) |
| Independent review | PASS | `evidence/pr-19-review.md` (F1 HIGH closed) |

### PR-16 — Login throttling — `PASS`

| Item | Status | Evidence |
|---|---|---|
| Throttle config in `config.py` | PASS | `LOGIN_THROTTLE_*` + parser |
| Dual-dimension tracker service | PASS | `services/login_throttle.py` |
| Router integration (delay before auth) | PASS | `auth.py` login; 401 detail unchanged |
| Delay schedule + reset + TTL tests | PASS | `evidence/pr-16-unit-tests.txt` (14 passed) |
| Real timing + dual-dimension integration | PASS | `evidence/pr-16-integration-timing.txt` (real 2.005s) |
| Independent review | PASS | `evidence/pr-16-review.md` (F1 MEDIUM IP-TTL bug closed) |

### PR-17 — CI four jobs — `PASS` (fix round)

> Reassessment F01 (CI guard blocker) and F04 (business E2E gap) fixed and independently reviewed:
> 3 DB jobs use `astra_week4_ci` (guard-compatible, `fix-F06-F01-review.md`); E2E-03/04 restore the
> R22b business flows with backend readback (independently re-run 5/5, `pr-17-e2e-business.md`).
> Remote CI remains `NOT_VERIFIED` (push not authorized).

| Item | Status | Evidence |
|---|---|---|
| `.github/workflows/ci.yml` (4 jobs) | PASS | ci.yml (frontend/backend/runtime-smoke/e2e) |
| 5 Playwright E2E specs (`workers=1`) | PASS (listed) | `tests/e2e/*.spec.ts` |
| Local reproduction (Job1-3) | PASS | `evidence/pr-17-ci-run-local.txt` (Job1/3 green; smoke 0 failed) |
| Job2 deterministic green | PASS | 883 passed / 3 deselected (pre-existing isolation debt) |
| Remote CI green / intentional-break | NOT_VERIFIED | push NOT_AUTHORIZED |
| E2E local end-to-end | NOT_VERIFIED | cross-site cookie topology; locators statically verified |
| Independent review | PASS_WITH_NOTES | `evidence/pr-17-review.md` (R01–R03 closed) |

### PR-18 — Legacy cleanup — `PASS_WITH_NOTES`

| Item | Status | Evidence |
|---|---|---|
| Candidate classification (SAFE/IN_USE/UNCLEAR) | PASS | `evidence/w4-00-cleanup-candidates.md` |
| Deletions (4 files + 1 dead import) | PASS | `evidence/pr-18-cleanup-components.md` |
| Full frontend suite + type checks after | PASS | 522 passed; tsc/test:typecheck exit 0 |
| Summary + net lines removed | PASS | `evidence/pr-18-summary.md` (124 lines; plan ≥500 NOT met) |
| Independent review | PASS_WITH_NOTES | `evidence/pr-18-review.md` (R-01 tracking reconciled now) |

### Week 4 Gate — `PARTIAL` (fix round 2026-09-26)

> Reassessment F01–F08 were confirmed and then **fixed**, each with independent review. All
> locally-verifiable criteria PASS; PARTIAL remains only for remote CI + real-provider OCR
> (`NOT_VERIFIED` by authorization).

| Item | Status | Evidence |
|---|---|---|
| Reassessment recheck | CONFIRMED then addressed | `evidence/gate/reassessment-verification.md` |
| F01 CI test-DB blocker | FIXED | `fix-F06-F01-review.md` PASS; jobs use `astra_week4_ci` |
| F02 CLI cross-loop regression | FIXED | `fix-F02-F03-review.md` PASS; two options 200/200 |
| F03 ceremony interference | FIXED | `fix-F02-F03-review.md` PASS; hash+binding match |
| F04 R22b E2E coverage gap | FIXED | `pr-17-e2e-business.md`; re-run 5/5 |
| F05 wrapped OCR errors | FIXED | `fix-F05-F07-review.md`, `fix-rework-review.md` PASS |
| F06 unbounded account throttle | FIXED | `fix-F06-F01-review.md` PASS |
| F07 full-chain log sanitization | FIXED | `fix-F05-F07-review.md` PASS |
| F08 backfill overclaim | FIXED (doc) | matrix row → PARTIAL |
| Test isolation (3 deselects) | FIXED | fresh + reused 922/0/9; deselects removed |
| Frontend / Backend / Migration / build:cf / smoke / E2E | PASS | `evidence/gate/*-v2.*` |
| Remote CI / real OCR baseline | NOT_VERIFIED | push + credentials not authorized |

---

## 4. Decision Log

| ID | Decision | Status | Date |
|---|---|---|---|
| W4-D01 | Serial order: W4-00 → PR-14 → PR-15 → PR-19 ‖ PR-16 → PR-17 → PR-18 → Gate | LOCKED | 2026-09-26 |
| W4-D02 | OCR diagnostic priority: taxonomy + baseline + UI, no pipeline rewrite | LOCKED | 2026-09-26 |
| W4-D03 | WebAuthn challenge table schema: purpose + binding keys + TTL | LOCKED | 2026-09-26 |
| W4-D04 | Throttling: dual-dimension (account+IP), graduated delays, no lockout | LOCKED | 2026-09-26 |
| W4-D05 | Polish is transient preview (exempt); persisted AI must link target_id | LOCKED | 2026-09-26 |
| W4-D06 | CI four jobs: frontend, backend, runtime smoke, E2E at workers=1 | LOCKED | 2026-09-26 |
| W4-D07 | Legacy cleanup: three-part evidence (grep + test + runtime) required | LOCKED | 2026-09-26 |
| W4-E01 | PR-14 adds no migration/column; taxonomy derived from existing `error_code` | FINAL | 2026-09-26 |
| W4-E02 | OCR real-provider baseline NOT_VERIFIED; no unproven entry-point disable | FINAL | 2026-09-26 |
| W4-E03 | PR-15 challenge funcs gain `db` param; per-ceremony consume semantics preserved | FINAL | 2026-09-26 |
| W4-E04 | PR-16 account throttle key = `username` (no email field exists) | FINAL | 2026-09-26 |
| W4-E05 | PR-19 wires gateway `target_type`/`target_id`; Capture → target linkage | FINAL | 2026-09-26 |
| W4-E06 | PR-17 CI locally reproduced only; remote push NOT_AUTHORIZED | FINAL | 2026-09-26 |
| W4-E07 | PR-18 deletes only the 5 verified dead items; others IN_USE/UNCLEAR | FINAL | 2026-09-26 |
| W4-E08 | WebAuthn raw `challenge` column retained (supersedes D03 hash-only); never logged | FINAL | 2026-09-26 |
| W4-E09 | CI Job 2 omits ruff/mypy (not in repo toolchain); install+pytest only | FINAL | 2026-09-26 |
| W4-E10 | Reserved ui-v2 tree excluded from `test:typecheck` only (not routed/pending approval) | FINAL | 2026-09-26 |
| W4-E11 | CI Job 2 deselects exactly 3 pre-existing test-isolation failures (tracked debt) | FINAL | 2026-09-26 |

Main-agent execution-time decisions (W4-E*) will be appended here as they are finalized.

---

## 5. Gate Matrix (living)

| Criterion | Target | Current | Evidence |
|---|---|---|---|
| OCR baseline | ≥8/10 OR entry marked/disabled | NOT_STARTED | `pr-14-ocr-baseline-report.md` |
| WebAuthn migration 033 | fresh + incremental replay PASS | NOT_STARTED | `pr-15-migration-replay.log` |
| WebAuthn security cases | concurrent/expired/consumed/cross-purpose rejected | NOT_STARTED | `pr-15-unit-tests.txt` |
| AI governance classification | polish decision recorded | NOT_STARTED | `ai-governance.md` |
| AI target linkage | persisted calls write target_id | NOT_STARTED | `pr-19-*` |
| Login throttling | delay schedule 0/0/0/2s/5s/15s PASS | NOT_STARTED | `pr-16-unit-tests.txt` |
| Throttling dual dimension + timing | account+IP enforced; real timing | NOT_STARTED | `pr-16-integration-timing.txt` |
| CI four jobs | all defined + locally reproduced | NOT_STARTED | `gate/ci/` |
| Legacy cleanup | three-part evidence complete | NOT_STARTED | `pr-18-summary.md` |
| Migration head | single head 033 | NOT_STARTED | `gate/migrations/` |
| Frontend tests | 69 files / 516+ PASS | NOT_STARTED | `gate/tests/` |
| Backend tests | 821+ passed / ≤4 failed / ≤9 skipped | NOT_STARTED | `gate/tests/` |
| Type checks | `tsc --noEmit` exit 0; `mypy` | NOT_STARTED | `gate/tests/` |
| Runtime smoke | 0 failures, health 200 | NOT_STARTED | `gate/browser/` |
| `git diff --check` | clean | NOT_STARTED | `gate/` |

---

## 6. Risk Register

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| OCR baseline <80% success | MEDIUM | Mark entry experimental/disabled; Gate passes with honest disclosure | PR-14 |
| WebAuthn ceremony breakage | HIGH | Preserve exact call signatures; test all three ceremonies with real DB | PR-15 |
| Throttling UX degradation | MEDIUM | Graduated delays (no delay until 4th attempt); configurable | PR-16 |
| PR-17 remote CI not runnable locally | MEDIUM | Validate via local reproduction; report CI-green as NOT_VERIFIED (push unauthorized) | PR-17 |
| Legacy cleanup deletes live code | HIGH | Three-part evidence; incremental deletion; full tests after each | PR-18 |
| Plan-vs-reality drift (task files assume paths/classes) | HIGH | W4-00 inventory records DELTAS; adapt to current source | W4-00 |
| Existing dirty worktree overlap | HIGH | Baseline snapshot; never revert/stage unrelated changes | all |

---

## 7. Execution Log (append-only)

| Date | Work pkg | Actor | Action | Result |
|---|---|---|---|---|
| 2026-09-26 | — | main | Plan confirmed; tracking document established | IN_PROGRESS |
| 2026-09-26 | W4-00 | inv-ocr (`ses_f23c32589ffe4vpdih0m2JnbYc`) | OCR/capture read-only inventory → evidence | PARTIAL (plan deltas found) |
| 2026-09-26 | W4-00 | inv-auth (`ses_f23c31b35ffeejrShrVmyskbhs`) | WebAuthn/login/AiRun inventory → evidence | PARTIAL (plan deltas found) |
| 2026-09-26 | W4-00 | inv-cleanup (`ses_f23beedcbffeklgWviAvFqVn0m`) | Legacy cleanup classification → evidence | 5 SAFE / 7 IN_USE / 6 UNCLEAR |
| 2026-09-26 | W4-00 | main | Baseline + migration head (single 032) + scratch guard (37 OK) + decision lock | PASS |
| 2026-09-26 | PR-14 | impl-14 → rev-14 → rework → recheck | taxonomy/UI/logs; F1/F2 HIGH closed | PASS_WITH_NOTES |
| 2026-09-26 | PR-15 | impl-15 → rev-15 → rework → recheck | migration 033; F1 BLOCKER + F2 HIGH closed | PASS |
| 2026-09-26 | PR-19 | impl-19 → rev-19 → rework → recheck | gateway target linkage; F1 HIGH closed | PASS |
| 2026-09-26 | PR-16 | impl-16 → rev-16 → rework → recheck | dual-dimension throttle; F1 MEDIUM closed | PASS |
| 2026-09-26 | PR-17 | impl-17 → rev-17 → rework → recheck | CI 4 jobs; R01–R03 closed | PASS_WITH_NOTES |
| 2026-09-26 | PR-18 | impl-18 → rev-18 | 5 dead items removed; R-01 reconciled | PASS_WITH_NOTES |
| 2026-09-26 | Gate | main + gate-final-review | migration replay, baseline, build:cf, smoke; PARTIAL justified | PARTIAL |

---

## 8. Evidence Index

Root: `docs/workflows/personal-learning-system-convergence/week4/evidence/`

```text
w4-00-baseline.diff
w4-00-migration-head.txt
w4-00-ocr-inventory.md
w4-00-webauthn-inventory.md
w4-00-cleanup-candidates.md
pr-14-ocr-baseline-report.md
pr-14-chromium-states.md
pr-15-migration-replay.log
pr-15-unit-tests.txt
pr-15-integration-tests.txt
pr-19-ai-call-audit.md
pr-19-airun-query.txt
pr-19-tests.txt
pr-16-unit-tests.txt
pr-16-integration-timing.txt
pr-17-ci-run-local.txt
pr-18-cleanup-*.md
pr-18-summary.md
gate/
  week4-gate-matrix.md
  week4-gate-summary.md
  migrations/
  tests/
  ci/
  browser/
```

---

## 9. Notes

- PR-19 may run in parallel with PR-15/16 (MEDIUM, no migration/auth dependency).
- All other work packages are serial; HIGH migration 033 does not run in parallel with other migrations.
- Week 4 closes the 30-day convergence plan (M1→M2→M3→M4). No work beyond Week 4 is authorized.
- Final code accept does not imply commit, push, merge, migration, deployment, or production writes.
