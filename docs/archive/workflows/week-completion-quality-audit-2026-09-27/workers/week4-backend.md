# Week 4 Backend and Database Audit

Date: 2026-09-27

Scope: PR-14 through PR-19, with backend, database, authentication, AI-run linkage, CI/E2E and legacy backend integration emphasis.

Execution: read-only source review; this worker ran no tests and opened no database connection. The main agent supplied fresh isolated PostgreSQL 16, backend-suite, build, smoke and Chromium evidence cited below.

Path convention: repository source paths are relative to the repository root. `evidence/...` refers to `docs/workflows/week-completion-quality-audit-2026-09-27/evidence/...`; `week4/evidence/...` refers to `docs/workflows/personal-learning-system-convergence/week4/evidence/...`.

## Conclusion

Week 4 backend/database work is **PARTIAL**. The current checkout no longer supports three high-impact findings from the 2026-09-26 reassessment: CI now uses an allowed scratch database name, the CLI Passkey server keeps its async engine on one persistent loop, and the two R22b business E2Es now perform real actions and backend readback. Fresh evidence confirms the backend suite, migration to 033, workerd smoke and all five Playwright flows pass.

No current finding is supported at P0. The main P1 candidates for cross-review are: (1) `alembic check` proposes destructive drops because schema lifecycle metadata omits migration-owned objects and the new WebAuthn indexes; (2) login throttling can be raced by concurrent attempts and its IP map has no capacity bound; (3) the AiRun creation-confirmation backfill remains helper-only, while several call sites remain unclassified or unlinked. The OCR success-rate acceptance remains unverified because the ten-sample report is a mocked local harness, not a real provider measurement.

Evidence grades follow the audit prompt: A = fresh runtime/test/migration evidence; B = current implementation source; C = structural presence; D = documentation claim. A grade applies only to the named evidence and not to adjacent untested behavior.

## PR task matrix

