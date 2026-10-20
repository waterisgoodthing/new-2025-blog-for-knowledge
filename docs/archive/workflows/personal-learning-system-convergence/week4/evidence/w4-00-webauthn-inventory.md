# W4-00 WebAuthn / Login Auth Inventory (READ-ONLY evidence)

Scope: current source at preflight time. Read-only; no files outside this evidence file were
modified, no DB/migration commands were run, no git writes were performed.

Source of truth for this document: actual files under `backend/app/` plus the current
`backend/alembic/versions/` graph. Line numbers are exact for the revision read.

---

## 1. `backend/app/services/passkey_service.py`

### 1.1 Module-level globals (all in-memory dicts)

| Line | Name | Type | Declaration |
|------|------|------|-------------|
| 14 | `_reg_challenge_store` | `dict[str, bytes]` | `{}` |
| 15 | `_auth_challenge_store` | `dict[str, bytes]` | `{}` |
| 16 | `_operator_reg_challenge_store` | `dict[str, bytes]` | `{}` |

The names are **underscore-prefixed/private**, not the public names assumed by the Week 4 plan.
There are exactly three global stores, all plain dicts, all module-scoped, all lost on process
restart, and all shared process-wide (no per-request/per-session namespacing except the operator
store key).

### 1.2 Private helpers

| Line | Signature |
|------|-----------|
| 19 | `_get_rp_id() -> str` |
| 23 | `_get_origin() -> str` |
| 27 | `_get_rp_name() -> str` |
| 31 | `_resolve_rp_id(rp_id: str \| None = None) -> str` |
| 35 | `_resolve_origin(origin: str \| None = None) -> str` |
| 39 | `_b64url_encode(data: bytes) -> str` |
| 43 | `_b64url_decode(s: str) -> bytes` |

There is **no** `_generate_challenge()` helper; challenges are produced inline via
`secrets.token_bytes(32)` (lines 53, 114, 174). The PR-15 task text assumes a
`_generate_challenge()` function that "remains unchanged" — it does not exist.

### 1.3 Public function signatures

| Line | Signature | Ceremony |
|------|-----------|----------|
| 50 | `generate_registration_options(rp_id: str \| None = None) -> dict` | registration (generate/store) |
| 80 | `verify_registration(attestation: dict, expected_origin: str \| None = None, expected_rp_id: str \| None = None) -> dict \| None` | registration (verify/consume) |
| 110 | `generate_operator_registration_options(session_id: str, rp_id: str \| None = None) -> dict` | operator registration (generate/store) |
| 141 | `verify_operator_registration(attestation: dict, session_id: str, expected_origin: str \| None = None, expected_rp_id: str \| None = None) -> dict \| None` | operator registration (verify/consume) |
| 171 | `generate_authentication_options(rp_id: str \| None = None) -> dict` | authentication (generate/store) |
| 186 | `verify_authentication(assertion: dict, stored_credential_id: str, stored_public_key: bytes, stored_sign_count: int, expected_origin: str \| None = None, expected_rp_id: str \| None = None) -> tuple[bool, int]` | authentication (verify/consume) |
| 218 | `async register_credential(db: AsyncSession, credential_id: str, public_key: bytes, device_name: str \| None = None) -> PasskeyCredential` | credential persistence |
| 241 | `async reset_credential(db: AsyncSession) -> bool` | credential reset |
| 250 | `async replace_credential(db: AsyncSession, credential_id: str, public_key: bytes, device_name: str \| None = None) -> PasskeyCredential` | credential replace |
| 274 | `async get_credential(db: AsyncSession) -> PasskeyCredential \| None` | credential read |

`get_credential` (line 274) has **no callers** anywhere in `backend/` (definition only). It is dead
code today.

### 1.4 Exact challenge storage keys and lifecycle

