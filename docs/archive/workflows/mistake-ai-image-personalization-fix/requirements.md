# Requirements: AI Mistake And Prompt Management Upgrade

## Functional Requirements

### REQ-01: Collect learner context before generation

The write-mistake page must make it natural to enter the learner's mistaken thinking before AI generation. AI calls must include this context when present.

Acceptance:

- The primary red/orange learner field is worded as wrong thought/error thinking, not only "wrong answer".
- Upload and text analysis controls clearly sit after, or are gated by, the relevant learner-context inputs.
- If the user starts AI generation without personal context, the UI must either warn them or mark the result as generic.

### REQ-02: Preserve backwards-compatible data contracts

Existing saved mistakes and backend contracts must continue to work.

Acceptance:

- Existing `my_answer` records still render.
- Frontend API types remain synchronized with backend Pydantic schemas.
- No migration is required unless a new first-class persisted field is intentionally introduced and documented.

### REQ-03: Generate explanations for image-only questions

The image-analysis flow must not stop at OCR when the image lacks visible answer or explanation. It should produce a solved answer and analysis when the visible question is sufficient.

Acceptance:

- Uploading a clear question image without visible answer can produce `correct_answer` and `analysis`.
- If the image is insufficient, the analysis must say what is missing and ask for specific补充信息.
- OCR uncertainty must remain visible and not be presented as certain facts.

### REQ-04: Preserve visual context for image-dependent questions

Image-based questions must retain enough visual context for later review.

Acceptance:

- Saved mistake records keep uploaded images.
- AI output includes a concise visual-context summary when the question depends on a figure, diagram, topology, geometry, or screenshot.
- The detail page makes the original image and visual-context summary discoverable near the question/analysis.

### REQ-05: Generated analysis must be deterministic and self-consistent

AI analysis must not use uncertain wording to bridge a reasoning gap. Words such as "可能", "也许", "似乎", "大概", "推测" are allowed only in OCR uncertainty or missing-information notes, not as the basis for a final answer.

Acceptance:

- Final `correct_answer`, `analysis`, `error_reason`, and `key_step` must be written as determinate reasoning when the problem is solvable.
- If the model cannot determine a value because the image/text is ambiguous, it must state that the information is insufficient and list the missing or uncertain condition.
- The model must not say "图中显示为 X，可能因 Y" and then treat that uncertain explanation as the final derivation.
- For arithmetic/protocol problems, intermediate values must be internally consistent. If two values conflict, the output must flag the conflict instead of forcing an answer.

### REQ-06: Mermaid errors must not break the upload page

Invalid generated Mermaid must fail quietly inside its own block.

Acceptance:

- `/write-mistake` must not show a large Mermaid `Syntax error in text` overlay.
- Invalid Mermaid is either hidden behind a safe fallback or shown as plain code inside the expected diagram card.
- Browser console warnings are acceptable only if the user-facing UI remains clean.

### REQ-07: Use Qwen3.7 Plus as the general model

The general-purpose AI model must default to DashScope `qwen3.7-plus`.

Acceptance:

- Backend config defaults `AI_MODEL` to `qwen3.7-plus`.
- General AI calls use DashScope-compatible base URL and configured DashScope/API key unless explicitly overridden.
- `/manage?tab=ai` displays "Qwen3.7 Plus" / `qwen3.7-plus` as configured when the key is present.
- Runtime configuration must not keep reporting `gpt-4o` when `AI_API_KEY` is empty and `DASHSCOPE_API_KEY` is configured; `.env.example` and runtime behavior must make the effective general route clear.

### REQ-08: Add automatic fallback to Qwen3.7 Plus

Independent text and OCR paths must fall back to `qwen3.7-plus` when their primary provider is unavailable.

Acceptance:

- DeepSeek text failures can fall back to Qwen `qwen3.7-plus`.
- DashScope vision primary failures can fall back to Qwen `qwen3.7-plus`.
- Fallback triggers on connection errors, timeout, 5xx, 429, and provider auth/model errors where a fallback key is available.
- Fallback does not hide total failure: final errors report which providers were attempted.
- Audit/log output records primary vs fallback provider without logging secrets.

### REQ-09: Build a visual prompt management UI

`/manage?tab=ai` must become a practical prompt lab rather than a static status page.

Acceptance:

- Shows provider cards with health, model ID, base URL label, role, and last test result.
- Shows prompt templates grouped by feature, for example mistake OCR, mistake text analysis, polish, tags, knowledge summary, recommendation.
- Allows selecting a prompt template, editing draft text locally, and testing it with sample input.
- Test results show provider used, fallback used or not, latency, status, and output.
- Editing must not expose API keys.

### REQ-10: Prompt persistence must be explicit and safe

Prompt editing must have a clear persistence model.

Acceptance:

- Initial implementation may use backend static prompt registry plus draft UI, or persisted backend prompts if scoped and documented.
- If persistence is implemented, it must require admin auth and must not write secrets.
- There must be a reset-to-default path for editable prompts.

### REQ-11: Repair daily music generation and admin recovery path

Daily music must distinguish API reachability from data-generation health and provide a reliable admin recovery flow.

Acceptance:

- Public health being `200` must not be treated as proof that daily music data exists.
- Empty `daily-song/public` and empty `history/public` are reported as "data not generated / no history", not as CORS/tunnel failure.
- Backend must have an explicit generation/backfill path, and the design must state whether it is scheduled, request-triggered, or manually triggered.
- Candidate-pool status must be visible enough for admin diagnosis.
- If NetEase API is missing/unreachable, the admin UI or backend response must show that as the owning failure.

### REQ-12: Fix manage music API origin usage

Management music actions must call the configured backend API origin, not the frontend origin.

Acceptance:

- `src/app/manage/music-tab.tsx` must not call `fetch('/api/music/manage/generate-song')` directly.
- The "生成今日歌曲" action must use the existing typed API wrapper such as `generateDailySong()` / `apiFetch()`.
- Production `blog.limengyang.me` must not route this action to a frontend 404.

### REQ-13: Scope and architecture boundaries

The change must stay within `mistakes`, `notes`, `manage`, `music`, shared Mermaid rendering, and backend AI/music prompt/API/model-routing code.

Acceptance:

- No unrelated blog/home refactors.
- Frontend still follows `component -> src/lib/api -> backend API`.
- Shared model routing lives in backend services, not React components.
- Existing public routes must not expose prompt editing or provider health details.
- Backend routers remain thin; large prompt/normalization helpers should be moved into services when they grow.

## Validation Requirements

- Verify `qwen3.7-plus` runtime call with current DashScope key.
- Frontend TypeScript changes: run `npx tsc --noEmit`.
- Frontend build-sensitive changes: run `npm run build`.
- Backend AI/schema/service changes: run backend import checks for AI services and routers.
- UI changes: inspect `/write-mistake` in a browser and confirm no Mermaid syntax overlay.
- Browser-check `/manage?tab=ai` prompt test UI.
- Verify daily music public endpoints and admin generation path after changes.
- If possible, test with an image-only mistake sample and record whether answer/analysis are generated or why the model refused.