| ID | Expected | Actual in current source | Evidence | Status | Risk |
|---|---|---|---|---|---|
| PR-14 OCR diagnostics | Classify OCR failures, show retryable states, and provide a real 10-sample baseline that informs entry-point treatment. | Taxonomy and structured provider categories are present; Capture DTO derives its category from `error_code` rather than storing a duplicate column. Provider response parsing and transport errors are converted to typed categories in `ai_service.py:27-41,160-182,238-267`; capture adapter emits category/code/id only at `capture_recognition.py:27-31,91-112,176-193`. The baseline report explicitly uses a mocked provider and labels real-provider success `NOT_VERIFIED` (`week4/evidence/pr-14-ocr-baseline-report.md:12-26`). `empty_input` maps to `image_fetch`, and unhandled adapter exceptions map to `parse_error`/`invalid_response`, so these edge categories are misleading (`capture_failure_taxonomy.py:26-43`; `capture_recognition.py:145-163`). | B source; A full backend test suite; D report for baseline limits. | `PARTIAL` | P1 for unverified real OCR success/entry decision; P2 taxonomy semantics. |
| PR-15 WebAuthn challenge table | Persist distinct registration/authentication/operator challenges; expire and consume once; preserve ceremony semantics; migrate 032→033 and keep a single head. | Exact client-provided challenge bytes are hashed and matched with purpose/binding and `FOR UPDATE`; consumed state is flushed in the request transaction (`webauthn_challenge_service.py:166-210`, `passkey_service.py:48-80,118-153,258-297`). CLI registration uses one loop per server and disposes engine before loop shutdown (`cli.py:159-229`). Revision 033 adds purpose CHECK, `user_id → users.id ON DELETE CASCADE`, fail-closed live-challenge downgrade, three partial indexes plus a hash lookup index (`033_webauthn_challenges.py:64-161`). Raw challenge storage is a documented, accepted W4-E08 amendment, not hash-only (`week4/evidence/w4-00-decisions.md:91-104`; `models/webauthn_challenge.py:19-30`). | A fresh PG16 upgrade and full suite: `evidence/migration-upgrade.txt`, `evidence/backend-test.txt`; B source; offline `alembic heads/history` run by this worker returned one head, 033. | `COMPLETE_WITH_DEBT` | P1 schema metadata drift below; no reproduced challenge lifecycle failure in this pass. |
| PR-16 Login throttling | Configurable dual account/IP delay schedule, success reset, no permanent lockout, bounded state. | Settings, account key hashing and 10,000-account LRU cap exist (`config.py:61-66`; `login_throttle.py:26-41,91-119,138-199`). Delay is checked before the password query and failures are only recorded after a failed query (`routers/auth.py:184-211`). There is no in-flight reservation, so concurrent guesses can all read the same pre-failure count and avoid the next delay. `_ips` is a plain dict swept by TTL only; a high-cardinality burst within the TTL can grow without a configured ceiling (`login_throttle.py:91-93,170-199`). The current module doc says the IP map is bounded by TTL, which does not bound its peak cardinality inside that window. | B source; A full backend suite `evidence/backend-test.txt`; concurrency/cardinality are not covered by that pass. | `PARTIAL` | P1 abuse-control and memory-growth gap. |
| PR-17 CI and critical E2E | Four CI jobs; five Playwright flows including wrong answer→mistake draft and re-answer→ReviewRecord, with deterministic seed and persisted-state assertions. | Workflow has frontend, backend, runtime smoke and E2E jobs; each database service and URL now use `astra_week4_ci` (`.github/workflows/ci.yml:13-109,112-206,208-329`). E2E-03 submits a real wrong answer and reads back its attempt-linked pending draft (`tests/e2e/03-capture.spec.ts:15-74`); E2E-04 performs re-answer/rating and reads back the ReviewRecord with the same attempt (`04-review-flow.spec.ts:23-86`). Global setup seeds a guarded scratch DB (`global-setup.ts:21-79`; `seed_week4_business.py:200-243`). | A backend suite, workerd smoke and Chromium 5/5: `evidence/backend-test.txt`, `runtime-smoke.txt`, `e2e.txt`; B current workflow/specs. Remote GitHub Actions execution not evidenced here. | `COMPLETE_WITH_DEBT` | P2: remote CI status remains `NOT_VERIFIED`; source configuration is internally aligned with guards. |
| PR-18 Legacy cleanup | Delete only proven-safe application surfaces; provide static, test and runtime/no-surface evidence; preserve active compatibility routes and migrations. | Four unreferenced UI/component files plus one dead import were removed; current evidence records per-item scans and before/after frontend/type checks (`week4/evidence/pr-18-cleanup-components.md:10-25`; `pr-18-summary.md:13-23,49-58`). `sm2.py` and the legacy review chain remain because they are still imported/reachable; summary documents why they were not safe leaves (`pr-18-summary.md:60-83`). | B current tree/status; A frontend/build evidence; D detailed cleanup evidence. | `VERIFIED_COMPLETE` for the approved safe-to-delete set | P2 remaining legacy compatibility maintenance; no basis to remove it in PR-18. |
| PR-19 AI governance | Document transient vs persisted calls, link modification calls, and wire creation confirmation to AiRun target backfill. | Capture recognition and Capture draft pass `target_type="Capture"` plus capture id (`capture_recognition.py:91-96`; `capture_ai_draft.py:97-103`). Polish is an authenticated transient stream and bypasses the gateway (`routers/ai_polish.py:17-45`). `backfill_ai_run_target` exists and flushes an update, but explicitly has no production caller (`ai_run_service.py:178-203`; only definition and tests found by source search). The question-draft confirm endpoint only echoes the submitted draft and creates no entity; it has no DB dependency or run id (`routers/ai.py:487-497`). The current audit lists 15 other unlinked gateway call sites, including staged mistake generation and other AI endpoints (`week4/evidence/pr-19-ai-call-audit.md:29-52`); source confirms representative staged calls omit targets (`mistake_staged_service.py:13-40,71-108,111-145`). Their final transient/persisted classification is not yet enforced end-to-end. | B source; A backend suite; D governance/audit docs. | `PARTIAL` (`SURFACE_COMPLETE` for helper-only backfill) | P1 canonical provenance gap; no evidence that every unlinked row represents a persistent canonical entity, so classify the remaining sites before expanding scope. |

## Cross-cutting backend and database findings

