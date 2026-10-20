# Independent Review — Week 4 F07 (full-chain error sanitization) + F05 (structured cross-layer OCR errors)

- Reviewer role: independent reviewer (no implementation ownership)
- Mode: READ-ONLY source inspection + scratch-DB reproduction; no source changed; no git write
- Date: 2026-09-27
- Scratch DB: `astra_week4_fix` (via `scripts/week4-scratch-guard.py`); `blog_db`/`blog_v2` untouched
- Changed set verified present: `backend/app/services/ai_service.py`, `ai_gateway.py`, `capture_recognition.py`, `capture_failure_taxonomy.py` (new), `backend/tests/test_ai_error_chain.py` (new). Also modified in the same worktree: `backend/app/services/capture_ai_draft.py` (see F1).

## VERDICT: PASS_WITH_NOTES

Core F07 invariant holds: no raw provider response body reaches raised exceptions, WARNING logs, `ai_call_logs.error`/`attempts`, or `ai_runs.error_message_safe`/`error_code` — independently reproduced with a synthetic secret marker. F05 structured categories propagate `AIProviderError.category -> GatewayCallResult.failure_category -> recognition error_code/DTO` as specified, and existing `timeout`/`provider_error`/`no_provider` contracts are preserved (all required tests pass). One MEDIUM cross-layer gap remains on the draft path (category collapses to `unknown`); it was acknowledged by the implementer but is reachable in the shipped code.

## Findings

| id | severity | problem | evidence (file:line) | required action |
|----|----------|---------|----------------------|-----------------|
| F1 | MEDIUM | `capture_ai_draft` does not consume `GatewayCallResult.failure_category`; it re-sniffs the generic gateway message. `_build_failure_result` sets `error=str(exc)` and `_call_with_fallback` always raises `AIProviderError(message="All AI providers failed")`, so the sniff input is the constant "All AI providers failed" and every provider failure collapses to `provider_error`/`unknown`. Native `httpx.ReadTimeout`, 401/403/429, 404 and non-JSON bodies all lose their F05 category on the draft path (recognition path is correct). | `capture_ai_draft.py:103` (`raise RuntimeError(err)`), `capture_ai_draft.py:150-152` (`categorize_provider_error(str(e))`), `ai_gateway.py:218`, `ai_service.py:263-267` | Mirror `capture_recognition._resolve_provider_category`: call `categorize_provider_category(gw.failure_category)` first and only fall back to string sniffing. Add a `failure_category` field to `DraftResult` (or at minimum derive `error_code` from the structured category). Capture the result in `capture_service.trigger_draft`. Reproduced below. |
| F2 | LOW | `ai_gateway._build_failure_result` persists `str(exc)[:500]` directly into `ai_call_logs.error` / `ai_runs.error_message_safe`; safety depends entirely on upstream only ever raising the fixed-message `AIProviderError`. Any future exception carrying body text would be persisted verbatim. Current code is safe (verified), so this is defense-in-depth. | `ai_gateway.py:218`, `ai_gateway.py:161-162` | Optional hardening: build the persisted error from an allowlisted category, not `str(exc)`; add a regression test for a body-bearing exception. |
| F3 | LOW | `capture_recognition` passes `str(e)` into the fallback sniff on the `RuntimeError` branch. Not logged or persisted, and the structured category takes precedence, so no leak today. Latent only if a direct `RuntimeError` with body text is raised by the adapter boundary. | `capture_recognition.py:145-147`, `capture_recognition.py:166-173` | No action required; keep structured-category-first ordering. |
| F4 | LOW | `ai_validator` writes `str(e)[:200]` of a Pydantic `ValidationError` into `error_message_safe`, which can echo model output (not the provider HTTP envelope/credentials). Pre-existing and outside the F05/F07 changed set. | `ai_validator.py:111-116` | Optional: confirm model-output echo in `error_message_safe` is acceptable; otherwise replace with a fixed message. Not a provider-body leak. |

Severity counts: BLOCKER 0, HIGH 0, MEDIUM 1, LOW 3.

## Verification detail

### 1. No raw provider body reaches exceptions / logs / columns (F07) — PASS
- Source grep of the changed files for `response.text`, `response.content`, `str(e)`/`str(exc)`, `err_str`, `exc_info`:
  - `ai_service.py`: no `response.text`; transport/status/parse failures raise fixed-message `AIProviderError` (`ai_service.py:170-182`, `185-197`). Bodies are never read.
  - `ai_gateway.py:218` is the only `str(exc)`; exception is the sanitized `AIProviderError` (see F2).
  - `capture_recognition.py:147` / `capture_ai_draft.py:152` `str(e)` are used only to pick a category, never logged or persisted (see F1/F3).
