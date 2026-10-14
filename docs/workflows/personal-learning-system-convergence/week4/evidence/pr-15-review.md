# PR-15 Independent Review — WebAuthn Challenge Persistence (migration 033)

Reviewer: independent (read-only; did not implement PR-15)
Date: 2026-09-26
Scope: migration 033, `webauthn_challenge_service`, `passkey_service`, `auth.py`, `cli.py`, registry, tests, evidence.
Scratch DB: `astra_week4_pr15` (via `scripts/week4-scratch-guard.py`; no DB create/drop; no `blog_db`/`blog_v2`).

## Verdict

**FAIL**

The challenge lifecycle itself is correct and all 12 PR-15 tests pass against the real 033 scratch DB, but the mandatory startup/revision contract was **not** reconciled: `backend/main.py` still pins `EXPECTED_ALEMBIC_REVISION = "032"` while the single Alembic head is `033`. Any application startup (lifespan) or direct readiness check against a 033 database raises `RuntimeError` and fails the app. This is a release BLOCKER.

## Counts by severity

| Severity | Count |
| --- | --- |
| BLOCKER | 1 |
| HIGH | 1 |
| MEDIUM | 1 |
| LOW | 2 |
| INFO | 1 |

## Findings

| id | severity | problem | evidence file:line | required action |
| --- | --- | --- | --- | --- |
| F1 | BLOCKER | Startup Alembic pin is stale at `032` while the only head is `033`; lifespan startup and `validate_database_readiness()` fail against a 033 database. Startup tests and any lifespan-based HTTP test fail. | `backend/main.py:17` (`EXPECTED_ALEMBIC_REVISION = "032"`); raise at `backend/main.py:31-35`, called from `backend/main.py:70`; reproduced below and in `/tmp/pr15_readiness.txt` / `tests/test_auth_error_handling.py:36` | Change `EXPECTED_ALEMBIC_REVISION` to `"033"` **and** update every pin assertion in lockstep: `backend/tests/test_security_settings_guards.py:68`, `backend/tests/test_pr12_note_knowledge_points_contract.py:182`, `backend/tests/test_pr09_migration.py:76`. Re-run lifespan tests after the bump. |
| F2 | HIGH | Raw challenge plaintext is persisted in a new `challenge` column, contradicting the LOCKED design (hash-only) and PR-15's own acceptance criteria ("No challenge plaintext in … database"). `challenge_hash` is written but never used for lookup/verification, so the design's hash-bound verify protocol is not implemented as specified. | Column: `backend/alembic/versions/033_webauthn_challenges.py:80`; model `backend/app/models/webauthn_challenge.py:19`; write `backend/app/services/webauthn_challenge_service.py:36`; read `backend/app/services/passkey_service.py:95,170,226`. Design: `docs/.../design.md:240` ("不存明文 challenge"), `:258` (verify by `challenge_hash`); acceptance `docs/.../week4/tasks/pr-15.md:223,249`. Schema proof: `pr-15-schema-dump.sql` includes `challenge | character varying(128)`. | Either (a) redesign to hash-only (hash the client challenge, query by `challenge_hash`, drop the raw column), or (b) obtain an explicit design amendment/waiver that updates `design.md` D14 and the acceptance criteria and documents why raw challenge storage is required for `webauthn` verification. Update F2 acceptance checkboxes to match the approved decision. |
| F3 | MEDIUM | Lazy cleanup of expired challenges required by the design is not wired into any production path: `cleanup_expired_challenges` is only called by tests (no auth-path call, no admin endpoint). Expired rows accumulate until manual cleanup. | Service `backend/app/services/webauthn_challenge_service.py:87`; only caller `backend/tests/test_webauthn_challenge_lifecycle.py:179`. Requirement: `docs/.../design.md:261`; task `docs/.../week4/tasks/pr-15.md:168,215`. | Invoke lazy cleanup on the verify path, or add the sanctioned admin endpoint, or record an explicit waiver. |
| F4 | LOW | Challenge TTL is hardcoded (`DEFAULT_TTL_SECONDS = 300`) rather than configurable as the design states. | `backend/app/services/webauthn_challenge_service.py:10`; design `docs/.../design.md:245` ("2–5 min，配置化"). | Move TTL into `backend/app/config.py` (or document the fixed 300s as accepted). |
| F5 | LOW | Locked docs disagree on the same schema (design vs task spec): `design.md` says `purpose VARCHAR(30)`, `session_id VARCHAR(64)`; `pr-15.md` says `VARCHAR(32)` / `VARCHAR(255)`. Implementation follows `pr-15.md`. | `docs/.../design.md:241-242`; `docs/.../week4/tasks/pr-15.md:32-33`. | Reconcile `design.md` D14 to the implemented/`pr-15.md` types (documentation only). |
| F6 | INFO | FK adds `ON DELETE CASCADE`, which `pr-15.md` left unspecified; consistent with the design's "appropriate ON DELETE behavior" and acceptable. | `backend/alembic/versions/033_webauthn_challenges.py:93-98`. | None (confirm CASCADE is the intended policy). |