| Ceremony | Store global | Write key | Read/consume key | Consumption |
|----------|--------------|-----------|------------------|-------------|
| registration | `_reg_challenge_store` | `["current"]` (line 55) | `.get("current")` (line 87) | `del _reg_challenge_store["current"]` only on **success** (line 99) |
| authentication | `_auth_challenge_store` | `["current"]` (line 175) | `.get("current")` (line 196) | `del _auth_challenge_store["current"]` only on **success** (line 211) |
| operator_registration | `_operator_reg_challenge_store` | `[session_id]` (line 116) | `.pop(session_id, None)` (line 149) | pop happens **before** verification, so it is consumed on read regardless of verification outcome |

Exact current keys (quoted):

- registration: `_reg_challenge_store["current"]`
- authentication: `_auth_challenge_store["current"]`
- operator_registration: `_operator_reg_challenge_store[session_id]` where `session_id` is the
  per-request random token passed to `generate_operator_registration_options`

Semantics notes (current behavior, not aspiration):

- Registration and authentication use the single fixed key `"current"`, so **only one outstanding
  challenge exists globally** for each of those ceremonies. A second `generate_*` call overwrites
  the first; concurrent ceremonies interfere and cross-user replay is structurally possible.
- Registration/auth challenges are **not** expired by time and are **not** deleted on a failed
  verification (only on success), so a failed attempt leaves `"current"` populated. They are never
  keyed by user or session.
- Operator challenges are keyed by an ephemeral `session_id` (random `secrets.token_hex(16)`
  generated in the router) and are popped on read before verification, so they are single-use but
  consume on any verification attempt. They are not tied to the admin session and have no TTL.
- No cleanup/GC, no expiry timestamp, no hashing, no DB backing for any of the three stores.

---

## 2. Call sites of `passkey_service` functions

| File:line | Call | Ceremony / role |
|-----------|------|-----------------|
| `backend/app/cli.py:19-22` | imports `generate_registration_options, register_credential, reset_credential` (plus `verify_registration` imported/used later) | CLI |
| `backend/app/cli.py:168` | `generate_registration_options(rp_id=host)` | registration generate (local CLI HTTP server, `GET /api/passkey/register/options`) |
| `backend/app/cli.py:191` | `verify_registration(attestation, expected_origin=origin, expected_rp_id=host)` | registration verify (local CLI, `POST /api/passkey/register/verify`) |
| `backend/app/cli.py:207` | `await register_credential(session, result["credential_id"], result["public_key"], device_name)` | registration persistence |
| `backend/app/cli.py:299` | `await reset_credential(session)` | credential reset (`cmd_reset_passkey`) |
| `backend/app/routers/auth.py:229` | `from app.services.passkey_service import verify_authentication` | authentication import |
| `backend/app/routers/auth.py:241` | `verify_authentication(assertion, stored_credential_id=cred.credential_id, stored_public_key=cred.public_key, stored_sign_count=cred.sign_count)` | authentication verify (`POST /api/auth/login-passkey`) |
| `backend/app/routers/auth.py:299-300` | `from ... import generate_authentication_options`; `return generate_authentication_options()` | authentication generate (`GET /api/auth/passkey/auth-options`) |
| `backend/app/routers/auth.py:336,339` | `generate_operator_registration_options(session_id)` | operator registration generate (`POST /api/auth/passkey/operator/reg-options`) |
| `backend/app/routers/auth.py:351,354` | `verify_operator_registration(req.attestation, session_id=req.session_id, expected_origin=..., expected_rp_id=...)` | operator registration verify (`POST /api/auth/passkey/operator/register`) |
| `backend/app/routers/auth.py:367` | `replace_credential(db, result["credential_id"], result["public_key"], req.device_name)` | operator registration credential replace |

Call-site gaps (important for PR-15 scope):

- **No API/router endpoint calls `generate_registration_options` or `verify_registration`.** The
  only registration path is the local dev CLI server in `backend/app/cli.py`. There is no
  `POST /api/auth/passkey/reg-options` route (removed; asserted absent in
  `backend/tests/test_security_settings_guards.py:71-73`).
- `register_credential` is called only from CLI; `reset_credential` only from CLI;
  `get_credential` has no callers.

---

## 3. Login / authentication router map

Router: `backend/app/routers/auth.py`, `router = APIRouter(prefix="/api/auth", tags=["auth"])`
(line 36). Registered in `backend/main.py:97` via `app.include_router(auth.router)`.

