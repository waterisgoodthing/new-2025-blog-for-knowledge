# Week 4 Gate — Final Independent Review

Reviewer role: FINAL INDEPENDENT GATE REVIEWER (implemented nothing in Week 4).
Date: 2026-09-26 16:01 CST.
Mode: READ-ONLY. No source modified; no git write; only this evidence file created.
Repo: `/Users/limengyang/2025-blog-public` @ `refactor/baseline` `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`.
Scope check: matches the matrix's stated scope (`local + isolated scratch DB only`).

---

## Verdict

**PARTIAL — JUSTIFIED.** Every locally-verifiable, in-scope criterion is independently reproduced
or supported by authentic evidence, and the three `NOT_VERIFIED` items are genuine
authorization/environment boundaries (not hand-waving). `PARTIAL` is therefore an honest status,
not a product defect.

**FAIL findings: none. BLOCKED: no.** Two **inconsistencies/understatements** were found (both
residual-risk, neither invalidates a PASS row):

1. **Backend non-hermeticity is materially understated.** The gate reports the reused-DB debt as
   "3 tests deselected". Independently reproduced: on a *reused* scratch DB the full suite yields
   **19 failed / 843 passed / 21 errors**, not 883 passed. The 883/0/9/3 figure is only reproducible
   on a **fresh** DB (confirmed). The suite is not re-runnable in place; this is much larger than the
   "3 deselected" framing.
2. **`build:cf` evidence file carries no literal exit code.** `gate/ci/gate-buildcf.txt` ends at
   `OpenNext build complete.` with no captured `exit=0`. `build:cf exit 0` is asserted in the CI
   local-run narrative and implied by the full `job3-buildcf.txt`, but the cited artifact itself does
   not record an exit status. Minor evidence gap, not falsified.

---

## Per-criterion verification

Legend: **SUPPORTED** = referenced evidence exists and the claim holds (reproduced where cheap);
**SUPPORTED (as reported)** = evidence authentic and the claim is accurately self-limited;
**UNSUPPORTED** = claim not backed.

