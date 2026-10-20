# PR-14 — Independent Review / Verification

Role: independent REVIEWER/VERIFIER (did not implement). Mode: read-only (this file is the only
artifact created; no source, test, migration, or DB was modified). Refs inspected at working tree
(no commit).

Status: `FAIL` — no BLOCKER, but two HIGH defects: (1) the derived DTO category collapses every real
provider auth/model failure to `unknown`; (2) the "logs never leak raw provider response / API keys"
claim is contradicted by current source. Structural claims (no migration, no column, single alembic
head 032, derived-not-persisted, serialization, UI empty state, retry, tests green) all verify.

---

## 1. Verdict summary

| Area | Claim | Verified |
|------|-------|----------|
| No DB migration / no column | yes | PASS — `alembic heads` = single `032 (head)`; no `failure_category` in `backend/app/models/` or `backend/alembic/` |
| Enum has exactly 8 categories | yes | PASS — source + test |
| Every produced `error_code` maps to a category or intentionally `unknown` | yes | PARTIAL — `provider_error` (the dominant provider failure) falls to `unknown`; the dedicated sniffer result is discarded before the DTO |
| `failure_category` derived, not persisted | yes | PASS structurally — `@computed_field`; no column |
| Serializes in API response | yes | PASS — `response_model=list[CaptureOut]` etc.; pydantic 2.11.1; `model_dump`/JSON include the key |
| Logs cannot leak API keys / raw provider body | yes | FAIL — raw provider body logged (truncated); draft path not redacted at all |
| Empty-result state distinct from error banner | yes | PASS for recognition; MEDIUM mislabel when the same code comes from the draft stage |
| Category label renders; retry works w/o infinite loop | yes | PASS — synchronous retry, no polling loop |
| Frontend type matches backend serialized field | yes | PASS — `str` enum serializes `"provider_auth"` etc.; union matches |
| 10-sample baseline honest (real-provider rate NOT_VERIFIED) | yes | PASS on §3 disclosure; PARTIAL on §2 category column (see F1/F9) |

Severity counts: **BLOCKER 0 · HIGH 2 · MEDIUM 3 · LOW 2 · INFO 2**.

---

## 2. Findings

