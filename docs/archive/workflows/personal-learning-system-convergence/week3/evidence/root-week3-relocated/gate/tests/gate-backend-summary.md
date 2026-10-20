# Week 3 Gate — backend test evidence

agent_id: GATE-seed-verify  date: 2026-09-25

## Targeted suites (all 5 PRs) — clean scratch DB `astra_week3_gate_suite` (alembic 032)

Command (guarded):
```
python3 scripts/week3-scratch-guard.py run --db-name astra_week3_gate_suite -- env PYTHONPATH=. .venv/bin/python -m pytest \
  tests/test_pr09_legacy_mistake_freeze.py tests/test_pr09_migration.py tests/test_pr09_permissions.py tests/test_pr09_routes.py \
  tests/test_pr10_kp_analytics_contract.py tests/test_pr10_kp_analytics_service.py \
  tests/test_pr12_note_knowledge_points_contract.py tests/test_pr12_note_knowledge_points_service.py \
  tests/test_pr13_practice_service.py tests/test_pr13_practice_http.py \
  tests/test_pr11_dashboard_service.py tests/test_pr11_dashboard_http.py -q
```
Result: **147 passed**

## Full backend suite — fresh scratch DB `astra_week3_gate_full` (alembic 032)

Result: **821 passed, 4 failed, 9 skipped, 6 subtests passed**

The 4 failures are all documented test-isolation / environment issues; each passes in isolation on a fresh DB:

| Failure | Nature | Isolation result |
|---|---|---|
| `test_lsr03_guarded_runner.py::test_asyncpg_is_available_and_psycopg2_is_not_a_runtime_fallback` | environment: psycopg2 IS installed in this venv; test asserts it is absent (runtime-fallback guard). Pre-existing (baseline 10F in pr-09 evidence), allowed. | n/a (env) |
| `test_pr09_verify_http.py::test_public_empty_envelope_explicit` | full-suite pollution: earlier `test_pr09_verify_api_contract.py` leaves visibility=public mistakes. Already recorded as pre-existing pollution (pr-09-testfix-7). | PASS alone on fresh DB |
| `test_pr11_dashboard_service.py::test_all_empty_answers_are_honest` | asserts empty scratch DB; earlier tests in the same run seed rows. | PASS alone on fresh DB |
| `test_pr11_dashboard_service.py::test_partial_service_failure_degrades_without_raising` | same empty-DB assumption. | PASS alone on fresh DB |

Also `tests/test_pr09_verify_http.py` + `tests/test_pr09_verify_api_contract.py` together on one fresh DB show cross-file pollution (2 failed) but each file alone passes (27 passed / 24 passed). Not product defects.

Evidence: tests/gate-targeted-pytest.txt, tests/gate-full-pytest.txt, tests/gate-full-pytest-failed.txt,
tests/gate-isolation-pytest.txt, tests/gate-pr09-files-pytest.txt, tests/gate-pr09-file-alone-pytest.txt.