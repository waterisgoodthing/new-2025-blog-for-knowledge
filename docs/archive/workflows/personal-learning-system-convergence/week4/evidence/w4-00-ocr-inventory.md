# W4-00 — OCR / Capture Recognition Flow Inventory

Status: `PARTIAL` (read-only inventory; no code, DB, migration, or git write performed)
Scope: current OCR/capture recognition shape only. Evidence is source-verified at the
paths and line numbers below. Historical week4 task text is treated as a claim to be
checked, not as fact.

Repository: `/Users/limengyang/2025-blog-public`
Branch: `refactor/baseline` (worktree is dirty; see below — nothing was modified by this task)

---

## 1. File inventory

### Backend — capture domain

| Path | Role | Exists |
|---|---|---|
| `backend/app/models/capture.py` | SQLAlchemy `CaptureItem` model (table `capture_items`), state + error fields + CHECK constraints | yes |
| `backend/app/schemas/capture.py` | Pydantic request/response DTOs + AI output schema `MistakeDraftSuggestionV1` | yes |
| `backend/app/services/capture_service.py` | Capture lifecycle orchestration (create / patch / trigger_recognition / trigger_draft / convert) | yes |
| `backend/app/services/capture_recognition.py` | Narrow single-image OCR/vision adapter; wraps `call_vision` | yes |
| `backend/app/services/capture_ai_draft.py` | Narrow text-AI adapter for structured mistake draft; wraps `call_text` | yes |
| `backend/app/routers/captures.py` | Admin HTTP router `/api/admin/captures` | yes |
| `backend/alembic/versions/015_add_capture_items.py` | Migration creating `capture_items` | yes |
| `backend/alembic/versions/016_add_ai_call_logs.py` | Migration creating `ai_call_logs` | yes |

### Backend — AI/OCR gateway + provider layer

| Path | Role |
|---|---|
| `backend/app/services/ai_gateway.py` | Unified AI call entry + call logging (`call_text`, `call_vision`, `call_general`, `call_stream`) |
| `backend/app/services/ai_service.py` | Low-level provider selection, real HTTP provider call, fallback loop |
| `backend/app/services/ai_routing_policy.py` | Typed provider/model/fallback policy per `task_type` |
| `backend/app/services/ai_prompt_registry.py` | Prompt templates, preferred provider, max_tokens, json_mode, prompt version |
| `backend/app/services/ai_prompts.py` | Prompt strings (`RECOGNITION_SYSTEM_PROMPT`, `RECOGNITION_SYSTEM_MESSAGE`) |
| `backend/app/services/ai_validator.py` | `validate_ai_output` + `SCHEMA_MAP` (CAPTURE_RECOGNITION -> `RecognitionOutput`) |
| `backend/app/services/ai_task_types.py` | `AiTaskType` enum (`CAPTURE_DRAFT`, `CAPTURE_RECOGNITION`) |
| `backend/app/services/ai_task_result.py` | `AiErrorCode` enum + internal `AiTaskResult` |
| `backend/app/schemas/ai_output.py` | `RecognitionOutput` schema (`{text: str}`) |
| `backend/app/models/ai_call_log.py` | `AiCallLog` model (table `ai_call_logs`) |
| `backend/app/services/ai_run_service.py` | `AiRun` records; input summary spec includes `capture_recognition` |

### Frontend — capture UI + client

| Path | Role |
|---|---|
| `src/app/manage/(workspace)/capture/page.tsx` | Route page `/manage/capture`; renders header + `CaptureContent` |
| `src/app/manage/(workspace)/capture/components/capture-content.tsx` | Mode selector (image / manual / mistake), lazy-mount + keep-alive |
| `src/app/manage/(workspace)/capture/components/capture-workspace.tsx` | Image capture workspace: upload, recognize, draft, edit, convert, error banner |
| `src/app/manage/(workspace)/capture/components/manual-question-entry.tsx` | Manual question entry mode (not OCR) |
| `src/app/manage/(workspace)/capture/components/mistake-draft-entry.tsx` | Mistake-draft-from-bank mode (not OCR) |
| `src/lib/api/captures.ts` | Typed capture API client (`Capture` DTO, all endpoints) |

### Committed capture tests found