| id | severity | problem | evidence (file:line) | required action |
|----|----------|---------|----------------------|-----------------|
| F1 | HIGH | Derived DTO category is wrong for all real provider failures. `recognize_image` sets `error_code="provider_error"` for every non-timeout provider failure, and `CaptureOut.failure_category` derives from `error_code` only. `_ERROR_CODE_CATEGORY` has no `provider_error` key → `unknown`. The richer `categorize_provider_error()` result stored on `RecognitionResult.failure_category` (`provider_auth` / `invalid_model`) is never persisted or consumed, so the UI can never show those labels for a real 401/403/429/404. | `backend/app/services/capture_failure_taxonomy.py:26-41` (no `provider_error`); `backend/app/services/capture_recognition.py:155-169`; `backend/app/schemas/capture.py:162-168`; `backend/app/services/capture_service.py:225-226` (category not written); claim table `.../pr-14-ocr-baseline-report.md:36-37` | Surface the sniffed category at serialization time (e.g. distinguish auth/model/timeout `error_code`s at recognition, or carry/derive the category where the message is still available). Add an HTTP/DTO-level test asserting `failure_category` for a `provider_error` case. |
| F2 | HIGH | Sanitization claim is false. `ai_service` embeds the raw provider response body in the raised error (`f"AI API error ({status}): {response.text}"`), and `capture_recognition` logs `_sanitize_log_detail(err_str)`. The redactor only replaces `sk-…`, `bearer …`, and keyword patterns; arbitrary raw JSON/response bodies pass through (truncated to 200 chars). The evidence file asserts raw provider response bodies are never logged. | `backend/app/services/ai_service.py:130`, `:213`; `backend/app/services/capture_recognition.py:27-43`, `:157-163`; false claim `.../pr-14-logs-sample.txt:16-17` | Correct the claim to "known secret patterns are redacted and the detail is truncated to 200 chars", or redact/whitelist to a structured safe field instead of logging the exception string. |
| F3 | MEDIUM | Redactor not applied on the draft branch. `capture_ai_draft` logs the raw provider exception (`str(e)[:200]`) with no redaction in its `ValueError` / `RuntimeError` / generic branches. Any secret present in a `call_text` provider error is written to logs verbatim. | `backend/app/services/capture_ai_draft.py:114`, `:124`, `:135` | Reuse the sanitizer on these branches, or centralize provider-error logging. |
| F4 | MEDIUM | `error_code` stage conflation in the derived taxonomy. `empty_input` is produced both for empty image bytes (recognition) and for an empty recognized-text draft (`capture_service.trigger_draft`), and both map to `image_fetch` → the UI renders "图片读取失败" for a draft-stage text problem. Likewise a draft-stage `empty_result` (validation `EMPTY_RESULT`) triggers the recognition-specific "未识别到内容 / 这张图片里没有识别到可用的文字" banner although no image is involved. | `backend/app/services/capture_service.py:252-255`; `backend/app/services/ai_validator.py:80-86`; `backend/app/services/capture_failure_taxonomy.py:31,33`; `src/app/manage/(workspace)/capture/components/capture-workspace.tsx:399-408` | Derive/display by `last_stage` (or split the error vocabulary) so OCR-image semantics are not applied to draft failures. |
| F5 | MEDIUM | Frontend test fixture is unrealizable and masks F1. It pairs `error_code: 'provider_error'` with `failure_category: 'provider_auth'`, a combination the backend never emits (backend yields `unknown`). No backend or HTTP/DTO test asserts `CaptureOut.failure_category`, so the derivation bug is untested end-to-end. | `src/app/manage/(workspace)/capture/components/capture-workspace.test.tsx:119-121`; no `failure_category` assertion in `backend/tests/` | Fix the fixture to the real backend output, and add a DTO/HTTP test (see F1). |
| F6 | LOW | `no_provider` → `provider_auth` labels a configuration gap as "AI 服务未授权或额度不足". Semantically imprecise. | `backend/app/services/capture_failure_taxonomy.py:27`; `capture-workspace.tsx:68` | Consider a distinct label/handling for unconfigured provider. |
| F7 | LOW | Layering: `schemas/capture.py` imports from `services/capture_failure_taxonomy.py` (schema → service), opposite to the documented `router → schema → service` direction. No cycle today. | `backend/app/schemas/capture.py:7-10`; AGENTS.md §3 | Move the enum/mapping to a schema/domain-neutral module or duplicate a thin enum at the contract layer. |
| F8 | INFO | `invalid_model` and `image_format` are declared but no produced `error_code` maps to them (documented for `image_format`). `invalid_model` is reachable only through the discarded `RecognitionResult.failure_category`. | `backend/app/services/capture_failure_taxonomy.py:6-7,57` | Keep as documented future values, but do not present them as delivered until wired (ties to F1). |
| F9 | INFO | Baseline wording. §3 is honest (`NOT_VERIFIED`, "1/10 is a harness property"). But §2's "failure_category / Category label (zh-CN)" columns for the `provider_error` samples show the internal dataclass value, which does not match the serialized DTO (`unknown`). | `.../pr-14-ocr-baseline-report.md:36-41`, `:46-52` | Relabel §2 columns as "recognition-layer category (pre-DTO)" or add a serialized-DTO row. |

No BLOCKER found. F1 and F2 are HIGH and both carry a concrete reproduction in §3.

---

## 3. Concrete reproductions (HIGH)

### F1 — DTO returns `unknown` for a real auth failure