### P1 — Alembic metadata drift can generate destructive operations

Fresh isolated `alembic check` failed with exit 255 and proposed removing six migration-owned `legacy_note_migration_*` / `legacy_migration_*` tables, six `draft_items` columns, and all four PR-15 WebAuthn indexes (`evidence/alembic-check.txt:1-31`). This is **schema metadata drift, not a failed upgrade or observed data loss**: fresh PG16 upgrade through 033 succeeded (`evidence/migration-upgrade.txt:18-37`).

The registry documents and excludes only guest tables (`backend/app/models/registry.py:79-94`; `alembic/env.py:22-31`). It does not register or exclude the migration-only 026 ledger tables. Revision 026 adds `source_hash`, approval fields, conversion sequence and target IDs to `draft_items` (`backend/alembic/versions/026_legacy_system_retirement.py:1028-1047`), while `DraftItem` has no mapped counterparts (`backend/app/models/question.py:31-83`). Revision 033 adds four indexes (`033_webauthn_challenges.py:104-134`), while the ORM model defines no matching indexes or CHECK constraint (`models/webauthn_challenge.py:11-38`). CI currently upgrades and tests but has no schema-drift gate (`.github/workflows/ci.yml:97-109`).

Impact: a future unreviewed autogenerate migration could delete durable workflow ledger data, compatibility columns or lookup indexes. Do not interpret the failure as an upgrade failure; treat it as a G2 blocker for accepting autogenerated schema diffs until the migration-only ownership is represented explicitly and the check is clean or narrowly allowlisted.

### P1 — Login throttling has a concurrent bypass and an unbounded peak map

`get_required_delay()` only reads counters under a lock; the lock is released before login performs the DB query and only then calls `record_failure()` (`login_throttle.py:221-242`; `routers/auth.py:184-211`). A parallel burst can therefore start many guesses against the same prior count before any failure increments it. Separately, account entries are capped but IP entries are not; TTL removes expired values, but does not cap distinct IPs received during one TTL interval (`login_throttle.py:91-93,170-199`). In-memory per-process state and multi-worker inconsistency are documented design limitations (`login_throttle.py:8-25`), but these two concrete bypass/capacity properties are not covered by that disclaimer.

### P1 — AiRun backfill remains a helper without a user confirmation boundary

The helper is implemented and unit-tested, but no production handler invokes it (`ai_run_service.py:178-203`; `docs/architecture/ai-governance.md:48-51,96-98`). The current question-draft confirm route is an echo response, so the plan's confirmation→canonical entity→AiRun link path is absent (`routers/ai.py:487-497`). Capture linkage is working; do not report all PR-19 linkage as missing. The remaining caller inventory needs a decision for each site: target an existing canonical entity, carry a run id through an actual creation flow, or explicitly classify a truly transient suggestion. `AiRun.target_id` is polymorphic text without a database FK (`models/ai_run.py:19-21`), so the service contract must provide the integrity check.

### P2 — OCR error categories still merge non-equivalent cases

`empty_input` means no bytes were supplied but is serialized as `image_fetch`; generic programming/adapter exceptions are returned as `parse_error`, which serializes as `invalid_response` (`capture_failure_taxonomy.py:26-43`; `capture_recognition.py:145-163`). The `image_format` enum has no current producer (`capture_failure_taxonomy.py:6-7`). These distort diagnosis but do not undo the typed provider timeout/auth/response handling now present in `ai_service.py:160-182,238-267`.

### P2 — Provider error sanitization improved, but gateway still persists generic exception text

Provider HTTP errors now omit response bodies and carry stable categories (`ai_service.py:27-41,160-182,238-267`), resolving the prior raw-provider-response path. However, `ai_gateway._build_failure_result()` stores `str(exc)[:500]`, and `_finish_run_record()` writes it into `AiRun.error_message_safe` (`ai_gateway.py:204-220,157-165`). The provider exception class is safe by construction, but unexpected non-provider exceptions can bypass that class. This is a source-level sanitization risk, not a reproduced secret leak; keep severity P2 unless a concrete exception source is shown to contain sensitive material.