| Path |
|---|
| `backend/tests/test_capture_service.py` |
| `backend/tests/test_i6_capture_failure_matrix.py` |
| `backend/tests/test_i6_capture_http.py` |
| `backend/tests/test_anon_capture_access.py` |
| `backend/tests/test_ai_gateway.py` (gateway-level, includes `call_vision` failure) |
| `backend/tests/test_ai_validator.py` (RecognitionOutput success + missing field) |
| `backend/tests/test_ai_prompt_registry.py` (`test_capture_recognition_has_user_content_template`) |
| `src/app/manage/(workspace)/capture/components/capture-content.test.tsx` |

---

## 2. Exception-handling map (file:line -> catch -> behavior)

### 2.1 `backend/app/services/capture_recognition.py` (OCR adapter)

| Lines | Guard / try | Behavior on failure |
|---|---|---|
| L46-51 | `if use_fake:` | Returns `success=True`, `recognized_text=fake_text`, `raw_output={"_fake": True}` |
| L53-59 | `if not image_bytes:` | Returns `success=False`, `error_code="empty_input"`, `error_message_safe="Image bytes are empty"` |
| L61-105 | main `try` for real call | (see rows below) |
| L77-81 | `if not gw.success:` | If gateway error contains `"no provider"`/`"not configured"` -> `raise ValueError(err)`, else `raise RuntimeError(err)` |
| L83-91 | `validate_ai_output` fails | Returns `success=False`, `error_code=validation.error_code`, echoes validator `error_message_safe` |
| L92-100 | empty recognized text | Returns `success=False`, `error_code="empty_result"` |
| L106-114 | `except ValueError` | `logger.warning("Recognition failed (no provider): %s", ...)`; returns `error_code="no_provider"`, `"No AI provider configured"` |
| L115-124 | `except RuntimeError` | `logger.warning("Recognition failed (provider error): ...")`; if `"timeout"`/`"timed out"` in message -> `error_code="timeout"` / `"Recognition timed out"`, else `error_code="provider_error"` / `"AI provider error"` |
| L125-133 | `except Exception` | `logger.warning("Recognition failed (unexpected): ...")`; returns `error_code="parse_error"`, `"Failed to parse recognition result"` |

Key fact: the adapter never raises to `capture_service`; all failures become a
`RecognitionResult` with an `error_code` string. There is **no exception-type-based
category enum** — categorization is by string sniffing (`"timeout"` substring) and by
which `except` block matches. There is **no** `AuthenticationError`, `ModelNotFoundError`,
`JSONDecodeError`, `ImageFetchError`, or `UnsupportedImageFormatError` handling.

### 2.2 `backend/app/services/capture_ai_draft.py` (draft adapter)

| Lines | Guard / except | Behavior |
|---|---|---|
| L67-73 | empty `recognized_text` | `error_code="empty_input"` |
| L84-88 | `if not gw.success:` | `ValueError` for no-provider, else `RuntimeError` |
| L90-104 | schema validation | returns `validation.error_code`; has a fallback re-normalization via `_validate_suggestion` |
| L105-112 | `except ValidationError` | `logger.warning("AI draft schema validation failed: ...")`; `error_code="schema_error"` |
| L113-120 | `except ValueError` | `error_code="no_provider"` |
| L121-132 | `except RuntimeError` | `error_code="timeout"` or `"provider_error"` (same substring test) |
| L133-141 | `except Exception` | `error_code="parse_error"` |

### 2.3 `backend/app/services/capture_service.py` (lifecycle)

| Lines | Behavior |
|---|---|
| L82-85 | `CaptureConflict("Attachment is not active")` / `CaptureValidationError("Attachment must be an image")` raised to router |
| L137-138 | `CaptureConflict(f"Cannot edit a {capture.status} capture")` |
| L184-185 | `CaptureConflict(f"Cannot recognize a {capture.status} capture")` |
| L196-208 | `try` reads attachment bytes; `except AttachmentNotFound` -> sets `status="failed"`, `error_code="attachment_missing"`, `error_message_safe="Source attachment not found"`, `finished_at`; **returns capture, does not raise** |
| L219-225 | Maps `RecognitionResult`: success -> `status="recognized"` + text; failure -> `status="failed"` + `result.error_code`/`error_message_safe` |
| L243-248 | `CaptureConflict` if draft not allowed from current status |
| L251-260 | Empty `recognized_text` in `trigger_draft` -> `status="failed"`, `error_code="empty_input"` |
| L284-297 | Maps `DraftResult`: success -> `status="ready"` + draft fields; failure -> `status="failed"` + `result.error_code`/`error_message_safe` |
| L325-345 | Convert guards: idempotent on `converted`; `CaptureConflict` for archived / not-ready |
| L377-392 | `except AttachmentConflict` on link -> only `logger.warning`, conversion continues |