```
$ cd backend && .venv/bin/python -c "...CaptureOut.model_validate(failed_ns_with_error_code_provider_error)..."
pydantic 2.11.1
categorize_failure(provider_error) = unknown
categorize_provider_error("AI API error (401): invalid api_key") = provider_auth
DTO failure_category for error_code=provider_error => CaptureFailureCategory.UNKNOWN
DTO model_dump has key: True
JSON: {...,"error_code":"provider_error",...,"failure_category":"unknown"}
```

`test_ocr_baseline.py` rows `auth_401` and `invalid_model_404` expect `provider_auth` / `invalid_model`
on `RecognitionResult.failure_category`, but `capture_service` never persists that field and the API
serializes `CaptureOut` (which recomputes from `error_code`). The user-facing category is therefore
`unknown` (label "未知错误") for 401/403/429/404.

### F2 — raw provider response body is logged

```
$ cd backend && .venv/bin/python -c "from app.services.capture_recognition import _sanitize_log_detail; print(_sanitize_log_detail('AI API error (400): {\"error\":{\"type\":\"invalid_request_error\",\"message\":\"Unsupported image format: webp bytes 52494646\"}}'))"
AI API error (400): {"error":{"type":"invalid_request_error","message":"Unsupported image format: webp bytes 52494646"}}
```

`ai_service.py:130` builds the message from `response.text`; the redactor leaves the body intact.
A secret that does not match `sk-…`, `bearer …`, or the keyword alternation is logged verbatim
(truncated to 200 chars), contradicting `pr-14-logs-sample.txt:16-17`.

---

## 4. Verification performed

### 4.1 Migrations / schema (no migration, no column)

```
$ cd backend && .venv/bin/python -m alembic heads
032 (head)

$ grep -rn "failure_category" backend/app/models/ backend/alembic/
(no output)
```

Versions dir ends at `032_note_knowledge_points.py`; no `033` added. `CaptureItem` has only
`error_code` / `error_message_safe` (no category column) — `backend/app/models/capture.py:59-60`.

### 4.2 Enum + mapping

`CaptureFailureCategory` has exactly the 8 declared values (`capture_failure_taxonomy.py:13-23`).
Produced `error_code` vocabulary and mapping:

| produced code | produced at | category |
|---|---|---|
| `empty_input` | recognition (`capture_recognition.py:83`), draft (`capture_ai_draft.py:71`, `capture_service.py:254`) | image_fetch (see F4) |
| `empty_result` | recognition (`:125`), validator (`ai_validator.py:84`) | invalid_response |
| `parse_error` | recognition (`:183`), draft (`:139`), validator (`:96`) | invalid_response |
| `schema_error` | draft (`:110`), validator (`:104,115`) | schema_validation |
| `no_provider` | recognition (`:148`), draft (`:118`) | provider_auth |
| `timeout` | recognition (`:155`), draft (`:128`) | provider_timeout |
| `provider_error` | recognition (`:155`), draft (`:128`), gateway (`ai_gateway.py:148`) | **unknown (unmapped — F1)** |
| `attachment_missing` | `capture_service.py:203` | image_fetch |

Produced error_codes with **no explicit mapping**: `provider_error` (falls through to `unknown`).
This is not an intentional "future code": a dedicated `categorize_provider_error()` exists and is
computed, but its result never reaches the DTO.

### 4.3 DTO derivation / serialization

`CaptureOut.failure_category` is a `@computed_field` (not a stored column), returns `None` unless
`status == "failed"`, and is present in `model_dump()` / `model_dump_json()` with pydantic 2.11.1
under `model_validate` from an ORM-like object. Routers declare `response_model=list[CaptureOut]`
and `response_model=CaptureOut` (`backend/app/routers/captures.py:35,43,57,68,80,91`). No other
capture DTO consumer broke (`npx tsc --noEmit` exit 0).

### 4.4 UI / retry

Empty-result is a distinct amber `EmptyResultBanner` selected by `error_code === 'empty_result'`;
other failures render `ErrorBanner` with the category label (`capture-workspace.tsx:399-408,509-540`).
`handleRecognize` is a single awaited request — no polling, no effect re-entry loop
(`capture-workspace.tsx:174-187`, `:98-115`). Frontend union matches the serialized `str` enum
(`src/lib/api/captures.ts:17-25,55`).