### 3.1 Session/auth dependencies

| Line | Function | Behavior / status codes |
|------|----------|-------------------------|
| 65 | `_is_auth_bypass_active()` | True only when `AUTH_BYPASS == "true"` AND `AUTH_BYPASS_ALLOW == "true"` |
| 76 | `async _resolve_session_user(session_token, db) -> tuple[User \| None, str \| None]` | returns `(user, auth_level)`; bypass returns first `is_admin` user with `auth_level="password"` |
| 107 | `async get_current_user(request, session_token=Cookie(None, alias="admin_session"), db=Depends(get_db)) -> User` | 401 `"Not authenticated"` |
| 119 | `async get_current_admin(request, session_token=Cookie(None, alias="admin_session"), db=Depends(get_db)) -> User` | 401 `"Not authenticated"`; 403 `"Admin privileges required"` |
| 133 | `async get_passkey_admin(...) -> User` | 401; 403 non-admin; 403 `"Passkey authentication required for this action"` when `auth_level != "passkey"` |
| 152 | `async get_optional_user(...) -> User \| None` | no error |
| 161 | `async get_optional_admin(...) -> User \| None` | no error |

### 3.2 Endpoints

| Method + path | Line | Signature highlights | Error responses / status codes |
|---------------|------|----------------------|--------------------------------|
| `POST /api/auth/login` | 172 | `login(req: LoginRequest, request, db)` | 401 `"Invalid credentials"` (line 181) if user missing or `verify_password` false. **No throttling.** |
| `POST /api/auth/login-passkey` | 223 | `login_passkey(request, db)` — reads raw JSON `body["assertion"]` | 400 `"Missing assertion"` (234); 401 `"No passkey registered"` (239); 401 `"Passkey verification failed"` (248); 401 `"No admin user found"` (257) |
| `GET /api/auth/passkey/auth-options` | 297 | `passkey_auth_options()` — public, no auth | none |
| `POST /api/auth/passkey/operator/validate-key` | 320 | `operator_validate_key(x_operator_registration_key: Header(alias="X-Operator-Registration-Key"))` | 403 `"Operator registration is not configured"` / `"Invalid operator registration key"` (via `_require_operator_key`, lines 303-317) |
| `POST /api/auth/passkey/operator/reg-options` | 328 | `operator_passkey_reg_options(req: OperatorRegOptionsRequest, x_operator_registration_key: Header(...))` | 403 from `_require_operator_key`; returns `{"options": ..., "session_id": secrets.token_hex(16)}` |
| `POST /api/auth/passkey/operator/register` | 343 | `operator_passkey_register(req: OperatorRegisterRequest, x_operator_registration_key: Header(...), db)` | 403 from `_require_operator_key`; HTTP 200 with `OperatorRegisterResponse(success=False, ...)` on verification failure (361-364) and on internal error (395-398); HTTP 200 `success=True` on success (387-391) |
| `GET /api/auth/passkey/status` | 401 | `passkey_status(db)` — public | returns `{"registered": bool}` |
| `POST /api/auth/logout` | 409 | `logout(request, session_token=Cookie(None, alias="admin_session"), db)` | sets `revoked=True`; returns 200 |
| `POST /api/auth/register` | 442 | `register(req: RegisterRequest, db, x_registration_key: Header(alias="X-Registration-Key"))` | 403 `"Registration is disabled"` (455); 403 `"Invalid registration key"` (465); 409 `"Username already exists"` (472) |
| `GET /api/auth/me` | 480 | `me(request, session_token=Cookie(...), db)` | 401 `"Not authenticated"` (488) |
| `GET /api/auth/session-state` | 492 | `session_state(session_token=Cookie(...), db)` | returns `SessionStateOut` |
| `GET /api/auth/sessions` | 501 | `list_sessions(user=Depends(get_current_admin), db)` | 401/403 via dependency |
| `DELETE /api/auth/sessions/{session_id}` | 526 | `revoke_session(session_id, user=Depends(get_current_admin), db)` | 400 `"Invalid session id"` (537); 404 `"Session not found"` (547) |
| `POST /api/auth/set-password` | 553 | `set_password(req: SetPasswordRequest, user=Depends(get_passkey_admin), session_token=Cookie(...), db)` | 401/403 via `get_passkey_admin` (requires `auth_level == "passkey"`) |