### 2.4 `backend/app/services/ai_gateway.py` (gateway envelope)

| Lines | Behavior |
|---|---|
| L268-289 (`call_text`), L307-325 (`call_vision`), L344-363 (`call_general`), L388-408 (`call_stream`) | Each wraps `_call_with_fallback` in `try`, and `except Exception` (L283/L319/L357/L402) -> `_build_failure_result`; **never raises**; always calls `_write_call_log` then `_finish_run_record` |
| L191-202 | `_build_failure_result`: `data=None`, `provider_used=""`, `model=""`, `attempts=[]`, `error=str(exc)[:500]` |
| L74-101 | `_write_call_log`: independent session; on any exception only `logger.warning("AI call log write failed: ...")` |
| L131-174 | `_finish_run_record`: failure path stamps `error_code="provider_error"` / `error_message_safe=result.error or "AI provider call failed"`; any exception -> `logger.warning` |

### 2.5 `backend/app/services/ai_service.py` (lowest level)

| Lines | Behavior |
|---|---|
| L105-132 | `_call_provider`: real `httpx.AsyncClient(timeout=120)` POST; non-200 -> `raise RuntimeError(f"AI API error ({status_code}): {response.text}")` |
| L129-130 | **No per-status exception class** — auth (401/403), invalid model (404), quota (429) all collapse into one `RuntimeError` string |
| L135-147 | `_parse_json_response` / `_parse_text_response`: `KeyError`/`JSONDecodeError`/`IndexError` -> `RuntimeError("Failed to parse AI response: ...")` |
| L150-213 | `_call_with_fallback`: no provider -> `raise ValueError(...)` (L161); per-provider `except RuntimeError` (L184) computes `is_retryable` by substring `["429","500","502","503","504","timeout","ConnectError"]` (L187); `except Exception` (L200); final `raise RuntimeError("All AI providers failed. Trail: ...")` (L212-213) |

---

## 3. Provider call sites

| # | File:line | Function | What it does | Provider/model config source |
|---|---|---|---|---|
| 1 | `backend/app/services/capture_recognition.py:76` | `recognize_image` | `call_vision(AiTaskType.CAPTURE_RECOGNITION, messages)` — the OCR/vision call for image capture | resolved by gateway |
| 2 | `backend/app/services/ai_gateway.py:292-325` | `call_vision` | Vision gateway; `_resolve_registry_defaults(..., fallback_preferred="dashscope_vision")`; required caps `{"vision","json"}` | `ai_routing_policy` + `ai_prompt_registry` |
| 3 | `backend/app/services/ai_gateway.py:307-316` | `call_vision` inner | `_call_with_fallback(required_caps={"vision","json"}, preferred=<policy>, fallback_chain=<policy>)` | `resolve_routing_policy` |
| 4 | `backend/app/services/ai_routing_policy.py:111-119,134` | `_vision_policy` | CAPTURE_RECOGNITION: `primary_provider="dashscope_vision"`, `primary_model="qwen3.7-plus"`, `fallback_chain=("dashscope_vision","qwen_general")`, `require_json=True` | code constant |
| 5 | `backend/app/services/ai_routing_policy.py:59-65,84-90` | `PROVIDER_POLICIES` / `MODEL_POLICIES` | `dashscope_vision` capabilities `{vision,json}`, default model `qwen3.7-plus`, enabled by `DASHSCOPE_API_KEY` | code constant |
| 6 | `backend/app/services/ai_prompt_registry.py:81-91` | registry entry | `CAPTURE_RECOGNITION`: `version="v1"`, `system_prompt=RECOGNITION_SYSTEM_MESSAGE`, `output_schema_name="RecognitionOutput"`, `json_mode=True`, `preferred_provider="dashscope_vision"`, `max_tokens=4000`, `user_content_template=RECOGNITION_SYSTEM_PROMPT` | code constant |
| 7 | `backend/app/services/ai_prompts.py:63-73` | prompt strings | `RECOGNITION_SYSTEM_PROMPT` (JSON `{"text": ...}` instruction), `RECOGNITION_SYSTEM_MESSAGE` | code constant |
| 8 | `backend/app/services/ai_service.py:105-132` | `_call_provider` | **Only real outbound HTTP**: `POST {base_url}/chat/completions` with `Authorization: Bearer {key}` | provider dict from `_get_providers()` |
| 9 | `backend/app/services/ai_service.py:31-75` | `_get_providers` | Reads `DEEPSEEK_API_KEY`/`DEEPSEEK_BASE_URL`/`DEEPSEEK_MODEL`; `DASHSCOPE_API_KEY`/`DASHSCOPE_BASE_URL`/`DASHSCOPE_MODEL`; `AI_API_KEY`/`AI_BASE_URL`/`AI_MODEL` from settings | `app.config.get_settings()` |
| 10 | `backend/app/services/ai_service.py:216-229` | `call_ocr_model` | Legacy OCR wrapper, docstring "Internal — use ai_gateway.call_vision"; **not used by the capture path** (no caller in capture services) | hard-coded `preferred="dashscope_vision"` |

