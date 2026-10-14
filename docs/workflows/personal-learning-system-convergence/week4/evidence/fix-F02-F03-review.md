# Independent Review — Week 4 fixes F02 (CLI cross-event-loop) + F03 (WebAuthn challenge matching)

- Reviewer: independent (did not implement these changes)
- Date: 2026-09-27
- Repo: /Users/limengyang/2025-blog-public
- Branch: `refactor/baseline` (dirty working tree; no commit, no push)
- Scope files claimed under review:
  - `backend/app/cli.py` (tracked, modified)
  - `backend/app/services/webauthn_challenge_service.py` (untracked/new)
  - `backend/app/services/passkey_service.py` (tracked, modified)
  - `backend/tests/test_webauthn_challenge_lifecycle.py` (untracked/new)
  - `backend/tests/test_passkey_ceremonies.py` (untracked/new)
  - `backend/tests/test_cli_registration_server.py` (untracked/new)
- Read-only: no source modified, no git write. One file created: this evidence file.
- Databases: only `astra_week4_pr15` via the Week 4 guard. `blog_db` / `blog_v2` never targeted.
- Migration 033 was **not** modified by this fix (see §5).

## Verdict

**PASS** for both F02 and F03 at the reviewed scope.

- **F03 achieves true per-ceremony isolation.** All three verify paths (`verify_registration`,
  `verify_authentication`, `verify_operator_registration`) derive the challenge from the
  client-presented `response.clientDataJSON`, hash it, and select the EXACT matching row by
  `challenge_hash` + `purpose` + binding (`passkey_service.py:48-80`, `:131-136`, `:209-219`,
  `:276-281`; `webauthn_challenge_service.py:166-204`). There is **no fallback** to
  `get_valid_challenge` (latest) on any verify path; the latest-selection function has no
  production caller left. Missing/malformed `clientDataJSON` fails closed (`:64-66`, `:33-52`).
  Consume semantics are preserved: registration/authentication consume only on success
  (`:145`, `:293`); operator consumes **before** verification (`:219`).
- **F02 fixed.** `create_registration_server` now owns exactly one `_ServerEventLoop` (one
  asyncio loop on one daemon thread) and one `AsyncEngine` for the server lifetime
  (`cli.py:159-189`, `:216-229`); every DB call runs through `event_loop.run(...)` and there is
  no per-request loop. Two consecutive `GET /api/passkey/register/options` against the real HTTP
  server both return 200 and persist one challenge each; only one `passkey-registration-loop`
  thread exists.
- No regression found: all call sites (`cli.py`, `routers/auth.py`) use the new async
  signatures; the legacy in-memory store names are gone from product code; migration 033 is
  unchanged.

Remote CI execution and a real hardware-authenticator registration are **NOT_VERIFIED**
(no push authorization; no authenticator in scope). All verification here is local and guarded.

## Severity counts

| Severity | Count |
|---|---|
| BLOCKER | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 3 (test/evidence-coverage; no code defect) |
| INFO | 3 |

No BLOCKER or HIGH finding, so no further reproduction is required beyond what is recorded below.

## Findings

| # | Sev | Area | Finding | Evidence |
|---|---|---|---|---|
| 1 | LOW | F02 test coverage | The new CLI regression test drives only two `GET /options` requests. The re-check standard in `quality-reassessment.md` also names `verify` and failure-retry over HTTP; those paths share the same `event_loop`/`_run_on_db` funnel, so structural risk is low, but the POST `/verify` and retry error path are not asserted at HTTP level. | `backend/tests/test_cli_registration_server.py:67-106`; `cli.py:222-229,262-293` |
| 2 | LOW | F03 concurrency evidence | No **committed, automated two-session PostgreSQL** concurrency test was added; the committed A/B tests are single-session (`test_passkey_ceremonies.py:168-300`) and the lifecycle concurrency test only inserts/counts rows (`:169-179`). The F03 re-check standard asked to "补 PG 并发证据". I reproduced it independently on PG (see §4) and behavior is correct, but that proof lives only in this review, not in the suite. | `test_passkey_ceremonies.py`; `test_webauthn_challenge_lifecycle.py:169-179` |
| 3 | LOW | Latent footgun / stale evidence | `get_valid_challenge` (latest-selection) is retained with no production caller; the historical gate probe `evidence/gate/recheck_probes.py:74-80` still calls it and describes the pre-fix bug. Harmless today, but a future verify call could silently reintroduce latest-selection. | `webauthn_challenge_service.py:135-163`; `evidence/gate/recheck_probes.py:64-83` |
| 4 | INFO | Stale probe | `evidence/reassessment-2026-09-26/week4_auth_review_probe.py:45-54` asserts the **old** buggy behavior (`after_b==(False,0)`, `after_b_consumed==(True,1)`). Under the fix those assertions are now inverted, so the probe no longer reflects reality; it is an evidence artifact, not part of CI. | `week4_auth_review_probe.py:41-54` |
| 5 | INFO | Defense in depth | `_resolve_client_challenge` re-decodes the stored raw challenge and re-compares it to the client bytes after the hash lookup (`:76-79`). Redundant with the hash match, but a correct, cheap integrity check — not a defect. | `passkey_service.py:73-80` |
| 6 | INFO | Schema confirmation | Migration 033 already carries `challenge_hash` + the `(challenge_hash)` index, so no schema change was needed for F03. 033 is untracked, so "unchanged" is confirmed by mtime (Sep 26 14:52, a day before the Sep 27 fix files) and by the absence of any schema requirement in the fix; a git diff is impossible without a tracked baseline. | `033_webauthn_challenges.py:81-82,128-134`; file mtimes |