### 3.3 Session creation

- Password login (lines 183-219): `generate_session_token()` -> `hash_session_token(token)` ->
  `AdminSession(user_id, token_hash, auth_level="password", expires_at=get_session_expiry("password"), ip, user_agent)`;
  audit `action="login"`, `auth_level="password"`; cookie `max_age = PASSWORD_SESSION_DAYS * 86400` (3 days).
- Passkey login (lines 259-293): same shape with `auth_level="passkey"`, `expires_at=get_session_expiry("passkey")`,
  audit `auth_level="passkey"`, cookie `max_age = PASSKEY_SESSION_DAYS * 86400` (7 days).
- `PASSKEY_SESSION_DAYS = 7`, `PASSWORD_SESSION_DAYS = 3` in `backend/app/utils/auth.py:7-8`.
- Passkey login does **not** require a prior `/passkey/auth-options` challenge to be bound to the
  credential; verification reads the global `"current"` auth challenge.

---

## 4. Admin auth contract actually implemented

- **Stateful cookie session, HttpOnly.** Cookie name `admin_session` (`auth.py:40`), `path="/api"`
  (`auth.py:41`), `samesite="lax"` (`auth.py:42`), `httponly=True`, `secure` only when
  `request.url.scheme == "https"` (`auth.py:45-58`).
- **Backing table:** `admin_sessions` via model `AdminSession` in
  `backend/app/models/session.py:11-26` (`id UUID PK`, `user_id FK users.id CASCADE`,
  `token_hash String(64) unique`, `auth_level String(20)`, `expires_at`, `revoked`, `ip`,
  `user_agent`, `created_at`). Raw token is never stored; only `sha256` hex `token_hash`
  (`utils/auth.py:26-27`).
- **Authorization boundary:** `get_current_admin` (`auth.py:119`) and `get_passkey_admin`
  (`auth.py:133`). `AuthGate`-style frontend gating is UX only; the backend dependencies are the
  real boundary.
- **Passkey credential table:** `passkey_credentials` via `PasskeyCredential` in
  `backend/app/models/session.py:29-38` (single-row model in practice; service reads
  `scalar_one_or_none()`).
- **Admin password store:** `admin_passwords` via `AdminPassword` (`session.py:41-50`); `set_password`
  updates both `admin_passwords` and the admin `users.password_hash` (`auth.py:570-588`).
- **Auth bypass:** `AUTH_BYPASS` + `AUTH_BYPASS_ALLOW` (both default `"false"`); active only if both
  are `"true"` (`auth.py:65-69`).
- **No Bearer/JWT path is used for admin auth.** `JWT_*` settings exist (config.py:9-11) but have no
  references in `backend/app` other than their declaration.

---

## 5. Relevant config (`backend/app/config.py`)

| Line | Setting | Default |
|------|---------|---------|
| 9 | `JWT_SECRET_KEY` | `"your-secret-key-change-this"` (declared; unused for admin session auth) |
| 10 | `JWT_ALGORITHM` | `"HS256"` (declared; unused) |
| 11 | `JWT_EXPIRE_MINUTES` | `1440` (declared; unused) |
| 13 | `ENABLE_REGISTRATION` | `True` |
| 14 | `REGISTRATION_KEY` | `""` |
| 31 | `AUTH_BYPASS` | `"false"` |
| 32 | `AUTH_BYPASS_ALLOW` | `"false"` |
| 34 | `WEBAUTHN_RP_ID` | `"localhost"` |
| 35 | `WEBAUTHN_ORIGIN` | `"http://localhost:2025"` |
| 36 | `WEBAUTHN_RP_NAME` | `"Blog Admin"` |
| 38 | `OPERATOR_REGISTRATION_KEY` | `""` |