| # | Criterion (matrix) | Matrix status | Independent verdict | Basis |
|---|---|---|---|---|
| 1 | PR-14 failure taxonomy, 8 categories | PASS | **SUPPORTED** | `capture_failure_taxonomy.py:13-24` = 8 enum members; `test_capture_taxonomy.py` passes (targeted rerun) |
| 2 | PR-14 10-sample baseline ≥8/10 OR entry disabled | PARTIAL | **SUPPORTED (as reported)** | `pr-14-ocr-baseline-report.md` §1/§3: deterministic local only, real rate `NOT_VERIFIED`, entry intentionally not disabled (W4-E02) |
| 3 | PR-14 UI states | PASS | **SUPPORTED** | `capture-workspace.tsx` + `capture-workspace.test.tsx`; `pr-14-review.md` F4 recheck CLOSED; suite passes |
| 4 | PR-15 migration 033 fresh + incremental replay | PASS | **SUPPORTED** | `gate/migrations/gate-migration-replay.log`: fresh 001→033, downgrade 033→032, upgrade 032→033, heads `033`; I re-ran `alembic upgrade head` on a fresh DB → `033 (head)` |
| 5 | PR-15 challenge lifecycle | PASS | **SUPPORTED** | `pr-15-unit-tests.txt` 10 passed; `test_webauthn_challenge_lifecycle.py` rerun green |
| 6 | PR-15 three ceremonies | PASS | **SUPPORTED** | `pr-15-integration-tests.txt` 4 passed; `test_passkey_ceremonies.py` rerun green; test names cover registration/auth/operator |
| 7 | PR-15 security cases (concurrent/expired/consumed/cross-purpose) | PASS | **SUPPORTED** | Test names present (`test_expired_challenge_is_rejected`, `test_consumed_challenge_cannot_be_reused`, `test_cross_purpose_lookup_is_rejected`, `test_concurrent_ceremonies_store_independent_rows`) |
| 8 | PR-19 polish classification documented | PASS | **SUPPORTED** | `docs/architecture/ai-governance.md` exists |
| 9 | PR-19 target linkage writes target_id | PASS | **SUPPORTED** | `test_ai_governance.py` rerun green; gateway threading cited |
| 10 | PR-19 creation backfill | PASS (prospective) | **SUPPORTED (as reported)** | `backfill_ai_run_target` defined `ai_run_service.py:178`; `grep` shows only definition + tests, **no production caller**; doc explicitly `NOT_YET_WIRED` (`ai-governance.md:48,51,96,98`) |
| 11 | PR-16 delay schedule | PASS | **SUPPORTED** | `pr-16-unit-tests.txt` 14 passed (`test_delay_schedule_graduated_and_capped`) |
| 12 | PR-16 account reset | PASS | **SUPPORTED** | `test_account_counter_resets_on_success`, `test_successful_login_resets_account_delay` |
| 13 | PR-16 real timing 4th ≈2s | PASS | **SUPPORTED** | `pr-16-integration-timing.txt:11` `elapsed=2.005s` |
| 14 | PR-16 dual dimension + IP TTL decay | PASS | **SUPPORTED** | `pr-16-unit-tests.txt` + `pr-16-review.md` recheck F1 (IP-TTL eviction) CLOSED |
| 15 | PR-17 four jobs defined | PASS | **SUPPORTED** | `.github/workflows/ci.yml` jobs `frontend`/`backend`/`runtime-smoke`/`e2e` |
| 16 | PR-17 Job 1 frontend local | PASS | **SUPPORTED** | **Reproduced**: vitest 70 files / 522 passed; `tsc --noEmit` exit 0; `test:typecheck` exit 0 |
| 17 | PR-17 Job 2 backend local | PASS | **SUPPORTED (fresh DB only)** | **Reproduced on fresh `astra_week4_review`**: 883 passed / 0 failed / 9 skipped / 3 deselected. Reused DB → 19 failed + 21 errors (see inconsistency 1) |
| 18 | PR-17 Job 3 runtime smoke local | PASS | **SUPPORTED (not re-run)** | `job3-buildcf.txt` (118 lines, real Next route table/versions), `job3-backend.log`, `job3-preview.log`, `job3-smoke.txt` (ok=20 failed=0); inspected only |
| 19 | PR-17 Job 4 E2E local | PARTIAL | **SUPPORTED (as reported)** | `job4-e2e.txt`: E2E-05 pass, E2E-01..04 fail in shared login (`管理面板` never visible); `pr-17-review.md` R01/R02 CLOSED statically; post-rework only `--list` run (no browser) |
| 20 | PR-17 remote CI green / intentional break | NOT_AUTHORIZED / NOT_VERIFIED | **SUPPORTED (genuine)** | push not authorized; agreed boundary |
| 21 | PR-18 three-part evidence per item | PASS | **SUPPORTED** | `pr-18-cleanup-components.md` exists; 5 items each grep+test+no-surface |
| 22 | PR-18 deletion safety | PASS | **SUPPORTED** | 522 passed after (reproduced); `pr-18-review.md` |
| 23 | PR-18 net reduction ≥500 | PARTIAL (NOT MET) | **SUPPORTED (as reported)** | `git diff --numstat`: 64+26+6+27 = 123 deleted + 1 import line = **124**; honestly disclosed |
| 24 | Baseline frontend tests | PASS | **SUPPORTED** | Reproduced 70/522 (target was 69/516+) |
| 25 | Baseline backend tests | PASS | **SUPPORTED (fresh DB)** | Reproduced 883/0/9/3 on fresh DB; target 821+/≤4 failed/≤9 skipped |
| 26 | Baseline type checks | PASS | **SUPPORTED** | Reproduced both exit 0 |
| 27 | Baseline migration head single 033 | PASS | **SUPPORTED** | No migration has `down_revision="033"`; `revision="033"` only; `main.py:17` = `"033"`; `alembic heads` → `033` |
| 28 | Baseline runtime smoke 0 fail, health 200 | PASS | **SUPPORTED (not re-run)** | `gate-runtime-smoke.txt` ok=20 failed=0; `gate-backend.log` GET /api/health 200 |
| 29 | Baseline `build:cf` exit 0 | PASS | **SUPPORTED w/ gap** | `job3-buildcf.txt` authentic full build; cited short file has no literal exit code (inconsistency 2) |
| 30 | `git diff --check` clean | PASS | **SUPPORTED** | Reproduced: exit 0, no whitespace errors |