No `openai` / `anthropic` SDK import exists in `backend/app` (only raw `httpx` against
OpenAI-compatible `/chat/completions`). No `providers/` package directory exists.

---

## 4. Current success/failure response DTO fields

### `CaptureOut` (`backend/app/schemas/capture.py:132-155`)

`id`, `source_attachment_id`, `status`, `recognized_text`, `user_error_context`,
`question_draft_text`, `analysis_draft_text`, `error_summary_draft`, `subject_id`,
`knowledge_point_suggestions`, `model_output_version`, `attempt_count`, `last_stage`,
`error_code`, `error_message_safe`, `started_at`, `finished_at`, `mistake_draft_item_id`,
`created_by`, `created_at`, `updated_at`.

**There is no `failure_category` field.** Failure info is carried by `error_code`
(string, e.g. `empty_input`/`no_provider`/`timeout`/`provider_error`/`schema_error`/
`parse_error`/`empty_result`/`attachment_missing`) and `error_message_safe`.

- `CaptureStatus` Literal: `uploaded, recognizing, recognized, drafting, ready, failed, converted, archived` (`capture.py:8-17`)
- `CaptureLastStage` Literal: `recognize, draft, convert` (`capture.py:18`)
- `ConvertResultOut`: `capture`, `mistake_draft_item_id`, `question_draft_id` (`capture.py:158-163`)
- Internal adapter result dataclasses: `RecognitionResult(recognized_text, success, error_code, error_message_safe, raw_output)` (`capture_recognition.py:22-30`); `DraftResult(suggestion, success, error_code, error_message_safe)` (`capture_ai_draft.py:27-34`)
- AI output schema for recognition: `RecognitionOutput{text: str}` (`backend/app/schemas/ai_output.py:18-25`)
- Existing error-code vocabulary: `AiErrorCode` (`backend/app/services/ai_task_result.py:18-31`): `empty_input, no_provider, timeout, provider_error, schema_error, parse_error, empty_result`

### Frontend client mirror

`src/lib/api/captures.ts` mirrors the DTO exactly: `Capture` interface L29-51
(including `error_code`, `error_message_safe` at L43-44), `CaptureStatus` L5-13,
`CaptureLastStage` L15, plus `listCaptures`/`createCapture`/`getCapture`/
`patchCapture`/`triggerRecognition`/`triggerDraft`/`convertCapture` L96-137.

---

## 5. Frontend state handling (file:line)

| Concern | Location |
|---|---|
| Loading state (list/detail) | `capture-workspace.tsx:80` `loading`; render L219-225 |
| Busy status (recognizing/drafting) | `capture-workspace.tsx:61-63` `isBusy`; spinner in list L352-354, header L431-433 |
| Recognize success/failure toast | `capture-workspace.tsx:161-174` (`updated.status === 'recognized'` -> success toast; `'failed'` -> error toast) |
| Draft success/failure toast | `capture-workspace.tsx:176-189` |
| Upload error toast | `capture-workspace.tsx:144-149` |
| Error banner rendering | `capture-workspace.tsx:386-388` and `ErrorBanner` L488-495 — shown only when `status === 'failed' && error_message_safe` |
| Empty state | `capture-workspace.tsx:235-236`, `EmptyState` L317-324 ("还没有采集项…") — this is the **no-captures** empty, not an OCR empty-success |
| Retry (re-recognize) | `capture-workspace.tsx:695-734` `ActionButtons`: same "重新识别" button re-calls `onRecognize` (L713-722); label switches based on `capture.status === 'uploaded'` |
| Attempt count display | `capture-workspace.tsx:435-439` "(第 N 次)" |
| Error category shown to user | No — only `error_message_safe` string; `error_code` is never rendered |
| Empty vs error distinction | **Does not exist in UI.** OCR empty (`empty_result`) and provider error both render as the same red `ErrorBanner` driven by `status === 'failed'`. There is no dedicated "no content extracted" success-like state. |