## Verification that PASSED (against current source, 033 scratch DB)

- **Migration 033 head/chain**: `revision = "033"`, `down_revision = "032"`; 032's `down_revision = "031"` intact; `alembic heads` returns a single `033 (head)`; `alembic_version` holds exactly one row = `033`.
- **Schema vs `pr-15.md`**: columns, `purpose` CHECK (3 values), `users.id` FK, and the 4 indexes `(purpose,session_id)`, `(purpose,user_id)`, `(expires_at) WHERE consumed_at IS NULL`, `(challenge_hash)` all match the task spec. The only structural deviation is the extra raw `challenge` column (F2).
- **Upgrade defensive**: advisory xact lock `330033`, `users` prerequisite check, refuses if table already exists (`033_...py:65-70`).
- **Downgrade fail-closed**: refuses while any live (`consumed_at IS NULL AND expires_at > now()`) row exists; verified in `pr-15-migration-replay.log` steps [9]–[12] (refused with 2 live rows, then succeeded after deletion, then re-upgraded to 033).
- **Security cases** (`test_webauthn_challenge_lifecycle.py` + `test_passkey_ceremonies.py` = 12 passed): expired rejected; consumed not reusable; cross-purpose rejected; operator `session_id` mismatch rejected; user binding mismatch rejected; concurrent ceremonies store independent rows; cleanup removes expired only. Every ceremony test asserts `with_for_update`-based consume via the real table.
- **`with_for_update`**: present by default in `get_valid_challenge` (`webauthn_challenge_service.py:75-76`).
- **Semantics preserved vs original dicts**: registration and authentication consume **only on SUCCESS** (`passkey_service.py:104,238`); operator registration consumes **BEFORE verification** (`passkey_service.py:171`) matching the original `pop` semantics. No behavior drift found.
- **No dict remnants**: grep for `_reg_challenge_store|_auth_challenge_store|_operator_reg_challenge_store` matches only the migration docstring (`033_webauthn_challenges.py:4-5`).
- **Call sites**: all 6 ceremony functions are `async` and every caller awaits and passes `db` (`auth.py:241,301,341,356`; `cli.py:182,207` via `_run_on_db` which awaits `coro_factory(session)`). No missed caller, no sync/async mistake; no frontend caller of the Python functions.
- **Raw challenge not logged**: no logger/print emits the raw challenge or `expected_challenge`; warnings log only "no challenge stored" and an 8-char `session_id` prefix.

## Raw command outputs

All commands were wrapped by the scratch guard; target = `astra_week4_pr15` (no DB create/drop).