---

## 5. Raw command outputs

### 5.1 Backend pytest (direct — refused by scratch guard, as expected)

```
$ cd backend && .venv/bin/python -m pytest tests/test_capture_taxonomy.py tests/test_ocr_baseline.py tests/test_i6_capture_failure_matrix.py tests/test_capture_service.py tests/test_i6_capture_http.py -q
...
RuntimeError: Database safety: non-scratch connection refused before DBAPI
app/utils/scratch_db_safety.py:62: RuntimeError
=========================== short test summary info ============================
FAILED tests/test_i6_capture_failure_matrix.py::CaptureFailureMatrixTest::test_empty_recognized_text_stays_failed_without_draft
FAILED tests/test_i6_capture_failure_matrix.py::CaptureFailureMatrixTest::test_missing_attachment_stays_failed_without_downstream_objects
FAILED tests/test_capture_service.py::CaptureServiceTest::test_convert_creates_drafts_not_mistakes
FAILED tests/test_capture_service.py::CaptureServiceTest::test_convert_is_idempotent
FAILED tests/test_capture_service.py::CaptureServiceTest::test_convert_requires_ready_status
FAILED tests/test_capture_service.py::CaptureServiceTest::test_create_capture_sets_uploaded_status
FAILED tests/test_capture_service.py::CaptureServiceTest::test_draft_failure_zero_pollution
FAILED tests/test_capture_service.py::CaptureServiceTest::test_draft_with_fake_succeeds
FAILED tests/test_capture_service.py::CaptureServiceTest::test_get_capture_raises_for_missing_id
FAILED tests/test_capture_service.py::CaptureServiceTest::test_list_captures_returns_list
FAILED tests/test_capture_service.py::CaptureServiceTest::test_patch_capture_clears_failed_status
FAILED tests/test_capture_service.py::CaptureServiceTest::test_patch_capture_manual_path
FAILED tests/test_capture_service.py::CaptureServiceTest::test_recognition_failure_zero_pollution
FAILED tests/test_capture_service.py::CaptureServiceTest::test_recognition_with_fake_succeeds
FAILED tests/test_i6_capture_http.py::test_admin_can_upload_private_image_and_create_capture
FAILED tests/test_i6_capture_http.py::test_invalid_upload_is_rejected_and_does_not_leave_temp_file
16 failed, 17 passed, 33 subtests passed in 3.03s
```

### 5.2 Backend pytest (scratch guard, existing `astra_week4_pr14`, no DB created/dropped)

```
$ cd backend && python3 ../scripts/week4-scratch-guard.py run --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr14" -- .venv/bin/python -m pytest tests/test_capture_taxonomy.py tests/test_ocr_baseline.py tests/test_i6_capture_failure_matrix.py tests/test_capture_service.py tests/test_i6_capture_http.py -q
.................................                                                                    [100%]
33 passed, 33 subtests passed in 2.37s
PASS: db_name='astra_week4_pr14' source=explicit:--url; executing ['.venv/bin/python','-m','pytest',
'tests/test_capture_taxonomy.py','tests/test_ocr_baseline.py','tests/test_i6_capture_failure_matrix.py',
'tests/test_capture_service.py','tests/test_i6_capture_http.py','-q']
```

### 5.3 Frontend vitest

```
$ npx vitest run "src/app/manage/(workspace)/capture"
 RUN  v3.2.7 /Users/limengyang/2025-blog-public
 ✓ src/app/manage/(workspace)/capture/components/capture-content.test.tsx (2 tests) 93ms
 ✓ src/app/manage/(workspace)/capture/components/capture-workspace.test.tsx (4 tests) 113ms
 Test Files  2 passed (2)
      Tests  6 passed (6)
```

### 5.4 TypeScript

```
$ npx tsc --noEmit
EXIT=0
```

---

## 6. Unresolved questions for the main agent