Notes:
- The only loading UI is status-driven (`recognizing` -> spinner); the recognize
  button is synchronous (awaits the POST), so there is no separate "Processing image..."
  text state.
- `Retry` exists functionally (button always allows re-recognition except converted/
  archived), but is not gated by failure category and there is no retry-limit/loop guard.
- `error_code` reaches the client in the DTO but is not consumed anywhere in the capture UI.

---

## 6. Existing tests touching capture / OCR

Backend (committed):
- `backend/tests/test_i6_capture_failure_matrix.py`
  - L60-74 `test_missing_attachment_stays_failed_without_downstream_objects` (expects `error_code="attachment_missing"`)
  - L76-87 `test_empty_recognized_text_stays_failed_without_draft` (`empty_input`)
  - L91-100 `test_timeout_is_mapped_to_safe_error` (`error_code="timeout"`, message "Recognition timed out")
  - L102-123 `test_provider_failure_result_is_mapped_without_raw_error` (`provider_error`; asserts no "secret" leaks)
  - L125-146 `test_draft_schema_failure_does_not_become_empty_success` (`schema_error`)
- `backend/tests/test_capture_service.py` — fake-adapter success, zero-pollution on failure, idempotent convert, manual path (`test_recognition_with_fake_succeeds` L111, `test_recognition_failure_zero_pollution` L201, `test_draft_failure_zero_pollution` L217)
- `backend/tests/test_i6_capture_http.py` — admin upload + create capture (L96-99), invalid upload rejected (L120-123)
- `backend/tests/test_anon_capture_access.py` — all `/api/admin/captures*` endpoints return 401/403 (L25-39)
- `backend/tests/test_ai_gateway.py` — `test_call_vision_failure_writes_log` L219, `test_call_text_failure_returns_error_result` L193, `test_build_failure_result_truncates_error` L402
- `backend/tests/test_ai_validator.py` — `test_recognition_success` L56, `test_recognition_missing_field` L66
- `backend/tests/test_ai_prompt_registry.py` — `test_capture_recognition_has_user_content_template` L51

Frontend (committed):
- `src/app/manage/(workspace)/capture/components/capture-content.test.tsx` — mode switching / lazy-mount / state preservation only. **It does not test loading/success/error/empty/retry OCR states** (the workspace is mocked at L8-10).

None of the tests assert a `failure_category` field or an exception-type taxonomy;
they assert the existing `error_code` strings.

---

## 7. DELTAS vs week4 task assumptions

Preflight found the following concrete mismatches between `tasks/pr-14.md` / `tasks/w4-00.md`
text and the verified current source. None of these are speculative.