### PR review rechecks (item 5 spot-check)

All required independent reviews exist and their top findings are marked CLOSED in an appended
recheck section:

| File | Finding | Severity | Recheck status |
|---|---|---|---|
| `pr-14-review.md` | F1 derived DTO category / F2 raw body logging | HIGH ×2 | **CLOSED** (§7 round 2) |
| `pr-15-review.md` | F1 stale revision pin / F2 raw challenge storage | BLOCKER + HIGH | **CLOSED** (§recheck; F2 by amendment W4-E08) |
| `pr-17-review.md` | R01/R02 strict-mode locators / R03 Job 2 red | HIGH ×3 | **CLOSED** (§recheck) |
| `pr-19-review.md` | F1 backfill overclaim | HIGH | **CLOSED** (§Recheck; helper real, doc `NOT_YET_WIRED`) |
| `pr-16-review.md` | F1 IP-TTL eviction bug | MEDIUM | **CLOSED** (§recheck) |
| `pr-18-review.md` | R-01 tracking drift | MEDIUM | reconciled (SUMMARY) |

No BLOCKER/HIGH was left open. `pr-18-review.md` R-02 (metric not stated) and R-03
(`readFileAsText` still exported) are LOW and accurately disclosed as follow-ups.

### NOT_VERIFIED genuineness (item 4)

| Item | Genuine? | Evidence |
|---|---|---|
| OCR real-provider rate | **YES** | No provider credentials; `pr-14-ocr-baseline-report.md` runs a mocked deterministic harness; external calls out of local scope |
| Remote CI all-four-jobs + intentional break | **YES** | Push `NOT_AUTHORIZED` (TRACKING §0); no remote run evidence claimed |
| E2E-01..04 same-site topology | **YES** | Independently tested: sandbox resolver maps `app.lvh.me`, `app.127.0.0.1.nip.io`, `app.loca.lt`, `app.ci.test` all to `198.18.1.x` (not loopback); `/etc/hosts` has no ci.test entry; no passwordless sudo. The `*.localhost` vs `localhost` local pairing is cross-site under Chromium's eTLD+1 rule while CI `app.ci.test`/`api.ci.test` share `ci.test`. Reproducing the CI topology locally is genuinely blocked |

### DB safety (item 6)

- No production/private DB write found: `grep` over `evidence/**` for write-ish commands targeting
  `blog_db`/`blog_v2` returns **nothing**; all mentions are explicit "did not touch" statements.
- All scratch DBs used are `astra_week4_*`: `astra_week4_gate`, `_pr14`, `_pr15`, `_pr16`, `_pr17`,
  `_pr17r`, `_pr19`. `scripts/week4-scratch-guard.py` fail-closes on `blog_db`/`blog_v2` and
  non-allowlisted names; its standalone test behaves correctly (rejects `production_db`, remote
  host, missing child command).
- `blog_db`/`blog_v2` appear in `.github/workflows/ci.yml` only as the **ephemeral GitHub Actions
  postgres service** name — not the local production DB, and never executed locally.

### Worktree preservation (item 7)

- Baseline `w4-00-baseline-status.txt`: **163** entries. Current `git status --short`: **202**
  entries (81 modified/deleted, 121 untracked).
- Every baseline modified/deleted path is still modified/deleted — **no baseline file reverted**
  (`comm -23` of the M/D sets is empty).
- Nothing is staged (`git diff --cached` = 0 files). `git diff --check` exit 0.
- Delta is Week 4 additions (migrations 027–033, new services/tests/docs), as expected.