1. F1 intended fix: should the recognition layer emit a more specific `error_code`
   (`provider_auth` / `invalid_model`) so the derived DTO is correct and persisted-compatible, or
   should a new derivation path carry the message-derived category into `CaptureOut`? The current
   design cannot express auth/model categories through the DTO.
2. F2/F3: is the sanitization requirement scoped to recognition only, or repository-wide? If the
   latter, `capture_ai_draft.py` and the `ai_call_logs.error` persistence path
   (`ai_gateway.py:88-108`) also need review.
3. Are the baseline report's §2 category columns intended as "recognition-layer" values? If yes,
   the table should say so to avoid implying the UI shows `provider_auth` / `invalid_model`.

---

# 7. Recheck (round 2) — 2026-09-26

Re-verification against the current working tree (no source changed by this reviewer). Implementation
reports F1–F5 fixed; all were independently re-read and re-run.

## 7.1 Final verdict

**`PASS_WITH_NOTES`** — F1–F5 and F9 are CLOSED; the regression contract (`provider_error` →
`unknown`) holds. No BLOCKER/HIGH/MEDIUM remain. Residual LOW/INFO items only (F6, F7, plus new
INFO notes below). The sanitization claim is now true for both adapter log paths.

| Finding | Severity (orig) | Status | Evidence |
|---------|-----------------|--------|----------|
| F1 DTO collapses provider failures to `unknown` | HIGH | **CLOSED** | `capture_failure_taxonomy.py:28-29` adds `provider_auth`/`invalid_model`; `capture_recognition.py:137-153,171-185` RuntimeError branch sets specific `error_code`; independent repro below |
| F2 raw provider body logged / false claim | HIGH | **CLOSED** | `_sanitize_log_detail` removed; `capture_recognition.py:124-129,141-146,156-161` log only category/code/capture_id; evidence `pr-14-logs-sample.txt:1-8,20-22` now accurate |
| F3 draft path not redacted | MEDIUM | **CLOSED** | `capture_ai_draft.py:114-174` logs only category/code/capture_id; `str(e)` used only by local sniff at `:146` |
| F4 stage-conflated OCR/draft messages | MEDIUM | **CLOSED** | `capture-workspace.tsx:406-429,524-551` stage-aware labels + `showEmptyResult` gate; draft tests `capture-workspace.test.tsx:138-171` |
| F5 unrealizable frontend fixture / no DTO test | MEDIUM | **CLOSED** | fixture now `error_code='provider_auth'`+`failure_category='provider_auth'` (`:120-122`); `test_capture_taxonomy.py:262-283` `DtoFailureCategorySerializationTest` |
| F6 `no_provider` → `provider_auth` label | LOW | **OPEN** (unchanged, cosmetic) | `capture_failure_taxonomy.py:27`; `capture-workspace.tsx:68` |
| F7 schema→service layering | LOW | **OPEN** (unchanged) | `schemas/capture.py:7-10` |
| F8 `invalid_model` unreachable | INFO | **CLOSED** | now emitted at `capture_recognition.py:184`; `image_format` remains intentionally declared-unmapped (`capture_failure_taxonomy.py:6`) |
| F9 baseline wording / column conflation | INFO | **CLOSED** | `pr-14-ocr-baseline-report.md:28-63` separates pre-DTO `error_code` vs DTO `failure_category`; `:65-68` keeps real-provider `NOT_VERIFIED` |

New INFO notes (non-blocking):
- `capture_service.py:285` calls `draft_mistake(draft_input, use_fake=use_fake)` without `capture_id`, so draft log lines carry `capture_id=None`. Log-content leak is fixed; only log context is missing.
- Implementer summary "backend 50 passed" is not reproduced by the specified command — actual is **37 passed / 41 subtests** (I ran the exact command; verifiable below). vitest `8 passed` and `tsc` clean do match.
- `AiErrorCode` (`ai_task_result.py:18-30`) still documents itself as consistent with capture `error_code` but does not include the new `provider_auth`/`invalid_model` values; doc drift only, no enum-based validation consumes capture codes.
- `_provider_failure_error_fields` / `_draft_provider_failure_fields` duplicate the same mapping (minor DRY).

