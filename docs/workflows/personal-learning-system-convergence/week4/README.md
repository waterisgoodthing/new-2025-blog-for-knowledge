# Week 4 — RELEASE GATE execution plan

Status: **NOT_STARTED**  
Prepared: 2026-09-26  
Execution mode: **WORKER**; the main agent remains `primary_owner` and final code acceptor.

## 1. Outcome

Week 4 establishes the release gate by addressing the remaining high-risk gaps before the system can be considered production-ready:

1. **OCR diagnostic clarity** — understand the 31/31 failure baseline and establish visibility/retry/diagnosis flow
2. **Authentication hardening** — WebAuthn challenge lifecycle and login throttling
3. **AI governance closure** — finalize target-id discipline for persisted learning data
4. **CI completeness** — four-job pipeline with E2E coverage
5. **Legacy surface reduction** — remove dead code with evidence

This closes the 30-day convergence plan (M1→M2→M3→M4). Planning this week does **not** authorize implementation, production migration, commit, push, merge, deployment, or any work beyond Week 4.

## 2. Verified starting point

- Week 3 records its Gate as `PASS` on 2026-09-22 (user-decided; INC-01/INC-02 closed as process events).
- Current dirty worktree contains Week 1-3 implementations; migrations 027-032 exist.
- Source migration head is 032.
- Backend tests: 821 passed / 4 failed / 9 skipped (Week 3 final validation; 4 failures documented as test isolation/environment issues, not Week 3 regressions).
- Frontend tests: 69 files / 516 passed.
- CI: backend Job 2 runs on `.venv`; frontend Job 1 missing (Week 1 target deferred).
- OCR: 31/31 capture samples failed (baseline from earlier audit).
- WebAuthn: three global dict stores with `["current"]` single-key challenge (F15).
- Login: no throttling mechanism.

## 3. Decisions locked by this plan

### W4-D01 — Serial delivery order

Execute and accept each item before starting the next:

```text
W4-00 preflight and scope lock
→ PR-14 OCR diagnostic and UI
→ PR-15 WebAuthn challenge table
→ PR-19 AI governance closure (parallel-eligible, MEDIUM risk)
→ PR-16 login throttling
→ PR-17 CI four jobs
→ PR-18 legacy cleanup
→ Week 4 Gate
```

PR-19 (AI governance) can run in parallel with PR-15/16 since it is MEDIUM risk and does not touch auth/migrations. PR numbers follow the original 30-day plan.

### W4-D02 — OCR diagnostic priority (R10)

Week 4 does **not** rewrite the OCR pipeline. It establishes:

1. **Failure taxonomy**: `provider_auth / provider_timeout / invalid_model / invalid_response / schema_validation / image_fetch / image_format / unknown`
2. **Observable success rate**: instrument `capture_recognition` with categorical failure logging
3. **10-sample baseline**: controlled retry of 10 samples; target ≥8 successful completions
4. **UI contract**: failures must be visible, retryable, and diagnosable (not silent or presented as "no content")
5. **Entry-point honesty**: if the baseline remains <80% success, the Capture entry must be marked as experimental/unreliable or disabled

OCR candidate confirmation (PR-22), background status (PR-26), and pipeline rewrites are **NOT_AUTHORIZED** and do not block Week 4 Gate.

### W4-D03 — WebAuthn challenge lifecycle (R33)

Replace all three global dict stores (`registration_challenges`, `authentication_challenges`, `operator_challenges`) with a database table:

```sql
CREATE TABLE webauthn_challenges (
  id UUID PRIMARY KEY,
  challenge_hash VARCHAR(64) NOT NULL,  -- SHA-256 of the challenge bytes
  purpose VARCHAR(32) NOT NULL CHECK (purpose IN ('registration', 'authentication', 'operator_registration')),
  session_id VARCHAR(255),              -- binding key for operator_registration
  user_id UUID,                         -- binding key for user ceremonies
  created_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  consumed_at TIMESTAMP
);
```

Flow: `generate → store → verify(consume once) → garbage-collect expired`. Validation rules:

- Challenge must match `purpose` and binding key (session_id for operator, user_id for user ceremonies)
- Expired challenges are rejected
- Consumed challenges cannot be reused
- Concurrent ceremonies do not overwrite each other's challenges