---

## Raw evidence inspected

- Gate: `week4-gate-matrix.md`, `week4-gate-summary.md`.
- Tests: `gate/tests/gate-frontend.txt`, `gate/tests/gate-backend.txt`.
- Migrations: `gate/migrations/gate-migration-replay.log`.
- CI: `gate/ci/gate-buildcf.txt`, `gate-preview.log`, `gate-backend.log`, `job1-npm-test.txt`,
  `job1-npm-build.txt`, `job2-backend.txt`, `job3-{buildcf,preview,backend,smoke}.*`,
  `job4-{e2e,buildcf,backend}.*`, `job4-e2e-list-rework.txt`.
- Browser: `gate/browser/gate-runtime-smoke.txt`.
- Per-PR: `pr-14-ocr-baseline-report.md`, `pr-14-logs-sample.txt`, `pr-14-review.md`,
  `pr-15-{unit-tests,integration-tests,migration-replay,schema-dump,review}.*`,
  `pr-16-{unit-tests,integration-timing,review}.*`, `pr-17-ci-run-local.txt`, `pr-17-review.md`,
  `pr-18-{cleanup-components,summary,review}.md`, `pr-19-{ai-call-audit,airun-query,tests,review}.*`.
- Baseline: `w4-00-baseline-status.txt`, `w4-00-migration-head.txt`, `w4-00-decisions.md`.
- Source: `backend/main.py` (line 17), `backend/alembic/versions/*` (revision graph),
  `backend/tests/test_security_settings_guards.py:68`, `backend/app/services/capture_failure_taxonomy.py`,
  `.github/workflows/ci.yml`, `scripts/runtime-smoke.mjs`, `scripts/week4-scratch-guard.py`,
  `tests/e2e/*.spec.ts`, `playwright.config.ts`.

### Commands re-run by this reviewer (all on scratch DBs / read-only)

```text
npx vitest run                      -> 70 files / 522 passed
npx tsc --noEmit                    -> exit 0
npm run test:typecheck              -> exit 0
createdb astra_week4_review; alembic upgrade head -> 033 (head)   [guard-routed]
pytest tests/ on FRESH astra_week4_review -> 883 passed, 9 skipped, 3 deselected
pytest tests/ on REUSED astra_week4_review -> 19 failed, 843 passed, 21 errors  [pollution]
pytest (pr-14/15/16/19 suites)      -> 55 passed, 41 subtests
git status --porcelain | wc -l      -> 202   (baseline 163)
git diff --cached --name-only | wc -l -> 0
git diff --check                    -> exit 0
python3 scripts/week4-scratch-guard.test.py -> PASS/FAIL assertions behave correctly
```

Not re-run (expensive/blocked): `build:cf`, `npm run preview` + runtime smoke, Playwright browser
E2E, remote CI. These were judged from captured logs whose format, versions, chunk hashes, and
attachments are consistent with a real run.

---

## Overstated claims / missing evidence / inconsistencies

1. **Understated backend non-hermeticity (material).** `week4-gate-summary.md:45` frames the
   isolation debt as "3 tests deselected". Actual re-run failure surface on a reused DB is
   **19 failed + 21 errors**. Recommend restating as: "suite is single-shot on a fresh DB; any
   re-run on the same DB fails ~40 tests; fix isolation before treating 883/0 as repeatable."
2. **`build:cf` artifact lacks a literal exit status.** `gate/ci/gate-buildcf.txt` shows
   `OpenNext build complete.` only. `build:cf exit 0` is credible but not literally evidenced by the
   cited file.
3. **Job 4 evidence is pre-rework.** The only full E2E browser log (`job4-e2e.txt`) predates the
   R01/R02 `exact:true` locator fixes; post-rework only `--list` was captured. "E2E-05 pass" is from
   the pre-rework run; the fixed specs were never executed in a browser. The matrix correctly labels
   this PARTIAL and "locators statically verified", so it is disclosed — but a full PASS would need
   a post-rework browser run under same-site topology.