### 1. `alembic heads` (guard)

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/alembic heads"
033 (head)
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/alembic heads']
```

Supporting DB revision probe (read-only):

```
$ psql -U limengyang -d astra_week4_pr15 -tAc "SELECT count(*) FROM alembic_version"
1
$ psql -U limengyang -d astra_week4_pr15 -tAc "SELECT version_num FROM alembic_version"
033
$ psql -U limengyang -d astra_week4_pr15 -tAc "SELECT to_regclass('public.webauthn_challenges')"
webauthn_challenges
```

### 2. PR-15 lifecycle + ceremony tests (guard)

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_webauthn_challenge_lifecycle.py tests/test_passkey_ceremonies.py -q"
............                                                             [100%]
12 passed in 2.96s
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest tests/test_webauthn_challenge_lifecycle.py tests/test_passkey_ceremonies.py -q']
```

### 3. Reported startup-pin command (guard) — NOTE: these two files PASS as-is

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_security_settings_guards.py tests/test_manage_write_permissions.py -q"
.........................                                                [100%]
25 passed in 0.38s
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest tests/test_security_settings_guards.py tests/test_manage_write_permissions.py -q']
```

Root cause of the pass: `test_security_settings_guards.py:68` statically asserts `main.EXPECTED_ALEMBIC_REVISION == "032"`, i.e. it currently enshrines the same stale pin as `main.py:17`, and `test_manage_write_permissions.py` constructs `TestClient(main.app)` **without** a `with` block, so the lifespan (and therefore the readiness check) never runs. The failure is real but is exposed by lifespan/readiness tests, reproduced below.

### 4. BLOCKER F1 reproduction A — direct readiness check (guard)

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/python -c 'import asyncio, main; print(\"PIN=\", main.EXPECTED_ALEMBIC_REVISION); asyncio.run(main.validate_database_readiness()); print(\"READINESS_OK\")'"
PIN= 032
Traceback (most recent call last):
  ...
  File "/Users/limengyang/2025-blog-public/backend/main.py", line 32, in validate_database_readiness
    raise RuntimeError(
RuntimeError: Database schema is not at the expected Alembic revision 032; found ['033'].
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing [...]
```

### 5. BLOCKER F1 reproduction B — a lifespan-based test (guard)

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_auth_error_handling.py -q"
.F                                                                       [100%]
=================================== FAILURES ===================================
_______________ test_disabled_account_password_login_returns_401 _______________

        try:
>           with TestClient(main.app) as client:
                ^^^^^^^^^^^^^^^^^^^^
...
main.py:70: in lifespan
    await validate_database_readiness()
...
E           RuntimeError: Database schema is not at the expected Alembic revision 032; found ['033'].

main.py:32: RuntimeError
=========================== short test summary info ============================
FAILED tests/test_auth_error_handling.py::test_disabled_account_password_login_returns_401
1 failed, 1 passed in 0.56s
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest tests/test_auth_error_handling.py -q']
```

The same lifespan failure affects every `with TestClient(main.app)` / `main.lifespan(...)` test, including (non-exhaustive): `test_pr11_dashboard_http.py:69`, `test_pr09_verify_api_contract.py:54`, `test_pr12_note_knowledge_points_http.py:84`, `test_pr12_verify_concurrency.py:57`, `test_pr09_permissions.py:40,48,59,68`, `test_pr10_verify_contract.py:75`, `test_admin_profile_routes.py:101,115,123,164`, `test_pr13_practice_http.py:52`, `test_pr09_verify_http.py:52`, `test_dashboard_dependency_lifecycle.py:74`, `test_anon_capture_access.py:27,48`.

### 6. Schema dump (existing PR-15 evidence, unchanged)

```
                          Table "public.webauthn_challenges"
     Column     |           Type           | Nullable |      Default
----------------+--------------------------+----------+-------------------
 id             | uuid                     | not null | gen_random_uuid()
 challenge      | character varying(128)   | not null |
 challenge_hash | character varying(64)    | not null |
 purpose        | character varying(32)    | not null |
 session_id     | character varying(255)   |          |
 user_id        | uuid                     |          |
 created_at     | timestamp with time zone | not null | now()
 expires_at     | timestamp with time zone | not null |
 consumed_at    | timestamp with time zone |          |
