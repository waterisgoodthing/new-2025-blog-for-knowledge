# Testing and Engineering Quality Review

Date: 2026-09-27

Scope: Independent review of current test evidence, test assertions and skip gates, CI/build configuration, dependency reproducibility, and engineering hygiene for the Week-completion audit. This worker did not run tests, modify product code, or connect to a database. Runtime and database probe results below are from the main agent's evidence bundle.

## Conclusion

**Week acceptance assurance: FAIL.** The recorded suites and builds mostly pass, but fresh behavior probes found three important paths that the automated tests do not cover: selecting multiple answers in practice, carrying knowledge-point links through the mistake/review lifecycle, and routing writes to legacy mistakes through a generic AI suggestion endpoint. Those are acceptance-coverage failures, not evidence that the full suites failed.

**Local command evidence: PARTIAL.** The backend, frontend, type checks, builds, runtime smoke, migration replay, and five browser specs match their recorded pass counts. `alembic check` fails on schema metadata drift, and two backend warnings show incorrectly typed async mocks. Remote GitHub Actions status and production readiness are not established by local runs.

## Evidence reconciliation

| Check | Current evidence | Assessment |
|---|---|---|
| Backend | `922 passed, 9 skipped, 2 warnings, 47 subtests passed` in [`backend-test.txt`](../evidence/backend-test.txt). | Summary is accurate. The two warnings are from `test_log_write_failure_does_not_block` and `test_write_call_log_catches_exception`: `AsyncMock` is assigned to `session.add`, which is synchronous in SQLAlchemy, so its returned coroutine is never awaited. The mock does not model an `add()` failure; the tests separately exercise a failing async `commit()`. Treat as mock-quality debt, not as a passing check of every log-write failure mode. |
| Frontend | 70 Vitest files / 522 tests passed in [`frontend-test.txt`](../evidence/frontend-test.txt), and a separate Node 24 run also passed 70 files / 522 tests in [`frontend-test-node24.txt`](../evidence/frontend-test-node24.txt). | Both summaries are accurate. These are unit/component tests, not proof of all browser or persisted-data behavior. |
| Browser E2E | Five Chromium specs passed in [`e2e.txt`](../evidence/e2e.txt). E2E-03 submits a wrong answer and reads back its pending attempt-linked draft; E2E-04 re-answers and reads back the associated `ReviewRecord`. | Current evidence supersedes older reports that said these two flows were missing. These are real page actions plus API/DB readback, but use short-answer fixtures and do not cover the gaps below. |
| Runtime/build | `20/20` referenced assets and `23/23` checks passed in [`runtime-smoke.txt`](../evidence/runtime-smoke.txt); both Next and OpenNext builds exited zero. | Local build/runtime evidence only; it is not remote CI or deployed-runtime evidence. |
| Migrations | Fresh PostgreSQL 16 upgrade through 033 and empty-database 033→027→033 replay passed. The non-empty downgrade refused to remove two live WebAuthn challenges in [`migration-downgrade.txt`](../evidence/migration-downgrade.txt). | The refusal is the intended fail-closed behavior, not a failed acceptance check. It does not prove downgrade with arbitrary populated data is reversible. |
| Schema drift | [`alembic-check.txt`](../evidence/alembic-check.txt) exits 255 and proposes drops for migration-owned legacy ledger tables, `draft_items` columns, and WebAuthn indexes. | Real engineering failure despite successful upgrade. Do not accept generated drop operations until ORM/migration ownership is reconciled and the check is made clean or narrowly governed. |

### The nine skips

The full-suite log records only dots and an aggregate skip count. The supplementary [`skipped-tests.txt`](../evidence/skipped-tests.txt) run records all nine node IDs and reasons directly; it reports 35 passed, 9 skipped, and 6 subtests. The reasons also match the gates in source:

| Count | Tests skipped | Gate and reason |
|---:|---|---|
| 3 | `ReviewSchemaV2MigrationDynamicTest` in `backend/tests/test_review_schema_v2.py`: `test_migration_replay_and_state_normalization`, `test_new_rows_default_to_v2_algorithm_after_028`, `test_forbidden_states_rejected_at_database_level`. | `@skipUnless(_is_scratch_database())`; `_is_scratch_database()` accepts only `astra_week2_*` or `opencode_week2_*`. The audit used Week 4 scratch databases, so these Week 2 migration replay cases were not run. |
| 2 | `test_synthetic_negative_fixture_matrix_isolated_only` and `test_external_archive_manifest_replay_isolated_only` in `backend/tests/test_lsr03_fixture_rehearsal.py`. | Both require the separate `LSR03_DATABASE_URL` isolated fixture/archive database. The validation evidence lists only the Week 4 scratch cluster; it does not show an LSR03 fixture database. |
| 4 | All four tests in `backend/tests/test_legacy_note_migration_contract.py`: retained-negative fixtures, mirror-negative fixtures, frozen-contract surface, and immutable ledger/marker. | Each requires `LSR03_DATABASE_URL` and, depending on the case, an approved pending or migrated baseline. Those test cases were not exercised by the Week 4 scratch migration. |

These skips are opt-in historical migration/fixture tests, not random flakiness. The first group is specifically incompatible with the Week 4 scratch name; the latter six need a separate LSR03 baseline. CI currently uses `astra_week4_ci`, so these same version-/fixture-gated cases should remain skipped there unless that dedicated evidence environment is added. Preserve the per-test skip artifact so these cases are not mistaken for executed coverage.