4. Nothing else: all `PASS` rows are backed by an existing referenced artifact, and no `NOT_VERIFIED`
   was downgraded into a false `PASS`.

---

## Residual risk and exact remaining verification for a full PASS

| # | Remaining verification | Why it blocks full PASS |
|---|---|---|
| 1 | Authorized push → remote CI runs all four jobs green; then intentional-break catches a failure | Matrix row 20 is `NOT_AUTHORIZED/NOT_VERIFIED` |
| 2 | Real-provider OCR 10-sample baseline (or explicitly waive + disable/label entry) | Matrix row 2 `PARTIAL` |
| 3 | Post-rework browser E2E-01..04 under same-site topology (and re-run E2E set) | Matrix row 19 `PARTIAL` |
| 4 | Fix backend test isolation; remove the 3 `--deselect` flags; confirm suite is repeatably green on reuse | Understated non-hermeticity (inconsistency 1) |
| 5 | Wire `backfill_ai_run_target` into a real confirmation endpoint | Row 10 is prospective `NOT_YET_WIRED` |
| 6 | Reach ≥500 net lines or formally retire the secondary metric | Row 23 `NOT MET` |

Non-blocking: PR-18 R-02/R-03 follow-ups (`readFileAsText` export; metric wording), and capturing
literal exit codes for expensive local commands.

---

## Decision needed

Accept M4 as **PARTIAL** with the six items above documented as the Week 5+ burn-down, or require an
authorized remote CI run (item 1) before closing the 30-day plan. No gate row failed independently;
the two inconsistencies should be corrected in the summary wording before the gate is treated as
repeatable.

---

# §Fix-round recheck — 2026-09-27

Reviewer role: same FINAL INDEPENDENT GATE REVIEWER. Mode: READ-ONLY. No source modified; no git
write; only this section appended.
Trigger: reassessment `quality-reassessment.md` judged M4 **FAIL** (F01–F08); the fix round claims
all are resolved. This section re-verifies against **current source**, not summaries.

## Verdict

**PARTIAL (fix round) — JUSTIFIED.** All eight reassessment defects F01–F08 are **CLOSED** on
independent re-verification, and every locally-verifiable criterion now PASSes. The gate is **not**
`FAIL` and **not** `BLOCKED`. `PARTIAL` persists solely because two acceptance items still require
authorization this run did not have: **remote GitHub Actions** and a **real-provider OCR baseline**.
The previous review's material inconsistency #1 (backend non-hermeticity) is **resolved**: the full
suite is now green on a **reused** DB as well as a fresh one.

## Per-finding status (F01–F08)

