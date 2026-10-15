# Design: AI Mistake And Prompt Management Upgrade

## Overview

This is one combined AI learning upgrade with three cooperating parts:

1. Capture the learner's mistake context.
2. Analyze the problem, including image content, answer, explanation, and visual context.
3. Route AI calls through a reliable provider/fallback layer that can be inspected and tested in `/manage?tab=ai`.

## Model Registry

Use `qwen3.7-plus` as the general Qwen model and fallback target:

Do not use `qwen3.7-max` as the combined fallback in this workflow. Runtime validation showed text calls work, but image input fails with HTTP 400 in the current DashScope OpenAI-compatible path, so it cannot replace the multimodal fallback role.

```text
general_qwen:
  provider: dashscope
  model: qwen3.7-plus
  base_url: DASHSCOPE_BASE_URL
  key: DASHSCOPE_API_KEY or AI_API_KEY
  capabilities: text, vision, json

deepseek_text:
  provider: deepseek
  model: DEEPSEEK_MODEL
  base_url: DEEPSEEK_BASE_URL
  key: DEEPSEEK_API_KEY
  capabilities: text, json

dashscope_vision:
  provider: dashscope
  model: DASHSCOPE_MODEL
  base_url: DASHSCOPE_BASE_URL
  key: DASHSCOPE_API_KEY
  capabilities: vision, json
```

Recommended route mapping:

| Use case | Primary | Fallback |
|----------|---------|----------|
| general AI | `general_qwen` | none |
| text JSON | `deepseek_text` | `general_qwen` |
| text stream polish | `deepseek_text` | `general_qwen` |
| OCR/vision JSON | `dashscope_vision` | `general_qwen` |
| recommendations | `general_qwen` | `deepseek_text` if configured |

Fallback should activate on connection errors, timeouts, HTTP 429, HTTP 5xx, provider auth/model errors when fallback credentials exist, and malformed JSON when the route requires strict JSON.

## Frontend Design

### Write-Mistake Form

Current form state keeps `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, and `user_error_analysis`.

Proposed UI changes:

- Rename visible copy for `my_answer` from "我的错误答案" to "我的错误思路 / 当时答案".
- Promote `user_error_analysis` into the first learner-context cluster.
- Move or reframe the AI analysis card so the user sees the context fields before pressing AI buttons, or add a clear generic-analysis warning when context is empty.
- Keep `my_answer` as the API/database field for compatibility, but update labels and generated markdown headings.

### Visual Context

Use existing `images` as the source of truth for original uploaded visuals.

Add response metadata under `ai_metadata`:

- `visual_context`: concise description of what the image/diagram shows.
- `image_dependency`: boolean or string flag indicating whether the problem depends on the visual.

The mistake detail page should display this near the question or analysis when present.

### AI Management Prompt Lab

Replace the current static AI tab with a compact operational UI:

- Provider status band:
  - Qwen3.7 Plus, DashScope vision, DeepSeek text.
  - configured, unconfigured, last health check, latency, error summary.
- Prompt workspace:
  - left: prompt template list by feature.
  - center: editable prompt textarea with reset button.
  - right: test panel with input, mode, model route, and output.
- Test result panel:
  - provider used;
  - fallback provider used if any;
  - latency;
  - raw/summarized output;
  - error trail.

Initial persistence recommendation: draft editing and testing first; add saved prompt overrides only if explicitly kept in approved scope.

## Backend Design

### Prompt Split

The existing OCR prompt is too conservative for the write-mistake flow. Keep OCR discipline, but add a solving step contract:

- First: extract visible question and visual context.
- Then: if enough information exists, solve and explain.
- If information is insufficient, return specific missing requirements.
- Never use uncertain OCR wording as a bridge to a final answer. If a value is unclear or conflicts with the derivation, the model must mark the item insufficient instead of writing "可能" and continuing.

### Deterministic Analysis Guard

The backend should add a lightweight post-processing guard for final AI text:

- Detect hedge words such as "可能", "也许", "似乎", "大概", "推测" in answer/analysis fields.
- Allow them only in explicit OCR uncertainty or missing-information notes.
- If hedge words appear in final reasoning, either ask the model to regenerate once with stricter instructions or return a clear insufficient-information message.
- For calculation-heavy questions, prompt rules should require showing consistent intermediate values rather than reconciling conflicting numbers with speculation.

### Personalized Context Builder

The same personal-context text is duplicated in image/text sync and stream endpoints. A helper should build it consistently:

- wrong thought / user's answer;
- correct answer if already known;
- user's self-identified error point;
- instruction to write `personalized_diagnosis`, `misread_signal`, and `next_time_checklist`.

### Prompt Registry

Expose backend prompt templates by feature:

- `mistake.ocr`
- `mistake.text_analysis`
- `mistake.variant`
- `mistake.knowledge_card`
- `polish.polish`
- `polish.summarize`
- `polish.tags`
- `knowledge.summary`
- `recommendation.daily`

## Data Compatibility

No schema migration is planned. Existing records without visual metadata render normally.

The existing `my_answer` backend field remains the persisted field. The product copy may call it "错误思路 / 当时答案" while the internal field remains stable.

## Daily Music Design

Treat daily music as a data-generation workflow, not as a public API connectivity issue.

Current production evidence means:

- API and DB are healthy.
- Today's song is missing.
- Public history is empty.

Repair design:

- Frontend manage actions must use typed API helpers and configured API base, not relative `/api/...` fetches.
- Backend should expose or reuse diagnostics that distinguish:
  - daily song exists / missing;
  - candidate pool count;
  - NetEase API configured / reachable;
  - last sync/generation result.
- Generation policy must be explicit:
  - manual admin generation is required for this phase at minimum;
  - scheduler/cron can be added only if it stays within approved scope and can be validated.
- If candidate pool is empty, generation should return a clear actionable response instead of an opaque `null`.

## Risks

- Prompt changes may over-solve uncertain images. Mitigation: require explicit uncertainty and missing-info text.
- Mermaid validation can be expensive or browser-dependent. Mitigation: fail closed with safe fallback.
- Moving AI controls may disrupt existing quick-upload habit. Mitigation: keep upload available but make generic-vs-personalized state clear.
- Fallback can hide primary provider outages. Mitigation: expose provider attempt trail in logs and management test results.
- Music generation can still fail if NetEase API is not deployed in production. Mitigation: surface candidate-pool and NetEase reachability status in admin-facing diagnostics.