## 1. F03 source verification (per-ceremony matching, fail-closed, consume semantics)

- Client challenge extraction: `_client_data` returns `None` for non-dict credential / missing
  response / missing or empty `clientDataJSON` / bad base64 / non-JSON / non-object payload
  (`webauthn_challenge_service.py:33-52`). `client_challenge_bytes` returns `None` on any
  malformed step (`:55-70`). `challenge_hash_from_credential` returns `None` (`:73-78`).
- Exact selection: `_resolve_client_challenge` hashes the client bytes and calls
  `get_valid_challenge_by_hash(db, sha256(client), purpose, session_id=..., user_id=...)`; it
  returns `(None, None)` if no **unconsumed, unexpired, purpose/binding-matched** row exists, and
  additionally rejects a hash/raw mismatch (`passkey_service.py:64-80`).
- `get_valid_challenge_by_hash` filters on `challenge_hash == <exact>`, `purpose == <exact>`,
  `consumed_at IS NULL`, `expires_at > now()`, and enforces `session_id` / `user_id` equality or
  `IS NULL` exactly like `get_valid_challenge` (`webauthn_challenge_service.py:183-204`).
- No fallback: grep of `backend/app` shows `get_valid_challenge(...)` (latest) is referenced only
  by its own definition and tests; every product verify path uses the `_by_hash` variant.
- Consume semantics:
  - `verify_registration`: `mark_consumed` only after `verify_registration_response` succeeds
    (`:139-145`); on exception the row stays unconsumed (`:151-153`).
  - `verify_authentication`: `mark_consumed` only on success (`:284-294`); failure returns the
    original `stored_sign_count` (`:295-297`).
  - `verify_operator_registration`: `mark_consumed` runs **before** `verify_registration_response`
    (`:219`, then `:221-235`) — preserved operator semantics.

## 2. F02 source verification (one loop/engine per server lifetime)

- `_ServerEventLoop` allocates one `asyncio.new_event_loop()`, runs it `run_forever()` on a daemon
  thread named `passkey-registration-loop`, and exposes `run(coro)` via
  `asyncio.run_coroutine_threadsafe(...).result()` (`cli.py:159-182`).
- `create_registration_server` creates the loop and engine once, wraps all DB work in
  `_run_on_db` → `event_loop.run(...)`, and returns a `_RegistrationHTTPServer` that owns both for
  shutdown (`cli.py:216-229`, `:192-213`). The verify→register second step also runs via
  `event_loop.run(_register())` (`:293`), and `cmd_register_passkey` calls `server.server_close()`
  in `finally` (`:358-363`), which disposes the engine on the loop and then closes the loop.
- No per-request `new_event_loop()` remains on the registration-server path (the remaining
  `asyncio.new_event_loop()` uses at `:387,434,463,499,536` belong to one-shot CLI subcommands
  that create their engine inside the same function, not to the long-lived server).

## 3. Required guarded test run (exact command from the task)

```
$ python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr15" -- bash -c "cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_webauthn_challenge_lifecycle.py tests/test_passkey_ceremonies.py tests/test_cli_registration_server.py tests/test_security_settings_guards.py tests/test_manage_write_permissions.py -q"

..................................................                       [100%]
50 passed in 7.12s
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_webauthn_challenge_lifecycle.py tests/test_passkey_ceremonies.py tests/test_cli_registration_server.py tests/test_security_settings_guards.py tests/test_manage_write_permissions.py -q']
```

Raw result: **50 passed**, guard accepted the scratch target. This includes the two new F02 CLI
tests, both new lifecycle/ceremony suites, and the two pre-existing touched suites (no collateral
failure).

## 4. Independent reproduction (reviewer's own scripts in temp dir, not in repo)

### 4a. F03 A/B isolation + fail-closed + operator consume semantics