- Independent synthetic-secret reproduction (fresh marker `sk-live-REVIEW-SECRET-9c3b1d`, mocked 401 with body containing the key + `Authorization: Bearer`): secret absent from WARNING logs, `gw.error`/`gw.attempts`, `ai_call_logs.error`/`attempts`, and `ai_runs.error_message_safe`; `run.error_code='provider_auth'`, `run.status='failed'`. Output in Raw results §2.
- Test-suite reproduction: `SecretSanitizationTest` and `PersistedErrorSanitizationTest` (scratch DB) pass.

### 2. Category propagation (F05) — PASS (recognition path)
| native failure | category | surface |
|---|---|---|
| `httpx.ReadTimeout` / `ConnectError` | `provider_timeout` | `ai_service.py:170-171` |
| 401 / 403 / 429 | `provider_auth` | `ai_service.py:24,44-46` |
| 404 | `invalid_model` | `ai_service.py:47-48` |
| non-JSON HTTP body | `invalid_response` | `ai_service.py:179-182` |
| non-JSON `message.content` | `invalid_response` | `ai_service.py:185-190` |
Chain confirmed: `AIProviderError.category` (`ai_service.py:38-41`) -> `GatewayCallResult.failure_category` (`ai_gateway.py:219`) -> recognition `failure_category`/`error_code` (`capture_recognition.py:101-102,166-212`). Rising order in `_call_with_fallback` preserves the last category (`ai_service.py:260-267`). Covered by `test_ai_error_chain.py` (all pass).

### 3. Gap check — `capture_ai_draft.py` (see F1)
Status: CONFIRMED OPEN. The draft path loses category precision. Note: `capture_ai_draft.py` is **not** outside the changeset — `git diff` shows 91 changed lines in this worktree and its except-blocks were rewritten for log sanitization, so the "out of write scope" note understates that the same change touched the file and left the propagation incomplete. Repro output: native `httpx.ReadTimeout` -> draft `error_code='provider_error'`, category `unknown` (expected `timeout` / `provider_timeout`). Because `CaptureOut.failure_category` is derived from `error_code` (`schemas/capture.py:162-168`), the DTO also reports `unknown` for draft failures.

### 4. Preserved contracts — PASS
- `no_provider`: `ValueError("No AI provider configured...")` retained (`ai_service.py:210-213`); mapped in both adapters (`capture_recognition.py:129-144`, `capture_ai_draft.py:135-149`).
- `timeout` / `provider_error`: retained (`capture_recognition.py:196-212`; generic failures still `provider_error`).
- Failure-matrix tests pass: `test_i6_capture_failure_matrix.py` (timeout -> `timeout`, raw `gw.error` -> `provider_error` with no leaked text, draft schema -> `schema_error`).

### 5. Required test run — PASS
Command (verbatim, via guard):

```
python3 scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_fix" -- bash -c "cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_ai_error_chain.py tests/test_ai_gateway.py tests/test_capture_service.py tests/test_i6_capture_failure_matrix.py tests/test_capture_taxonomy.py -q"
```

Result: `62 passed, 2 warnings, 31 subtests passed in 2.07s`; guard line `PASS: db_name='astra_week4_fix' source=explicit:--url`. The 2 warnings are pre-existing `AsyncMock ... never awaited` warnings in `test_ai_gateway.py::LogWriteFailureTest` (mock teardown, not a functional failure).

## Raw results

### 1. Required pytest run
```
..............................................................                                                    [100%]
62 passed, 2 warnings, 31 subtests passed in 2.07s
PASS: db_name='astra_week4_fix' source=explicit:--url; executing [...]
```

### 2. Independent reproduction (`/var/folders/.../opencode/f05f07_repro.py`, scratch DB, evolved)
```
AI draft failed category=unknown code=provider_error capture_id=None
== (3) capture_ai_draft category precision ==
  native ReadTimeout -> draft error_code='provider_error' (expected 'timeout' / provider_timeout per F05)
  error_message_safe='AI provider error'
== (1) synthetic secret propagation ==
  secret in WARNING logs: False
  gw.error='All AI providers failed'
  gw.failure_category='provider_auth'
  secret in gw.error/attempts: False
  secret in ai_call_logs.error/attempts: False
  run.error_code='provider_auth' status='failed'
  secret in ai_runs.error_message_safe: False
PASS: db_name='astra_week4_fix' source=explicit:--url; executing [...]
```

## Unresolved questions / remaining

1. F1 required action needs a write-scope decision and a new approval; it changes `DraftResult`/`trigger_draft` and adds a test. Not performed under this read-only review.
2. Whether the draft path's `failure_category`/`error_code` precision is a product requirement or an accepted limitation — the implementer flagged it as known. Recommend treating F1 as in-scope follow-up before closing F05, since F05 is described as "cross-layer".
3. `error_message_safe` semantics for Pydantic echoes (F4) is a pre-existing behavior outside this changeset; confirm separately.

Status: F07 PASS (verified), F05 PASS on the recognition path, F05 PARTIAL on the draft path (F1). No BLOCKER/HIGH. No source modified; evidence file only.