There is **no existing throttling/rate-limit configuration** and **no login-throttle settings** in
`config.py` (`LOGIN_THROTTLE_*` do not exist). Session TTLs are hardcoded constants in
`backend/app/utils/auth.py:7-8`, not config.

---

## 6. Existing tests touching passkey / WebAuthn / login

No dedicated WebAuthn/passkey ceremony test exists (`ls backend/tests | rg -i "passkey|webauthn|throttle"`
returns nothing; no `test_passkey_ceremonies.py`, no `test_webauthn_*`, no `test_login_throttling*`).

| File | What it covers |
|------|----------------|
| `backend/tests/test_manage_write_permissions.py` | Route-surface contract: imports `get_current_admin, get_passkey_admin` (line 10); enumerates public write routes incl. `POST /api/auth/login`, `POST /api/auth/login-passkey`, operator routes (lines 14-19, 33-40); asserts every non-public write route depends on `get_current_admin` or `get_passkey_admin`; uses `admin_session` cookie (line 67). No ceremony/verification logic. |
| `backend/tests/test_security_settings_guards.py` | Asserts `/api/auth/passkey/reg-options` is **absent** (lines 71-73) and `/api/auth/passkey/status` is **present** (lines 76-78). |
| `backend/tests/test_auth_error_handling.py` | `verify_password` returns False for `"disabled"`/malformed hashes (lines 25-27); disabled-account login `POST /api/auth/login` returns 401 (line 38). |
| `backend/tests/test_temp_admin_bootstrap.py` | `verify_password` against bootstrapped admin password hash (lines 47, 60). |
| `backend/tests/test_optional_session_state.py` | Sets an `admin_session` cookie (line 41) to exercise optional session resolution. |
| `backend/tests/test_pr09_verify_http.py`, `test_pr09_verify_api_contract.py`, `test_pr10_*_http.py`, `test_pr12_*_http.py`, `test_pr12_verify_api.py`, `test_pr12_verify_concurrency.py`, `test_pr11_dashboard_http.py`, `test_pr13_*_http.py`, `test_i6_capture_http.py`, `lsr03_final_verifier_harness.py`, `lsr03_seed_rehearsal.py` | Integration tests that call `POST /api/auth/login` to obtain a real session for other feature tests. They are not passkey/throttle tests. |

There are currently **no automated tests exercising `generate_registration_options`,
`verify_registration`, `generate_authentication_options`, `verify_authentication`,
`generate_operator_registration_options`, or `verify_operator_registration` behavior.**

---

## 7. AiRun model / table and AI gateway write sites (for PR-19)

### 7.1 Model

`backend/app/models/ai_run.py:11` — table `ai_runs` (`__tablename__ = "ai_runs"`, line 14).

- `target_type: Mapped[str | None]` — `String(50)`, nullable (line 20)
- `target_id: Mapped[str | None]` — `String(100)`, nullable (line 21)
- Other columns: `task_type` (19), `provider_used` (22), `model` (23), `prompt_version` (24),
  `status` (25), `validation_status` (26-28), `input_summary` (29), `replay_input` (30),
  `output_data` (31), `warnings` (32), `error_code` (33), `error_message_safe` (34), `attempt` (35),
  `parent_run_id` FK self (38-42), `review_status` (43-45), `review_revision` (46-48),
  `reviewed_at`/`review_note` (49-50), `latency_ms` (51), `started_at`/`finished_at` (52-55),
  `created_at`/`updated_at` (56-64).
- Registered in `backend/app/models/registry.py:70` and `backend/app/models/__init__.py:16,57`.

### 7.2 Migration

`backend/alembic/versions/018_add_ai_runs.py` (`revision="018"`, `down_revision="017"`) creates
`ai_runs` with `target_type sa.String(50) nullable` (line 25) and `target_id sa.String(100) nullable`
(line 26), plus indexes `idx_ai_runs_created_at/task_type/status/review_status/parent_run_id`.

### 7.3 Where AiRun rows are written