A and B stored for the same purpose with B newer (so latest-selection would pick B); the client
answers A. Result: verifier receives exactly A's raw bytes, A is consumed, B is untouched. Forged
and missing `clientDataJSON` are rejected with nothing consumed. Operator wrong-session is
rejected, and with a stub that raises, the operator challenge is still consumed (consume-before-verify).

```
Registration: no matching challenge stored
Registration: no matching challenge stored
Operator registration: no matching challenge for session sess-B...
Operator registration verification failed: stubbed fail
F03 A/B registration isolation: PASS; forged+missing fail closed: PASS
F03 A/B authentication isolation: PASS
F03 operator session-binding + consume-before-verify: PASS
F02 two consecutive CLI options requests: both 200; one loop thread: PASS
ALL INDEPENDENT REPRODUCTIONS PASS
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing ['bash', '-c', 'cd backend && PYTHONPATH=. .venv/bin/python /var/folders/.../f03_f02_independent_repro.py']
```

### 4b. Two consecutive real HTTP `/options` requests (F02)

The reviewer script independently starts `create_registration_server(0, "localhost", DATABASE_URL)`,
performs two `urllib` GETs, asserts both status 200 with distinct challenges, and asserts exactly
one `passkey-registration-loop` thread exists — same conclusion as the committed test. Result
recorded in the block above ("both 200; one loop thread: PASS").

### 4c. PostgreSQL two-session concurrency (F03 acceptance "PG 并发证据")

Two separate engines/sessions against real PostgreSQL, concurrently:

```
Registration: no matching challenge stored
PG concurrent different challenges: both verified+consumed own row: PASS
PG concurrent same challenge: exactly one consumes (row lock): PASS
PG CONCURRENCY REPRODUCTIONS PASS
PASS: db_name='astra_week4_pr15' source=explicit:--url; executing [...f03_pg_concurrency_repro.py]
```

Interpretation: (1) two distinct outstanding challenges each verify against and consume their own
row with no interference; (2) two concurrent attempts on the **same** challenge yield exactly one
success — the `SELECT ... FOR UPDATE` row lock plus `consumed_at` filter prevents double-consume.

## 5. Regression sweep

- **Callers of changed functions**: only `backend/app/cli.py` (`generate_registration_options`,
  `verify_registration`) and `backend/app/routers/auth.py` (`verify_authentication`,
  `generate_authentication_options`, `generate_operator_registration_options`,
  `verify_operator_registration`) call the service; all pass `db` first and `await`, matching the
  new async signatures. No caller uses the old synchronous form.
- **Latest-selection on verify**: none in product code. `get_valid_challenge` is used only by
  tests and the historical probe.
- **Legacy in-memory stores**: `_reg_challenge_store` / `_auth_challenge_store` /
  `_operator_reg_challenge_store` appear nowhere except the migration docstring describing their
  removal.
- **Migration 033**: not modified (mtime Sep 26 14:52, before the Sep 27 fix files); the fix needs
  no schema change and uses existing `challenge_hash` + index. `downgrade()` fail-closed logic is
  untouched.
- **Touched pre-existing suites** (`test_security_settings_guards.py`,
  `test_manage_write_permissions.py`) still pass under the same run.

## Unresolved questions

1. **HTTP `verify`/retry coverage (F02, LOW #1).** Should the CLI regression test add a POST
   `/api/passkey/register/verify` request (and a failure-retry) against the real server so the
   full re-check standard — options, verify, failure retry — is machine-asserted, not just
   structurally implied?
2. **Committed PG concurrency test (F03, LOW #2).** Should a two-session PG test (different
   challenges both consume; same challenge exactly one consumes) be added to the suite? I proved
   the behavior on PG here, but nothing in CI locks it in.
3. **Fate of the latest-selection API and stale probes (LOW #3 / INFO #4).** `get_valid_challenge`
   and `recheck_probes.py` still encode the old behavior. Retain as-is, delete, or annotate as
   non-verification helpers? Any decision should keep a single documented verification entry point
   (the `_by_hash` path).
4. **Real authenticator + remote CI remain NOT_VERIFIED** (no push authorization, no hardware
   authenticator). The verification stub used in the ceremony tests exercises the real DB
   challenge lifecycle and the real code path up to the `webauthn` boundary only.

## Scope / safety statement

- Files read include the six scope files plus `backend/app/models/webauthn_challenge.py`,
  `backend/app/routers/auth.py`, `backend/alembic/versions/033_webauthn_challenges.py`,
  `scripts/week4-scratch-guard.py`, and the Week 4 reassessment/review evidence docs.
- Files written: this evidence file only. No source edited; no `git add`/`commit`/`push`/`merge`.
- DBs: only `astra_week4_pr15` via the guard (`astra_week4_*` allowlist); `blog_db`/`blog_v2`
  never connected or written. Reviewer reproduction scripts live under the temp dir, not the repo.