The existing three-ceremony semantics (registration / authentication / operator_registration) remain unchanged; only the storage mechanism is replaced.

### W4-D04 — Login throttling (R34)

Dual-dimension recursive backoff:

- **Account-level failures**: track failures per `username` or `email`
- **IP-level failures**: track failures per client IP
- **Delay schedule** (configurable in `backend/app/config.py`):
  - Attempts 1-3: no delay
  - Attempt 4: 2s
  - Attempt 5: 5s
  - Attempt 6+: 15s
- Successful login resets the account-level counter; IP counter decay is time-based (configurable TTL)

No permanent lockout; no complex fraud detection. Single-user project priorities: availability > sophisticated abuse prevention.

### W4-D05 — AI governance polish classification (R11)

**Decision on record**: Polish is currently a **transient preview** (streaming `polish_stream`, no `target_id` in request, result only persists if user saves). This does not require forced AiRun linkage. If polish later becomes a direct-persist operation, it must first enter the audit chain.

**Enforcement for persisted data**: Any AI call that produces canonical learning entities (Capture→recognition/draft/question, Mistake generation, auto-tagging, diagram with saved artifacts) must record `target_type` and `target_id` in AiRun:

- **Modification-type calls** (acting on existing Note/Question/Mistake/Capture): write `target_id` at call time
- **Creation-type calls** (generating new entity): backfill `target_id` after user confirmation creates the entity; if user abandons the suggestion, `target_id` remains NULL (valid state)

Diagram generation is also classified: if purely visual aid, it is transient and does not require target linkage; if the diagram itself is saved as a learning artifact, it must be linked.

### W4-D06 — CI four-job contract (R22)

| Job | Content |
|---|---|
| Job 1: Frontend | `npm ci` → `tsc --noEmit` → `test:typecheck` → `vitest` → `next build` |
| Job 2: Backend | install → PostgreSQL service → `alembic upgrade head` (fresh DB) → `pytest` |
| Job 3: Runtime Smoke | `build:cf` → production preview (workerd + backend + PG) → runtime-smoke.mjs (asset/API health checks) |
| Job 4: Critical E2E | 5 Playwright flows at `workers=1` (E2E-01 through E2E-05, see R22b) |

Job 3/4 use the Phase 0 T-00b topology contract (workerd :8787, backend :8001, explicit `NEXT_PUBLIC_API_URL`, seed fixture). Jobs run independently; failure in any job blocks merge.

### W4-D07 — Legacy cleanup evidence (R18)

Every deletion must have three-part evidence:

1. **Static reference check**: `grep -r` or equivalent proves no remaining imports/calls
2. **Test coverage**: deleted module's tests are also removed or prove the module was untested
3. **Runtime evidence**: recent logs or a controlled runtime search proves the endpoint/service was unused

Deletion candidates (from tasks.md):

- Legacy review API client (if superseded by canonical review flow)
- Legacy SM-2 caller (F11, `backend/app/services/sm2.py` if no longer invoked)
- Broken Dashboard quick-action tests
- WIP components with no call sites
- Unused API endpoints
- Duplicate analytics surfaces (if canonical analytics replaced them)

Order: `identify → gather evidence → remove frontend → remove endpoint → remove service`. Database columns/tables are deferred to a separate authorized cleanup phase; Week 4 only removes application code.

## 4. Work packages and acceptance

### W4-00 — Preflight and scope lock

Risk: MEDIUM  
Gates: G0 requirement/domain

Tasks:

1. Snapshot the Week 3 dirty-worktree scope; identify Week 3-owned files; preserve all unrelated changes.
2. Verify source migration head is exactly 032; pin the scratch runtime expectation before writing 033.
3. Inventory current OCR failure taxonomy from logs/code; identify the 10-sample baseline fixture or selection criteria.
4. Inventory the three WebAuthn challenge stores and their call sites.
5. Inventory legacy SM-2, dead review clients, and unused endpoints with initial `grep` evidence.
6. Create a Week 4 guarded scratch runner that rejects `blog_db`, `blog_v2`, default `.env`, and any database name outside `astra_week4_*`.

Stop if migration head is not 032, the Week 3 diff cannot be isolated, OCR instrumentation points are unclear, or legacy cleanup candidates cannot be safely classified.

### PR-14 — OCR diagnostic and UI