## Acceptance coverage gaps found by fresh probes

1. **Multiple-choice review re-answer is not covered by the passing E2E path.** Both seeded business questions are `short_answer` (`tests/e2e/seed/seed_week4_business.py`), and both R22b browser tests submit free-text answers. The main-agent browser probe is on `/manage/review`: after clicking A and C in a ReviewQueue re-answer, only C remained `aria-pressed=true`; the review-attempt endpoint returned HTTP 201 with `submitted_answer="C"` and `is_correct=false` (`evidence/probe-multiple-choice.cjs`, `probe-multiple-choice.txt`). Separately, the service probe in `evidence/probe_learning.py` showed an evaluator mismatch for the same `A C` answer: practice `_is_correct` returned false while the review evaluator returned correct. The browser reproduction is a ReviewQueue re-answer UI defect; the practice/review normalization difference is a separate backend behavior gap. Short-answer E2E and an isolated review-evaluator unit test did not cover either cross-layer case.

2. **The knowledge-point chain is tested in pieces, not as a learning lifecycle.** PR-10/PR-11 tests exercise analytics and dashboard calculations; PR-12 tests exercise the separate Note↔KnowledgePoint relation. None asserts propagation from a `QuestionKnowledgePoint` through a wrong `Attempt`, `MistakeDraft`, converted `Mistake`, and resulting `ReviewItem`. The main-agent transaction-scoped probe showed the source question had a KP while the draft and mistake had empty KP lists, and the linked KP metrics were unchanged after the attempt/review path (`evidence/probe_learning.py`, `probe-learning.txt`). Existing component/service passes could not detect this because they assert the isolated contracts, not the relational chain.

3. **The legacy freeze negative matrix does not cover indirect write entry points.** The PR-09 freeze tests cover the enumerated `/api/notes` and legacy review operations, and frontend tests disable the legacy mistake forms. The route inventory in `test_pr09_verify_api_contract.py` does not include the generic `/api/ai/suggestions/execute` organization action. The main-agent probe exercised that real handler/service with a legacy `Note(type="mistake")`; it returned 200 and changed the row's folder (`evidence/probe_freeze.py`, `probe-freeze.txt`). PR-09 specifies all legacy-mistake writes as frozen, so this is an uncovered route/contract path. The test suite checked known F-1..F-9 surfaces, not all write-capable operations over legacy mistake rows.

These probes are diagnostic evidence from isolated transactions/scratch data. They were not added as CI regression tests by this worker, and the observation scripts do not themselves fail the build on mismatch.

## CI and engineering hygiene

- `.github/workflows/ci.yml` now uses `astra_week4_ci` for its PostgreSQL service, which satisfies the current scratch-name guards. It defines frontend, backend, runtime-smoke, and Playwright jobs; the current five browser specs align with local E2E evidence. This verifies configuration by inspection, not a remote Actions run.
- CI uses Node 24 and Python 3.12; `package.json` declares Node `24.x`, and the backend requirements file contains fixed versions for core libraries. The first recorded frontend Vitest run used Node 26, outside the declared engine range; the supplementary Node 24 run then passed all 522 tests, closing that runtime-version evidence gap.
- `package-lock.json` supports reproducible `npm ci`. Python dependencies are installed from `backend/requirements.txt`, but `bcrypt`, `webauthn`, and `pytest` use open-ended lower bounds and there is no Python lock/hash file. CI can resolve newer versions over time.
- No frontend lint script or Python lint/type-check is configured. The workflow itself notes that Ruff/mypy are absent from dependencies and project configuration. Report lint as **NOT_CONFIGURED**, not as passed. Frontend shipped-source and test-tree TypeScript checks did pass.
- Local test artifacts do not establish GitHub Actions health, deployment, a production environment, or provider-backed OCR behavior. The working tree is dirty and there is no tested commit identity in this evidence set.

## Recommended engineering gates

- Add a ReviewQueue multiple-choice re-answer Playwright/API regression: select two answers, verify both remain selected, submit the normalized answer set, and assert the persisted attempt. Separately, align or explicitly specify practice and review answer normalization and test both evaluators against the same answer-set cases.
- Add a transactional backend integration test for Question→Attempt→MistakeDraft→Mistake→ReviewItem KP propagation and expected KPI updates; assert the links and metrics from persisted readback.
- Extend the legacy freeze route inventory to every write-capable endpoint that can mutate `Note(type="mistake")`, including generic suggestion/organization actions. Assert frozen rejection or document a precise allowed-field exception in the contract.
- Reconcile migration-only schema ownership for the objects reported by `alembic check` before accepting autogenerate output; add a guarded schema-drift check to isolated CI only after ownership is explicit.
- Preserve skipped node IDs/reasons in the test artifact. Keep the Week 2 and LSR03 fixtures opt-in and run them only against their explicitly isolated baselines.

## Evidence boundary

Evidence reviewed: `validation.md`; the raw backend, frontend, E2E, build, runtime-smoke, migration, and probe logs under `evidence/`; current CI/package/requirements configuration; source assertions and skip decorators; QA/SDET and DevOps/SRE profiles. This review did not rerun the full suite or connect to any database. Remote CI, a clean commit, production state, and real-provider OCR remain **NOT_VERIFIED**.