| ID | Claimed fix | Independent verdict | Basis (current source / repro) |
|---|---|---|---|
| F01 | 3 CI DB jobs use `astra_week4_ci`; no `blog_db` | **CLOSED** | `grep -n blog_db .github/workflows/ci.yml` → empty (exit 1); `astra_week4_ci` in `DATABASE_URL`/`POSTGRES_DB`/`pg_isready` for all 3 DB jobs (`ci.yml:55,65,69,120,131,135,218,232,236`); `grep -rn blog_db .github/` → none. Guard: accepts `astra_week4_ci` (exit 0), rejects `blog_db` (exit 1) and `blog_v2` (exit 1) |
| F02 | `cli.py` one server loop; two options 200/200 | **CLOSED** | `_ServerEventLoop` (one `new_event_loop()` on daemon thread `passkey-registration-loop`) created once in `create_registration_server` (`cli.py:159,169,172,217`) and used via `event_loop.run(...)` (`:229,262,293`); remaining `new_event_loop()` calls (`:387,434,...`) are one-shot subcommands, not the server path |
| F03 | verify locates challenge by `clientDataJSON` hash + purpose + binding | **CLOSED** | `passkey_service._resolve_client_challenge` hashes client bytes and calls `get_valid_challenge_by_hash(..., purpose, session_id=, user_id=)`, then re-checks raw bytes; returns `(None,None)` with **no latest fallback** (`passkey_service.py:48-80`); all three verify paths call it (`:131,:209,:276`); `get_valid_challenge` (latest) has **no product caller** (only its own def/docstring) |
| F04 | E2E-03/04 real R22b flows + API readback; 5/5 local | **CLOSED** | `tests/e2e/03-capture.spec.ts` (74 lines) captures `POST /api/admin/attempts` and reads back the draft; `tests/e2e/04-review-flow.spec.ts` (86 lines) reads back the ReviewRecord; `helpers.ts`/`global-setup.ts`/`seed_week4_business.py` present; `playwright.config.ts:9-23` adds `--host-resolver-rules=MAP api.ci.test/app.ci.test 127.0.0.1` + globalSetup; `gate-e2e-v2.txt` shows 5/5 (not re-run; see below) |
| F05 | typed `AIProviderError.category` threaded gateway→recognition→draft | **CLOSED** | `AIProviderError.category` + `ALLOWED_ERROR_CATEGORIES` (`ai_service.py:15,27,40`); gateway sets `failure_category=getattr(exc,"category",None)` (`ai_gateway.py:47,161,219`); recognition `_resolve_provider_category(gw.failure_category,…)` (`capture_recognition.py:101,147,166`); draft mirrors it (`capture_ai_draft.py:108,158,177-184`); cross-layer test `test_ai_error_chain.py` (18 tests) in the green suite |
| F06 | bounded account throttle state + username max_length | **CLOSED** | `_MAX_ACCOUNT_KEY_LENGTH=256` with sha256 key (`login_throttle.py:62,107-119`), capacity eviction `_evict_overflow_accounts` (`:138`) + `LOGIN_THROTTLE_MAX_ACCOUNTS=10000`; `LoginRequest.username` `max_length=100` (`schemas/auth.py:8`) |
| F07 | raw `response.text` removed at source | **CLOSED** | `grep -n "response\.text\|response\.content"` over `ai_service.py`/`ai_gateway.py`/`capture_recognition.py`/`capture_ai_draft.py` → **no matches** |
| F08 | matrix creation-backfill row corrected to PARTIAL | **CLOSED** | `week4-gate-matrix.md:22` now `PARTIAL`, "no production confirmation endpoint calls it (F08, documented NOT_YET_WIRED) — not scored PASS" |
| Test isolation | 3 deselects removed; fresh AND reused 922/0/9 | **CLOSED** | `grep -n deselect .github/workflows/ci.yml` → only explanatory comments (`:101,104`), no command flag; see raw reruns below |

## Raw results (re-run by this reviewer)

```text
npx vitest run            -> 70 files / 522 passed
npx tsc --noEmit          -> exit 0
npm run test:typecheck    -> exit 0
guard check --db-name astra_week4_ci  -> PASS (exit 0)
guard check blog_db / blog_v2         -> FAIL (exit 1) each
createdb astra_week4_gate_recheck; alembic upgrade head -> 033 (head)   [guard-routed]
BACKEND RUN 1 (fresh, no deselect):  922 passed, 9 skipped, 2 warnings, 47 subtests, 0 failed
BACKEND RUN 2 (REUSED same DB):      922 passed, 9 skipped, 2 warnings, 47 subtests, 0 failed
git status --porcelain | wc -l -> 206   ;   git diff --cached | wc -l -> 0
```

**Not re-run** (judged from captured logs only): `build:cf`, runtime smoke, and the Playwright
same-site E2E. Their post-fix logs are coherent: `gate-buildcf-v2.txt` (120 lines, real Next.js
16.2.12 route table + OpenNext bundle); `gate-runtime-smoke-v2.txt` (`referenced=20 ok=20 failed=0`,
same schema as the verified v1); `gate-e2e-v2.txt` (5/5 with real spec titles) with matching
`gate-e2e-backend.log` (real `OPTIONS` preflights + `/api/health` 200 on `:18001`) and
`job4-e2e-business-db-readback.txt` (real psql row counts). No command/exit line is captured for
`build:cf`, so "exit 0" is inferred from the completed bundle, as in v1.