Risk: MEDIUM  
Gates: G0, G4 recommendation

Implementation slice:

- add failure taxonomy enum and categorical logging to `capture_recognition` service
- instrument success/failure counts with observable metrics (can be log-based; no requirement for Prometheus/StatsD)
- run controlled 10-sample baseline: gather images, invoke recognition, record outcomes
- UI: Capture flow must show loading → success | error(category, retry button) states; no silent failures
- entry-point treatment: if baseline <8/10 success, add visible "experimental" label or disable the entry (record decision)

Acceptance evidence:

- failure taxonomy is exhaustive (every catch block maps to a category or `unknown`)
- 10-sample report with actual outcomes (≥8 success, or <8 with entry marked/disabled)
- real Chromium: OCR failure shows error message + category + retry button; retry executes a new attempt
- success flow remains unchanged

### PR-15 — WebAuthn challenge table

Risk: HIGH  
Gates: G0, G2 database, G3 security

Implementation slice:

- migration 033 creates `webauthn_challenges` table (UUID PK, purpose CHECK, indexes on `(purpose, session_id/user_id, expires_at)` as query patterns require)
- replace all three dict stores in `passkey_service.py` with database CRUD
- `generate`: insert row with TTL (default 5 minutes, configurable)
- `verify`: SELECT with purpose/binding-key match + not-expired + not-consumed, then UPDATE `consumed_at` atomically
- garbage collection: scheduled or on-demand DELETE of expired rows (implementation choice: cron, startup cleanup, or manual admin endpoint)
- preserve existing ceremony semantics: operator_registration by session_id, user registration/authentication by user_id

Acceptance evidence:

- migration 033 fresh upgrade, 032→033 upgrade, 033→032 downgrade, single-head check
- unit tests: concurrent ceremonies do not overwrite; expired challenge rejected; consumed challenge rejected; cross-purpose challenge rejected
- integration tests: registration, authentication, operator_registration flows all pass with real DB
- negative cases: wrong purpose, wrong session_id, expired, already-consumed all return appropriate errors

### PR-19 — AI governance closure

Risk: MEDIUM (parallel-eligible)  
Gates: G0, G4

Implementation slice:

- document the polish classification decision (transient preview, no forced linkage) in `docs/architecture/` or inline in polish router
- audit current AI call sites that produce canonical learning data: Capture recognition/draft/question generation, any auto-tagging, saved diagrams
- for modification-type calls: verify `target_type`/`target_id` are written at invocation
- for creation-type calls: verify `target_id` is backfilled after user confirmation; document the "abandoned suggestion → NULL `target_id`" contract as valid
- if any call site is missing linkage: add it and test that AiRun rows are created with correct target references

Acceptance evidence:

- polish decision is documented
- spot-check of 3-5 AI call sites proves target linkage or documents why it is transient
- new AiRun rows for Capture recognition have `target_type='Capture'` and `target_id=<capture_uuid>`
- creation-flow test: generate question draft → user confirms → `target_id` backfilled; user abandons → `target_id` remains NULL

### PR-16 — Login throttling

Risk: HIGH  
Gates: G0, G3

Implementation slice:

- add throttling config to `backend/app/config.py`: `LOGIN_THROTTLE_THRESHOLD_WARN`, `LOGIN_THROTTLE_DELAYS`, `LOGIN_THROTTLE_IP_TTL`
- implement dual-dimension tracker (in-memory or Redis; if in-memory, document "restart resets counters" limitation)
- integrate into login router: after failed auth, increment counters; if threshold exceeded, sleep before returning error
- integrate into login router: after successful auth, reset account-level counter
- add unit tests for delay schedule and reset behavior

Acceptance evidence:

- config values are externalizable (not hardcoded in service logic)
- unit test: 3 failures → no delay; 4th failure → 2s delay; 5th → 5s; 6th → 15s
- unit test: successful login resets account counter
- integration test: real login attempts trigger actual delays (measure elapsed time)
- negative case: attacker cannot bypass throttling by changing IP alone (account-level counter persists)

### PR-17 — CI four jobs

Risk: MEDIUM  
Gates: G0

Implementation slice:

- add or update `.github/workflows/ci.yml` (or equivalent CI config) with four jobs per W4-D06
- Job 1 (Frontend): add `npm test` and `npm run test:typecheck` (deferred from Week 1 target)
- Job 2 (Backend): already exists and runs on `.venv`; verify it uses fresh DB and `alembic upgrade head`
- Job 3 (Runtime Smoke): reuse `scripts/runtime-smoke.mjs`; run after `build:cf`; fail on any 404 or API health failure
- Job 4 (Critical E2E): add 5 Playwright tests (E2E-01 through E2E-05, see tasks.md R22b); run with `workers=1`

Acceptance evidence:

- CI config file exists and defines four jobs
- local reproduction of each job passes (or documents expected CI-only environment differences)
- push a test branch; all four jobs run and report status
- intentional failure (e.g., break a test) causes CI to fail

### PR-18 — Legacy cleanup

Risk: MEDIUM  
Gates: G0

Implementation slice:

- for each deletion candidate from W4-D07:
  - run `grep -r <module_name>` across `backend/` and `src/` to prove no references
  - verify its tests are removed or were never written
  - check recent backend logs (if available) or run a targeted runtime search to prove the endpoint/service was unused
- remove files/endpoints/services in dependency order (frontend → endpoint → service)
- run full test suite after each removal to catch any missed references

Acceptance evidence:

- evidence document listing each deleted item with three-part proof (grep + test + runtime)
- `git diff --check` clean
- frontend: `npm test`, `tsc --noEmit`, `test:typecheck` all pass
- backend: `pytest` all pass (or failure count unchanged from Week 3 baseline)

### Week 4 Gate

All PR-14 through PR-18 must individually pass their acceptance criteria. Gate verification matrix:

| Criterion | Evidence |
|---|---|
| OCR baseline | 10-sample report; ≥8 success OR entry marked/disabled |
| WebAuthn challenge | 033 migration replay PASS; unit tests PASS; three ceremonies PASS |
| AI governance | polish classified; spot-check PASS; creation-flow backfill PASS |
| Login throttling | config externalizable; delay schedule tests PASS; integration timing PASS |
| CI four jobs | all four jobs defined; test push triggers all; intentional break caught |
| Legacy cleanup | evidence doc complete; grep/test/runtime three-part proof for each item; full tests PASS |
| No regression | frontend 69 files / 516+ tests PASS; backend 821+ passed / ≤4 failed / ≤9 skipped |
| Migration head | single head at 033; fresh DB upgrade PASS |
| Runtime smoke | `build:cf` → workerd preview → smoke all PASS |

Stop if any PR's independent review finds a BLOCKER, any HIGH-risk PR's verification fails, or any migration cannot replay cleanly.

## 5. Risks and mitigations

| Risk | Mitigation |
|---|---|
| OCR baseline still <80% success | Mark entry as experimental or disable; Week 4 Gate passes with honest disclosure |
| WebAuthn ceremony breakage | Preserve exact call signatures; test all three ceremony types in isolation |
| Throttling degrades UX for legitimate retries | Use graduated delays (no delay until 4th attempt); make thresholds configurable |
| CI Job 3/4 flaky in remote CI | Document flake; retry policy; or accept Job 3/4 as local-only for Week 4, promote to CI in follow-up |
| Legacy cleanup deletes live code | Require three-part evidence (grep + test + runtime); remove in small increments; run full tests after each |

## 6. Not in Week 4 scope

- OCR pipeline rewrite or model replacement
- OCR candidate confirmation UI (PR-22)
- OCR background status tracking (PR-26)
- Authentication UI redesign (PR-20)
- Review undo API/UI (PR-24)
- Daily AI recommendation (PR-25)
- FSRS, vector search, Redis, Elasticsearch
- Database column/table cleanup (only application code cleanup in PR-18)
- Commit, push, merge, deployment, production migration execution
- Week 5+ or any work beyond the 30-day plan

## 7. Authorization boundary

This plan describes the Week 4 scope and execution order. It does **not** authorize:

- Implementation (requires separate user approval before W4-00 execution)
- Production database writes or migration execution
- Commit, stage, push, merge, or release operations
- Deployment to any environment
- Any work outside the PR-14 through PR-18 scope
- Deletion of canonical tables or migrations (only dead application code)

Week 4 Gate PASS proves the code is ready for the 30-day plan closure. Production rollout, if any, requires a separate deployment runbook and authorization.