| # | Week4 plan assumption | Verified reality | Evidence |
|---|---|---|---|
| D1 | `backend/app/services/capture_recognition_service.py` exists and is where OCR calls are wrapped | File **does not exist**. The OCR adapter is `backend/app/services/capture_recognition.py`; there is a separate `capture_service.py` orchestrator | `glob`/`ls`; `capture_recognition.py:1-133` |
| D2 | Add a `CaptureRecognition` model with `failure_category` nullable VARCHAR | No `CaptureRecognition` class anywhere. The persistence model is `CaptureItem` (`backend/app/models/capture.py:21`), table `capture_items`; it has `error_code` (`String(50)`) and `error_message_safe` (`String(300)`) but **no `failure_category`** | `models/capture.py:59-60`; grep for `class CaptureRecognition` -> NONE |
| D3 | Define `CaptureFailureCategory(str, Enum)` in `backend/app/schemas/capture.py` | Not present. `capture.py` has no enum for failures; failure vocabulary lives as strings in `capture_recognition.py` and in `AiErrorCode` (`ai_task_result.py:18-31`) | grep `CaptureFailureCategory` -> NONE |
| D4 | Add `failure_category` optional field to `CaptureOut` | Not present; `CaptureOut` uses `error_code` + `error_message_safe` only | `schemas/capture.py:146-147`; frontend mirror `captures.ts:43-44` |
| D5 | Map `AuthenticationError`/`ModelNotFoundError`/`JSONDecodeError`/`ImageFetchError`/`UnsupportedImageFormatError` to categories | These exception classes do not exist. `ai_service._call_provider` raises a single generic `RuntimeError("AI API error ({status}): …")`; JSON parse failure raises generic `RuntimeError`; attachment-missing is handled as `AttachmentNotFound` -> `error_code="attachment_missing"`. Category inference is substring-based (`"timeout"`), not type-based | `ai_service.py:129-130,139-147`; `capture_recognition.py:106-133` |
| D6 | UI lives at `src/app/capture/` | Actual route is `src/app/manage/(workspace)/capture/` (`page.tsx` + `components/`). `src/app/capture/` does not exist | `src/app/manage/(workspace)/capture/page.tsx:1-15`; `ls src/app/capture` -> NONE |
| D7 | 4 UI states Loading/Success/Error/Empty, with Empty distinct from Error | UI is status-driven: `recognizing`/`drafting` spinner, terminal `failed` -> single `ErrorBanner(message=error_message_safe)`, ready/converted success. No distinct empty-result state; `empty_result` collapses into the same failed banner. `error_code` is never rendered | `capture-workspace.tsx:61-63, 386-388, 488-495, 695-734` |
| D8 | Retry increments attempt count and is logged for analysis | `attempt_count` is incremented server-side on every `trigger_recognition` (`capture_service.py:190`) and re-recognition is allowed, so the button does re-attempt. But there is **no frontend retry-limit guard**, no category-aware retry, and no explicit "retry" telemetry beyond the existing gateway log | `capture_recognition`/`capture_service.py:187-190`; `ai_call_log.py:20-37` |
| D9 | Tests: `backend/tests/test_ocr_baseline.py`, `backend/tests/test_capture_taxonomy.py`, `src/app/capture/capture.test.tsx` | None exist. Current capture tests are the six files in §6; the frontend test only covers mode switching | `ls` -> NONE for all three |
| D10 | Failure logging with category, capture_id, sanitized message | Gateway logs to `ai_call_logs` with `task_type`, `provider_used`, `model`, `latency_ms`, `success`, `error` (truncated 500), `fallback_used`, `attempts`, `input_summary` (200), `prompt_version` — but **no `capture_id` and no category column**. Adapter logs are single `logger.warning` lines with truncated `str(e)[:200]` and no capture_id | `ai_gateway.py:74-101`; `models/ai_call_log.py:20-37`; `capture_recognition.py:108,118,127` |
| D11 | "Success/failure instrumentation" / counts | No aggregate success/failure counters. Per-call rows exist in `ai_call_logs`; there is an `ai_provider_health_snapshot` test (`backend/tests/test_ai_provider_health_snapshot.py`) but it is gateway/provider-level, not capture-level | `ai_call_log.py:39-43`; test filename |
| D12 | Failure mapping currently covers "provider errors, schema validation, image format, unknown" | Current observed categories are only: `empty_input`, `no_provider`, `timeout`, `provider_error`, `schema_error`, `parse_error`, `empty_result`, `attachment_missing`. There is **no image-format category** and no explicit `unknown` bucket label | `ai_task_result.py:18-31`; `capture_service.py:203,253` |

### Deltas confirmed absent (greps returned no matches)
- `failure_category`, `CaptureFailureCategory` — none in `backend/` or `src/`
- `capture_recognition_service.py` — does not exist
- `class CaptureRecognition` — does not exist
- `src/app/capture/` — does not exist
- `backend/tests/test_ocr_baseline.py`, `backend/tests/test_capture_taxonomy.py`, `src/app/capture/capture.test.tsx` — do not exist

### Most important mismatch
The plan's central instrumentation target is fictional: **there is no
`capture_recognition_service.py` and no `CaptureRecognition` model.** The real OCR path is
`capture_recognition.recognize_image` -> `ai_gateway.call_vision` -> `ai_service._call_with_fallback`
-> `ai_service._call_provider`, persisting to `CaptureItem` (error string fields already
present) and `ai_call_logs` (no `capture_id`, no category). The second material delta is
that a partial failure vocabulary already exists as `error_code` strings / `AiErrorCode`,
so PR-14 must extend an existing taxonomy rather than introduce the first one — and any
new `failure_category` requires a schema + model/migration change (risk upgrade), which
the current plan does not reconcile with the existing `error_code` column.

---

## 8. Verification / status

- Method: read-only file reads, `glob`, `grep`, `ls`. No file was created or modified
  other than this evidence file. No migration, no DB read/write, no git write.
- Result: `PARTIAL` — inventory complete for the current source; the plan's assumed
  architecture is contradicted by reality as itemized in §7. No runtime/DB execution was
  performed, so actual provider success rate is `NOT_VERIFIED`.
- Worktree at time of inventory: `refactor/baseline`, dirty (many pre-existing modified
  and untracked files unrelated to this task); none were touched.