| File:line | Operation |
|-----------|-----------|
| `backend/app/services/ai_run_service.py:78-109` | `start_ai_run(db, *, task_type, target_type=None, target_id=None, ...)` constructs `AiRun(...)` (line 92) and `db.add(run)` / `flush` (107-108). **Insert.** |
| `backend/app/services/ai_run_service.py:112-133` | `complete_ai_run(...)` mutates an existing run to `succeeded` (update, no insert). |
| `backend/app/services/ai_run_service.py:136-156` | `fail_ai_run(...)` mutates to `failed` (update). |
| `backend/app/services/ai_run_service.py:159-174` | `retry_ai_run(...)` calls `start_ai_run(...)` copying `parent.target_type`/`parent.target_id` (167-168) — insert. |
| `backend/app/services/ai_gateway.py:104-128` | `_start_run_record(...)` is the only production caller of `start_ai_run` (line 117) and **does not pass `target_type` or `target_id`**. |
| `backend/app/services/ai_gateway.py:131-174` | `_finish_run_record(...)` loads run by id (line 140) and calls `fail_ai_run` (145) or `complete_ai_run` (163). |
| `backend/app/services/ai_gateway.py:266,304,341,385` | `call_text` / `call_vision` / `call_general` / `call_stream` each call `_start_run_record(task_type_str, input_summary, prompt_version)`, then `_finish_run_record`. |
| `backend/app/routers/ai_runs.py:70-80` | `POST /api/admin/ai/runs/{run_id}/retry` -> `ai_run_service.retry_ai_run` (insert via service). |
| `backend/app/routers/ai_runs.py:83-102` | `POST /api/admin/ai/runs/{run_id}/decision` -> `decide_ai_run` (update only). |

### 7.4 Current `target_id` behavior (verified)

Every `ai_runs` row created through the production path (`ai_gateway._start_run_record`) is inserted
with `target_type = NULL` and `target_id = NULL`, because the gateway passes neither argument to
`start_ai_run` (`ai_gateway.py:117-123`). Retried rows copy the parent's NULL
(`ai_run_service.py:167-168`). No other code writes these columns. So **`target_id` is currently
always NULL in practice**; PR-19 must add the wiring to populate it.

---

## 8. Alembic migrations and head

`backend/alembic/versions/` contains 34 migration files:

```
001_initial_schema.py
002_add_status_field.py
003_restore_notes_status_index.py
004_add_ai_metadata_to_notes.py
005_add_folders.py
006_add_admin_sessions.py
007_change_folder_cascade.py
008_add_audit_logs.py
009_add_music_daily.py
010_add_managed_content_entries.py
011_add_subject_taxonomy.py
012_add_question_drafts_and_questions.py
013_add_mistakes_and_review.py
014_add_attachments.py
015_add_capture_items.py
016_add_ai_call_logs.py
017_add_prompt_version.py
018_add_ai_runs.py
019_align_subject_knowledge_tree.py
020_add_canonical_question_contract.py
021_add_attempt_learning_loop.py
022_add_admin_profiles.py
023_add_file_workspace_metadata.py
024_add_markdown_versions_links_search.py
025_align_fresh_install_metadata.py
026_legacy_system_retirement.py
027_guestbook.py
028_review_items_v2.py
029_review_record_states.py
030_reanswer_audit.py
031_mistake_visibility_public.py
032_note_knowledge_points.py
0ec85724afb9_add_user_admin_field.py
1119bee5a419_add_images_to_notes.py
```

Revision chain (from `revision` / `down_revision` in each file):

```
001
 └─ 002
     └─ 0ec85724afb9
         └─ 1119bee5a419
             └─ 003
                 └─ 004 → 005 → 006 → 007 → 008 → 009 → 010 → 011 → 012 → 013 → 014
                    → 015 → 016 → 017 → 018 → 019 → 020 → 021 → 022 → 023 → 024 → 025
                    → 026 → 027 → 028 → 029 → 030 → 031 → 032
```