## Fix-round review evidence (item 2)

| File | Verdict | Open BLOCKER/HIGH |
|---|---|---|
| `fix-F02-F03-review.md` | PASS | none (BLOCKER 0 / HIGH 0; 3 LOW test-coverage) |
| `fix-F05-F07-review.md` | PASS_WITH_NOTES (F07 PASS, F05 recognition PASS; 1 MEDIUM draft gap) | none at time; the MEDIUM is **closed** by the rework |
| `fix-rework-review.md` | PASS_WITH_NOTES | none (BLOCKER/HIGH/MEDIUM 0; closes the F05 draft gap, verifies no-deselect idempotency) |
| `fix-F06-F01-review.md` | PASS | none (BLOCKER 0 / HIGH 0) |
| `pr-17-e2e-business.md` | local PASS 5/5 (remote NOT_VERIFIED) | none |

No OPEN BLOCKER/HIGH remains in any fix-round review. F05's draft-path gap (MEDIUM in
`fix-F05-F07-review.md`) is genuinely closed: `capture_ai_draft.py:108,177-184` now consumes the
structured category, and the suite containing `test_ai_error_chain.py` is green.

## Overstated claims / inconsistencies

1. **Matrix body rows are stale (minor).** The main table still cites pre-fix artifacts/numbers —
   `gate/tests/gate-backend.txt` "883 passed, 3 deselected" (rows 31, 41) and old
   `gate-migration-replay.log` / `gate-buildcf.txt` / `gate-runtime-smoke.txt` paths — while the
   fix-round section and the summary/TRACKING/technical-report carry the v2 numbers (922/0/9,
   no deselect). It is **disclosed** (`week4-gate-summary.md:18-22` "Superseded statements";
   matrix "Overall" note), and the per-row *statuses* remain correct, so this is a presentation
   inconsistency, not a hidden overclaim. Recommend repointing the body rows to the `-v2` files.
2. **No other overstated claim found.** F01–F08 fixes are present in source, not just asserted.
   The prior review's non-hermeticity finding is fixed: 922/0/9 on both fresh and reused DB.

## NOT_VERIFIED check (item 5)

- **Remote CI (four jobs + intentional break):** still genuinely unverifiable — push is
  `NOT_AUTHORIZED` (TRACKING §0); no remote run is claimed. Genuine.
- **Real-provider OCR baseline:** still genuinely unverifiable — no provider credentials and
  external calls are outside local-only scope (`pr-14-ocr-baseline-report.md` §3). Genuine.
- E2E is **no longer** `NOT_VERIFIED`: F04 restores a local same-site run at 5/5
  (`gate-e2e-v2.txt`, `pr-17-e2e-business.md`).

## DB safety (item 4)

- `grep -rn blog_db|blog_v2` over the fix-round evidence returns only explicit *reject / not
  touched* statements; no write target. Scratch DBs used: `astra_week4_ci`, `_f04_e2e`, `_fix`,
  `_fix2`, `_gate2`, `_gate3`, `_pr15`, `_pr16`. `git diff --cached` = 0 files (nothing staged).

## Remaining verification for a full PASS

1. **Authorized push** → remote CI runs all four jobs green, then intentional-break is caught.
2. **Real-provider OCR** 10-sample baseline (or an explicit waiver/disabling of the entry).
3. Minor: repoint the matrix body rows to the `v2` evidence artifacts and restate the backend
   baseline as `922 passed / 0 failed / 9 skipped (no deselect)`.

## Decision needed

The fix round is independently **accepted as correcting all F01–F08**. Decide whether M4 closes at
**PARTIAL** with the two authorization-scoped `NOT_VERIFIED` items (remote CI, real OCR) as the
only residual, or whether an authorized remote CI run is required before closing the 30-day plan.
No defect remains on the local, in-scope surface; the gate does **not** warrant `FAIL` or `BLOCKED`.