Indexes:
    "webauthn_challenges_pkey" PRIMARY KEY, btree (id)
    "idx_webauthn_challenges_challenge_hash" btree (challenge_hash)
    "idx_webauthn_challenges_expires" btree (expires_at) WHERE consumed_at IS NULL
    "idx_webauthn_challenges_purpose_session" btree (purpose, session_id) WHERE session_id IS NOT NULL
    "idx_webauthn_challenges_purpose_user" btree (purpose, user_id) WHERE user_id IS NOT NULL
Check constraints:
    "ck_webauthn_challenges_purpose" CHECK (purpose IN ('registration','authentication','operator_registration'))
Foreign-key constraints:
    "fk_webauthn_challenges_user_id" FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
```

## Exact required follow-up for the startup pin (F1)

1. `backend/main.py:17`: change `EXPECTED_ALEMBIC_REVISION = "032"` → `"033"`.
2. Update the three static pin assertions to `"033"` in the same change so the contract is self-consistent:
   - `backend/tests/test_security_settings_guards.py:68`
   - `backend/tests/test_pr12_note_knowledge_points_contract.py:182`
   - `backend/tests/test_pr09_migration.py:76`
3. Re-run, under the guard against `astra_week4_pr15`:
   - `tests/test_security_settings_guards.py tests/test_manage_write_permissions.py -q`
   - any lifespan test, e.g. `tests/test_auth_error_handling.py -q`
   - plus a representative `with TestClient(main.app)` test set.
   All must pass with a `033` database.
4. This is an in-scope contract reconciliation for PR-15 and must land before PR-15 can be accepted. It does not authorize commit, push, migration, or deployment.

## Not performed (read-only boundary)

- Did not modify any source file; created only this evidence file.
- Did not run `alembic upgrade/downgrade` (schema mutation avoided; downgrade fail-closed was confirmed from the existing `pr-15-migration-replay.log` and by reading `downgrade()`).
- Did not create/drop databases; did not touch `blog_db`/`blog_v2`.
- Did not run the full test suite; only the PR-15 and named guard tests plus targeted reproduction.

---

# §recheck (2026-09-26) — post-fix re-verification

Original reviewer re-checked the implemented fixes against current source (read-only; no source modified; only this evidence file appended). Scratch DB `astra_week4_pr15`, single head `033`.

## Recheck verdict

**PASS**

All findings raised in the first review are CLOSED. F1 (the release BLOCKER) is fixed and independently reproduced as fixed: the lifespan now starts and `validate_database_readiness()` succeeds against the 033 database, and every expected-head pin asserts 033, while the 032 migration-shape assertion is correctly retained.

## Per-finding status

| id | severity | status | evidence |
| --- | --- | --- | --- |
| F1 | BLOCKER | **CLOSED** | `backend/main.py:17` = `"033"`; `backend/tests/test_security_settings_guards.py:68` = `"033"`; `backend/tests/test_pr09_migration.py:76` = `"033"`; `backend/tests/test_pr12_note_knowledge_points_contract.py:181-182` (`test_pinned_revision_matches_current_head` = `"033"`). The 032 migration-shape assertion is intentionally retained at `test_pr12_note_knowledge_points_contract.py:60` (`re.search(r'revision:\s*str\s*=\s*"032"', source)`). Runtime proof: lifespan tests `test_auth_error_handling.py` and `test_optional_session_state.py` (both `with TestClient(main.app)`) now pass, and `alembic heads` = single `033`; combined suite 75 passed. |
| F2 | HIGH | **CLOSED (by amendment W4-E08)** | Amendment present and coherent at `docs/.../week4/evidence/w4-00-decisions.md:91-105` (§2b), explicitly superseding the D03/PR-15 "hash-only" wording and retaining the raw `challenge` column with residual-risk rationale. Justification is sound: the `webauthn` library requires the server-side raw `expected_challenge`; hash-only would require replacing the library's challenge check with custom `clientDataJSON` parsing (higher risk) or passing the client-supplied value (circular/unsafe). Residual exposure = a 32-byte, single-use, TTL-bounded (≤300s) nonce in plaintext; not a credential. Raw challenge is never logged (see below). Docstrings aligned: `033_webauthn_challenges.py:9-11`, `webauthn_challenge_service.py:45-47`. |
| F3 | MEDIUM | **CLOSED** | Opportunistic SAVEPOINT-guarded cleanup now runs on store: `backend/app/services/webauthn_challenge_service.py:48,66-76`. Tests added: `test_store_opportunistically_cleans_expired_rows` and `test_store_survives_opportunistic_cleanup_failure` (`test_webauthn_challenge_lifecycle.py:190-221`). |
| F4 | LOW | **CLOSED** | `WEBAUTHN_CHALLENGE_TTL_SECONDS: int = 300` added at `backend/app/config.py:37`; consumed via `_resolve_ttl` (`webauthn_challenge_service.py:29-33,58`). |
| F5 | LOW | **CLOSED** | Migration 033 docstring now documents the raw column as an approved W4-E08 deviation (`033_webauthn_challenges.py:9-11`). |
| F6 | INFO | **CLOSED** | `ON DELETE CASCADE` FK policy retained as intended (`033_webauthn_challenges.py:93-98`); no action required. |

### No raw challenge/hash in logs (re-confirmed)

Grep of the two services shows only these log statements, none interpolating a challenge value or hash: `passkey_service.py:98` "Registration: no challenge stored"; `passkey_service.py:179` session id prefix only (`session_id[:8]`); `passkey_service.py:243` "Auth: no challenge stored"; `webauthn_challenge_service.py:76` cleanup-failure warning with `exc_info=True` (no payload).

### No other stale expected-head pin

Search for `032`/`033` across `backend/**/*.py` finds only: `main.py:17` (033), the three updated assertions (033), `033_...py:39-40` (`revision="033"`, `down_revision="032"`), `032_...py:26` (`revision="032"`), and `test_pr12_...contract.py:60` (032 migration-file shape assertion, correct to keep). No remaining expected-head assertion pins 032.

## Raw command results (recheck, via guard)

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/alembic heads"
033 (head)
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/alembic heads']
```

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && .venv/bin/python -m pytest tests/test_webauthn_challenge_lifecycle.py tests/test_passkey_ceremonies.py tests/test_security_settings_guards.py tests/test_manage_write_permissions.py tests/test_auth_error_handling.py tests/test_pr09_migration.py tests/test_pr12_note_knowledge_points_contract.py tests/test_optional_session_state.py -q"
........................................................................ [ 96%]
...                                                                      [100%]
75 passed in 4.64s
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && .venv/bin/python -m pytest ... -q']
```

(The two lifespan-based files in this set — `test_auth_error_handling.py`, `test_optional_session_state.py` — exercise `with TestClient(main.app)`; their passing confirms `main.lifespan` → `validate_database_readiness()` succeeds against the 033 DB, which is the end-to-end proof the F1 BLOCKER is gone.)

## Residual risk still considered potentially material

None material. The only accepted residual is W4-E08's plaintext short-lived, single-use challenge nonce (≤300s TTL, never logged, not a credential/secret), documented as an intentional amendment. If a future threat model treats DB-at-rest nonce disclosure as in scope, revisit W4-E08 with hash-only lookup; not required at PR-15 risk level.

## Recheck boundary

- No source file modified; only this §recheck section appended to `pr-15-review.md`.
- No DB create/drop; no `blog_db`/`blog_v2`; no git write; `alembic upgrade/downgrade` not run (existing replay evidence + code reading only).