- `032_note_knowledge_points.py`: `revision = "032"`, `down_revision = "031"`.
- No migration file declares `down_revision = "032"`. **Head is exactly one: `032`.**
- Migration 033 does not exist yet; `032 -> 033` is the expected next link for PR-15.
- Note: migrations `027`–`032` are currently **untracked** in git (`??` in `git status`), and the
  worktree has many other uncommitted changes. w4-00's "no uncommitted migration files" check does
  not hold as-shipped; see DELTAS.

---

## DELTAS vs Week 4 task assumptions

1. **Global dict names differ from the plan.** W4-00/PR-15 expect public names
   `registration_challenges`, `authentication_challenges`, `operator_challenges`. Actual names are
   private and distinct: `_reg_challenge_store` (passkey_service.py:14),
   `_auth_challenge_store` (15), `_operator_reg_challenge_store` (16). Any grep/contract test that
   keys off the plan names will fail against current source.

2. **Operator storage key is not `["current"]` and is not the admin session.**
   `_operator_reg_challenge_store` is keyed by an **ephemeral random** `session_id`
   (`secrets.token_hex(16)` produced at `auth.py:338`, passed to
   `generate_operator_registration_options`, stored at `passkey_service.py:116`, popped at 149).
   PR-15's router step "`store_challenge(..., purpose='operator_registration', session_id=session['id'])`"
   assumes an authenticated session object for the operator flow; the current operator flow is
   authorized by the `X-Operator-Registration-Key` header and has no session object.

3. **There is no registration API endpoint.** Registration generation/verification live only in the
   local CLI (`backend/app/cli.py:166-246`); the API `reg-options` route was removed and is asserted
   absent (`test_security_settings_guards.py:71-73`). PR-15 step "Update registration endpoint: call
   `store_challenge(..., user_id=current_user.id)`" has no current endpoint to update. Any DB-backed
   registration challenge for the CLI path must either stay CLI-only or a new endpoint must be
   designed (out of the stated plan).

4. **Authentication options are generated without any user.** `GET /api/auth/passkey/auth-options`
   is public and calls `generate_authentication_options()` with no user; PR-15's
   `purpose='authentication', user_id=user.id` binding assumes a user is known at generation time,
   which is not true today. Current auth challenges are keyed only by global `"current"`.

5. **Consumption semantics differ by ceremony, and differ from the PR-15 draft.**
   Registration/authentication delete the challenge only on **successful** verification
   (passkey_service.py:99, 211); the draft `verify_and_consume_challenge` consumes on any lookup.
   Operator registration pops **before** verification (line 149), i.e. consumes on attempt. PR-15
   must decide/ preserve actual semantics per ceremony, not a single uniform rule.

6. **No `_generate_challenge()` helper exists.** Challenges are inline `secrets.token_bytes(32)`
   (lines 53, 114, 174). PR-15 says the helper "remains unchanged".

7. **No existing WebAuthn ceremony tests.** PR-15 acceptance says "Existing passkey tests pass (or are
   updated to use DB instead of mocks)"; there are none. Only route-surface guards
   (`test_manage_write_permissions.py`, `test_security_settings_guards.py`) exist.

8. **Login throttling config does not exist.** PR-16 proposes
   `LOGIN_THROTTLE_THRESHOLD_WARN`, `LOGIN_THROTTLE_DELAYS`, `LOGIN_THROTTLE_IP_TTL`; `config.py` has
   none of these today, and `POST /api/auth/login` (auth.py:172-220) has no counter/delay logic.

9. **Login body is `{"username","password"}` (LoginRequest, schemas/auth.py:7-9)** — account-level
   throttling should key on `username`; there is no email field.

10. **Password-login session is also created on the operator passkey register path?** No — operator
    register only replaces the credential and audits `operator_passkey_register`; it does not create a
    session. Confirmed at auth.py:343-398.

11. **Migration head is 032 (confirmed), but migrations 027–032 are untracked in git.** The w4-00
    checkbox "Confirm no uncommitted migration files" is not satisfiable as-is without deciding how
    those untracked Week 3 migrations are handled before 033 is authored.

12. **`target_id` in `ai_runs` is currently always NULL** for gateway-created runs (PR-19 must add
    wiring); do not assume existing rows carry a meaningful target.
