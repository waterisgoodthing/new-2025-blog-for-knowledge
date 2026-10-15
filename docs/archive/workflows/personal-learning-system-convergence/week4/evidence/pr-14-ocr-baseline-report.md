# PR-14 — OCR Baseline Report

Status: `PARTIAL` (taxonomy + UI verified locally; **real-provider success rate = `NOT_VERIFIED`**)
Date: 2026-09-26
Repo: `/Users/limengyang/2025-blog-public`
Scope: `backend/app/services/capture_failure_taxonomy.py`, `capture_recognition.py`,
`capture_service.py`, `backend/app/schemas/capture.py`, `src/lib/api/captures.ts`,
`capture-workspace.tsx`, plus PR-14 tests. No migration, no DB column, no `blog_db`/`blog_v2` write.

---

## 1. Method

The 10-sample baseline is executed through the **deterministic local recognition path**
(`capture_recognition.recognize_image`) with an injected `call_vision` mock and the existing
`use_fake` adapter. It does **not** call a real provider.

- Harness: `backend/tests/test_ocr_baseline.py` (10 fixed cases, assertions on
  `(success, error_code, failure_category)`).
- Categories come from the derived taxonomy in
  `backend/app/services/capture_failure_taxonomy.py` (mapping over the existing `error_code`
  vocabulary), **not** from a new persisted column.
- No provider credentials are configured in this environment, and external provider calls are
  outside the authorized local-only scope (W4-E02). Therefore a real-provider measurement was
  **not** performed and the **real-provider success rate is `NOT_VERIFIED`**. The `1/10`
  success below is a harness property, not a product success rate.

## 2. Per-sample outcomes (local deterministic)

Two derivations are reported separately:

- **pre-DTO `error_code`** — the value persisted on `capture_items.error_code` and returned by
  the recognition/draft adapter (`RecognitionResult.error_code` / `DraftResult.error_code`).
- **DTO-serialized `failure_category`** — the `CaptureOut` computed field, derived from the
  persisted `error_code` via `capture_failure_taxonomy.categorize_failure()`. It is **not** a
  persisted column. For failed rows the mapping is: `provider_auth`→`provider_auth`,
  `invalid_model`→`invalid_model`, `timeout`→`provider_timeout`, `no_provider`→`provider_auth`,
  generic `provider_error`→`unknown`.

For these samples the adapter category and the DTO category agree, because the specific error
codes now map to their own categories.

| # | Sample | success | pre-DTO error_code | DTO-serialized failure_category | Category label (zh-CN) |
|---|--------|---------|--------------------|---------------------------------|------------------------|
| 1 | fake_success | `True` | `None` | `None` | — (识别成功) |
| 2 | empty_input (empty bytes) | `False` | `empty_input` | `image_fetch` | 图片读取失败 |
| 3 | no_provider | `False` | `no_provider` | `provider_auth` | AI 服务未授权或额度不足 |
| 4 | timeout | `False` | `timeout` | `provider_timeout` | AI 服务超时 |
| 5 | auth_401 (provider message sniff) | `False` | `provider_auth` | `provider_auth` | AI 服务未授权或额度不足 |
| 6 | invalid_model_404 | `False` | `invalid_model` | `invalid_model` | 模型不可用 |
| 7 | provider_error_unknown (generic) | `False` | `provider_error` | `unknown` | 未知错误 |
| 8 | schema_error | `False` | `schema_error` | `schema_validation` | 识别结果格式不符 |
| 9 | empty_result | `False` | `empty_result` | `invalid_response` | 识别结果无效 |
| 10 | parse_error | `False` | `parse_error` | `invalid_response` | 识别结果无效 |

Aggregate: **10/10 samples classified** (success or a non-null category);
**1 success**, 9 failures. This is a deterministic local baseline only.

DTO derivation is asserted directly in
`backend/tests/test_capture_taxonomy.py::DtoFailureCategorySerializationTest`:
`error_code='provider_auth'`→`provider_auth`, `invalid_model`→`invalid_model`,
`timeout`→`provider_timeout`, generic `provider_error`→`unknown`, and non-`failed`
statuses serialize `null`.

## 3. Real-provider rate

**`NOT_VERIFIED`.** No real provider request was made. Do not read the local 1/10 figure as a
provider success rate. Any real rate claim requires a separately authorized provider run.

## 4. Entry-point decision

Decision: **do not disable and do not add a warning label to the Capture entry.**

Rationale:
- The only unavailable measurement is the real-provider success rate (environment has no
  provider credentials; external calls are out of scope). An unverified number is not evidence
  for a user-visible product change such as disabling capture — that would be scope creep.
- The verified parts (error taxonomy, derived DTO category, distinct empty-result UI, working
  retry) already improve diagnosis without removing a working capability.
- The Week 4 gate records OCR baseline as `PARTIAL` (taxonomy + UI verified; real success rate
  unverified) with this honest disclosure (W4-E02), rather than a fabricated `PASS`.

## 5. Evidence / verification

- `backend/tests/test_ocr_baseline.py` — 10-sample local harness.
- `backend/tests/test_capture_taxonomy.py` — mapping + provider-error sniffing + detail-free log
  assertions + `CaptureOut.failure_category` serialization.
- `docs/workflows/personal-learning-system-convergence/week4/evidence/pr-14-logs-sample.txt` —
  detail-free sample category log lines (category / code / capture_id only).
- Commands and results are recorded in the PR-14 handoff report (backend pytest, capture vitest,
  `tsc --noEmit`).