## 7.2 Regression check (item 2)

`tests/test_i6_capture_failure_matrix.py:102-123` injects `GatewayCallResult(error="secret provider endpoint and token")`;
no marker matches, so it still yields `error_code="provider_error"`, safe message `"AI provider error"`
(asserted at `:120-123`). Confirmed by the run below (file included in the 37-passed suite) and by the
independent repro: `generic -> error_code=provider_error category=unknown`.

## 7.3 Independent end-to-end repro (F1 + log leak)

```
$ cd backend && .venv/bin/python -c "...DTO/model + recognize_image + logger capture..."
DTO provider_auth        -> provider_auth
DTO invalid_model        -> invalid_model
DTO timeout              -> provider_timeout
DTO provider_error       -> unknown
DTO no_provider          -> provider_auth
DTO empty_result         -> invalid_response
DTO empty_input          -> image_fetch
DTO attachment_missing   -> image_fetch
401      -> error_code=provider_auth category=provider_auth safe='AI provider authentication failed'
404      -> error_code=invalid_model category=invalid_model safe='AI model unavailable'
generic  -> error_code=provider_error category=unknown safe='AI provider error'
LOG: Recognition failed category=provider_auth code=provider_auth capture_id=cap-1
LEAK_PRESENT: False
```

Draft path (F3):

```
$ cd backend && .venv/bin/python -c "...draft_mistake with RuntimeError('...Bearer sk-live-DRAFTLEAK...')..."
draft -> provider_auth AI provider authentication failed
LOG: AI draft failed category=provider_auth code=provider_auth capture_id=None
LEAK: False
```

## 7.4 Raw command outputs (item 4)

```
$ cd backend && .venv/bin/python -m alembic heads
032 (head)
$ grep -rn "failure_category" app/models/ alembic/
NONE
```

```
$ cd backend && python3 /Users/limengyang/2025-blog-public/scripts/week4-scratch-guard.py run \
    --url "postgresql+asyncpg://limengyang@localhost:5432/astra_week4_pr14" -- \
    .venv/bin/python -m pytest tests/test_capture_taxonomy.py tests/test_ocr_baseline.py \
    tests/test_i6_capture_failure_matrix.py tests/test_capture_service.py tests/test_i6_capture_http.py -q
............................... [ 83%]
......                                                                   [100%]
37 passed, 41 subtests passed in 1.99s
PASS: db_name='astra_week4_pr14' source=explicit:--url; executing ['.venv/bin/python','-m','pytest',
'tests/test_capture_taxonomy.py','tests/test_ocr_baseline.py','tests/test_i6_capture_failure_matrix.py',
'tests/test_capture_service.py','tests/test_i6_capture_http.py','-q']
```

```
$ npx vitest run "src/app/manage/(workspace)/capture"
 ✓ src/app/manage/(workspace)/capture/components/capture-content.test.tsx (2 tests) 51ms
 ✓ src/app/manage/(workspace)/capture/components/capture-workspace.test.tsx (6 tests) 67ms
 Test Files  2 passed (2)
      Tests  8 passed (8)
```

```
$ npx tsc --noEmit
TSC_EXIT=0
```

## 7.5 Out-of-scope / deferred (item 5)

- `ai_gateway._write_call_log` persists `result.error[:500]` (`ai_service.py:130` raw body) into
  `ai_call_logs`, and `_finish_run_record`/`ai_run` persist `result.error` up to 500 chars
  (`ai_gateway.py:88-108,140-160`). This is pre-existing and outside the recognition/draft warning-log
  path that PR-14 owns; it does **not** contradict any PR-14 acceptance criterion (which concerns
  warning logs and the DTO). Tracked as **INFO / deferred**, not a PR-14 blocker.