## Eight-dimension Week 4 view (backend/database evidence only)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| Architecture | `PARTIAL` | Auth storage and AI gateway have clear service boundaries, but migration-only schema ownership and AiRun-to-entity confirmation flow are unresolved. |
| Frontend | `NOT_ASSESSED_HERE` | E2E business paths are verified in the main-agent evidence; visual/interaction quality belongs to the frontend reviewer. |
| Backend | `PARTIAL` | Core backend suite passes; login abuse controls and AI provenance still have implementation gaps. |
| Database | `PARTIAL` | Linear 033 head and fresh upgrade pass; schema metadata check fails with destructive candidate operations. |
| API | `PARTIAL` | CI and E2E contracts align locally; the question-draft confirm API does not persist or correlate the entity/run. |
| UX | `NOT_ASSESSED_HERE` | OCR retry and category UI are outside this backend-only review. |
| Testing | `COMPLETE_WITH_DEBT` | Fresh suite 922 passed, 9 skipped, 47 subtests; smoke 23/23 and Chromium 5/5. Real-provider OCR and remote Actions are unverified; `alembic check` fails. |
| Maintainability | `PARTIAL` | PR-18 safely removed dead surfaces; missing schema-lifecycle metadata and duplicate legacy routes remain costly to reason about. |

Backend/database-only completion estimate: **65–80%, Medium confidence**. This is not a whole-Week score. The estimate credits fresh migration, full backend suite and business E2E evidence, while discounting incomplete OCR measurement, throttling gaps, schema drift and missing AiRun backfill. Whole-Week range should be set by the primary auditor after frontend/product evidence is reconciled.

## Future work candidates

| Class | Candidate | Why / next evidence |
|---|---|---|
| A — Planned but unfinished | Wire AiRun backfill through the real confirmation/save endpoint, carrying an opaque `run_id`; verify persisted entity linkage and abandonment behavior. | Already required in PR-19; current helper-only test does not prove the production flow. |
| A — Planned but unfinished | Run the controlled ten-image OCR baseline against the authorized provider and record actual outcomes before changing the entry-point label. | The current 1/10 report is explicitly mock-only. A provider run needs separate authorization. |
| B — Planned but insufficient | Make schema ownership explicit for revision-026 ledger objects and columns and revision-033 checks/indexes; add a guard-safe `alembic check` to isolated CI. | Current check exit 255 identifies the exact destructive autogen candidates; no migration execution is implied. |
| B — Planned but insufficient | Make throttling admission atomic under concurrent login attempts and cap IP cardinality; retain a shared store as a separate decision if deployment grows beyond one process. | Current read-then-record flow races, and TTL alone does not cap peak dictionary size. |
| B — Planned but insufficient | Classify every gateway call as existing-target, creation/backfill, or transient and prevent audit persistence failures from silently producing unaudited canonical output. | Current 15-row inventory is not a substitute for endpoint-to-entity verification; `_start_run_record` currently returns `None` after a persistence error and the AI call continues (`ai_gateway.py:122-141`). |
| C — Newly recommended | Add a maintained “schema authority map” for ORM-owned, migration-only, and intentionally excluded objects. | Revision 026 demonstrates durable SQL-owned ledgers can be invisible to ORM metadata; an explicit ownership map would make future drift reviews safer. |

## Evidence and verification ledger

- `alembic heads/history` executed by this worker without a database connection: one head `033`, sequential `032→033`.
- Main-agent fresh backend result: `922 passed, 9 skipped, 47 subtests passed` in `evidence/backend-test.txt:69-70`.
- Main-agent fresh PG16 migration reached `032→033`: `evidence/migration-upgrade.txt:30-37`.
- Main-agent current E2E: five Chromium flows passed, including E2E-03/04 business readback: `evidence/e2e.txt:1-11`.
- Main-agent workerd smoke: 20/20 referenced assets and 23/23 checks passed: `evidence/runtime-smoke.txt:1-2`.
- Main-agent `alembic check`: exit 255 with the migration-only table/column and PR-15 index differences: `evidence/alembic-check.txt:1-31`.
- No remote GitHub Actions run, real-provider OCR, production DB inspection, or live-schema write was performed by this worker.
