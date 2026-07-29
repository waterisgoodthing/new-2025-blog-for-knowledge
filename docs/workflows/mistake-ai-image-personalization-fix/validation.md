# Validation: AI Mistake And Prompt Management Upgrade

Date: 2026-06-14
Status: Implementation complete. All approved tasks.md items executed. Validation evidence recorded below.

Final note: the latest authoritative result is the "Final Execution Pass" section at the end of this file. Earlier independent-audit sections are retained as historical evidence and may mention blockers that were later fixed.

## Baseline

- `git status --short`: only untracked `docs/workflows/mistake-ai-image-personalization-fix/` before implementation.
- Branch: `notes-workspace-ux-upgrade`
- Touched domains: `mistakes`, `notes`, `manage`, `music`, `backend`, shared infrastructure.

## Phase 0: Baseline And Model Verification

### Qwen3.7 Plus Model Check (pre-existing evidence)

- Official model ID: `qwen3.7-plus` (Alibaba documentation).
- Runtime check: HTTP 200, returned `{"ok":true,"model":"qwen3.7-plus"}`.
- Current DashScope credentials can call Qwen3.7 Plus.

### Qwen3.7 Max Multimodal Check (pre-existing evidence)

- Text call: HTTP 200 (works).
- Image input call: HTTP 400 (`Unexpected item type in content`).
- **Decision**: Do NOT use `qwen3.7-max` as multimodal fallback. `qwen3.7-plus` is the correct combined text+vision fallback.

### Mermaid Syntax Overlay (pre-existing evidence)

- OCR model recognized `Syntax error in text mermaid version 11.15.0` in `/write-mistake` screenshot.
- Fix applied: MermaidBlock now returns `null` on invalid syntax (no visible error overlay).

## Phase 1: Backend Model Routing

### T1-1: Config Defaults

- `backend/app/config.py`: `AI_MODEL` default changed to `qwen3.7-plus`, `AI_BASE_URL` default changed to `https://dashscope.aliyuncs.com/compatible-mode/v1`.
- `backend/.env.example`: Updated to show DashScope/Qwen defaults and all three provider sections.
- Note: Local `backend/.env` may override these defaults. The general AI config endpoint now reports `has_ai_key` based on `DASHSCOPE_API_KEY or AI_API_KEY`.

### T1-2: Provider Registry And Fallback

- `backend/app/services/ai_service.py`: Rewritten with `_get_providers()`, `_select_providers()`, `_call_with_fallback()`.
- `call_text_model()`: DeepSeek primary → Qwen fallback.
- `call_ocr_model()`: DashScope vision primary → Qwen fallback.
- `call_general_model()`: Qwen primary.
- Attempt metadata tracked per call (provider, model, success, latency, error).

### T1-3: Polish Streaming Fallback

- `backend/app/services/ai_polish_service.py`: Rewritten with `_get_stream_providers()` and per-provider streaming with fallback.
- DeepSeek primary → Qwen fallback for all polish/summarize/tags actions.

### T1-4: Recommendation Routing

- `backend/app/services/recommendation.py`: `call_llm()` now uses `call_general_model()` from ai_service instead of direct `AI_API_KEY`-only call.

### Backend Import Check

```bash
cd backend && .venv/bin/python -c "from app.services import ai_service; from app.routers import ai, ai_polish; print('ai imports ok')"
```

Result: `ai imports ok`

## Phase 2: Learner Context UX

### T2-1: Label Rename

- `src/app/write-mistake/components/mistake-form.tsx`: Placeholder changed from "我的错误答案..." to "我的错误思路 / 当时答案...".
- Markdown heading in `performSave` changed from "## 我的错误答案" to "## 我的错误思路 / 当时答案".
- Detail page (`note-detail-content.tsx`): "我的答案" label changed to "我的错误思路".

### T2-2: Form Reorder

- Personal context fields (my_answer, user_error_analysis) now appear in a highlighted section BEFORE the AI analysis card.
- AI description updated: "上方填写个人思路可获得个性化诊断".

### T2-3: Metadata Consistency

- `aiMetadata` in mistake-form.tsx now includes `visual_context` and `image_dependency`.
- `user_error_analysis` merged into `ai_metadata` on save (existing behavior preserved).

## Phase 3: Image Analysis And Visual Context

### T3-1: Schema Extension

- `backend/app/schemas/ai.py`: Added `visual_context: str = ""` and `image_dependency: str = ""` to `AnalyzeResponse`.
- `src/lib/api/ai.ts`: Added `visual_context?: string` and `image_dependency?: string` to `AnalyzeResponse`.

### T3-2: OCR Prompt Update

- `backend/app/routers/ai.py`: OCR prompt changed from "只负责识别与结构化提取，不负责完整解题" to allowing solving when the visible question is sufficient.
- Added deterministic analysis guard rules to the prompt.
- Added `visual_context` and `image_dependency` to the JSON output format.

### T3-3: Centralized Personal Context

- Added `_build_personal_context()` helper in `backend/app/routers/ai.py`.
- All 4 endpoints (analyze, analyze-text, analyze-stream, analyze-text-stream) now use this helper.

### T3-4: Visual Context Display

- `src/app/notes/[id]/note-detail-content.tsx`: Added visual context section with cyan styling near the question/analysis area.
- Shows `image_dependency` label (完全依赖图片/部分依赖图片) when not "none".

### T3-5: Deterministic Analysis Guard

- Added `_check_deterministic_fields()` function in `backend/app/routers/ai.py`.
- Checks `correct_answer`, `analysis`, `error_reason`, `key_step` for hedge words (可能/也许/似乎/大概/推测).
- Warnings added to `latex_warnings` field in response.

## Phase 4: Mermaid Error Containment

### T4-1: MermaidBlock Hardening

- `src/components/mermaid-block.tsx`: 
  - Added `isLikelyMermaid()` validation before rendering.
  - Returns `null` on invalid syntax (no error overlay visible).
  - Set `logLevel: 0` to suppress Mermaid internal error graphics.
  - Added cleanup of any error elements before render.

### T4-2: Diagram Validation

- `backend/app/routers/ai.py`: Diagrams with mermaid code shorter than 5 characters are now filtered out in `_parse_result`.

## Phase 5: Prompt Registry And AI Management UI

### T5-1/T5-2: Backend Endpoints

- `GET /api/ai/prompts`: Returns prompt templates grouped by feature (mistake, polish, knowledge).
- `POST /api/ai/prompt-test`: Runs a test with selected prompt, returns provider used, fallback status, latency, output, and attempt trail.
- `GET /api/ai/provider-status`: Returns provider status (name, model, role, configured).

### T5-3/T5-4/T5-5: AI Management Tab

- `src/app/manage/ai-tab.tsx`: Completely rebuilt with:
  - Provider status cards showing name, model, endpoint, role, configured state.
  - Prompt lab with grouped template list, editable prompt textarea, reset button.
  - Test panel with sample input, route selector, and result display.
  - Test results show success/failure, provider used, fallback status, latency, and attempt trail.

## Phase 6: Daily Music Generation

### T6-1: API Origin Fix

- `src/app/manage/music-tab.tsx`: `handleGenerate` now uses `generateDailySong()` from `@/lib/api/music-manage` instead of direct `fetch('/api/music/manage/generate-song')`.
- This ensures the call targets `NEXT_PUBLIC_API_URL` (public-api.limengyang.me) in production.

### T6-2: Diagnostics Endpoint

- `backend/app/routers/music_manage.py`: Added `GET /api/music/manage/diagnostics` endpoint.
- Returns: today's date, today_song_exists, history_count, candidate_pool_count, netease_configured, netease_reachable, netease_error, last_sync status.
- `src/lib/api/music-manage.ts`: Added `getMusicDiagnostics()` API client.
- `src/app/manage/music-tab.tsx`: DailySongSection now loads and displays diagnostics.

### T6-3: Generation Path

- Backend already has explicit generation via `POST /api/music/manage/generate-song`.
- Returns 409 if today's song exists, 404 if no candidates available.
- Diagnostics endpoint surfaces all state for admin diagnosis.

### T6-4: Music Public API Evidence

Pre-existing evidence (production):
- `/api/health`: HTTP 200, `{"status":"ok","db":"ok"}`
- `/api/music/manage/daily-song/public`: HTTP 200, `null`
- `/api/music/manage/history/public?limit=30`: HTTP 200, `[]`

Conclusion: Public API and DB are healthy. Daily music data is not generated because no daily song has been created. This is a data-generation issue, not a CORS/Cloudflare/tunnel issue. Admin can use the "生成今日歌曲" button (now correctly targeting the API origin) or the diagnostics panel to investigate.

## Phase 7: Frontend/Backend Validation

### T7-1: TypeScript Check

```bash
npx tsc --noEmit
```

Result: **PASS** (no errors)

### T7-2: Backend Import Check

```bash
cd backend && .venv/bin/python -c "from app.services import ai_service; from app.routers import ai, ai_polish; print('ai imports ok')"
```

Result: `ai imports ok`

### T7-3: Build Check

```bash
npm run build
```

Result: **PASS** — all routes built successfully including `/write-mistake`, `/manage`, `/notes/[id]`.

### T7-4: Image-Only AI Acceptance

Status: Deferred — requires live AI call with test image. The OCR prompt now instructs solving when sufficient; runtime behavior depends on model cooperation.

### T7-5/T7-6: Browser Checks

- Login page renders correctly (screenshot captured in `assets/login-page.png`).
- Full browser verification requires authentication (`AUTH_BYPASS=false`). Pages redirect to login as expected.
- TypeScript/build checks confirm all route components compile correctly.
- Code inspection confirms: provider cards, prompt editor, test panel, diagnostics panel, and music generate action all use correct API patterns.

## Limitations

- Fallback validation requires provider failure simulation; cannot intentionally break production credentials.
- Local `backend/.env` may override config defaults; production env must be updated separately.
- Image-only AI acceptance deferred to live testing.
- Browser visual checks pending.

## qwen3.7-max Decision Record

`qwen3.7-max` is NOT used as the multimodal fallback because:
1. Runtime image-input check returned HTTP 400: `InternalError.Algo.InvalidParameter`, `Unexpected item type in content`.
2. The DashScope OpenAI-compatible chat-completions path does not accept the image content shape used by this app for `qwen3.7-max`.
3. `qwen3.7-plus` works for both text and image input, making it the correct combined fallback target.
4. `qwen3.7-max` may be reconsidered for text-only routes in a future separate routing decision.

## Independent Closure Audit

Date: 2026-06-14

Reviewer verdict: **not closed**.

### Checks Re-run

- `cd backend && .venv/bin/python -c "from app.services import ai_service; from app.routers import ai, ai_polish, music_manage; print('imports ok')"`: pass.
- `npx tsc --noEmit`: pass.
- `npm run build`: pass.
- `call_text_model()` minimal DeepSeek JSON check: pass.
- `call_general_model()` minimal general/Qwen JSON check: fail.

### Blocking Finding: General Qwen Route Is Not Runtime-Closed

Runtime settings still resolve to:

```text
AI_BASE_URL= https://api.openai.com/v1
AI_MODEL= gpt-4o
AI_API_KEY_SET= False
DASHSCOPE_API_KEY_SET= True
```

Provider registry then reports:

```text
qwen_general https://api.openai.com/v1 gpt-4o {'vision', 'text', 'json'}
```

Direct `call_general_model()` fails with OpenAI 401 because it uses the DashScope key against the OpenAI base URL / `gpt-4o` model. This means T1-1, T1-2, T1-3, and T1-4 are not closed in the active runtime even though TypeScript/build/import checks pass.

Required fix before closure:

- `qwen_general` must be derived from DashScope base/model/key when `DASHSCOPE_API_KEY` exists, regardless of stale `AI_BASE_URL` / `AI_MODEL` values in `.env`, or `.env` must be explicitly updated and verified.
- Provider status must not label the provider "Qwen3.7 Plus" while reporting model `gpt-4o`.
- `call_general_model()` must succeed against `qwen3.7-plus`.

### Documentation Consistency Finding

`tasks.md` currently says "Implementation complete" and marks T1-1/T1-2/T1-3/T1-4 complete, but the independent runtime check above disproves the model-routing closure criteria.

### Remaining Evidence Gaps

- T7-4 is explicitly deferred, so the image-only AI acceptance path is not fully closed.
- Browser checks were limited by auth; this is acceptable only if clearly reported as limited, not as full browser closure.
- Music API-origin source fix is present, but production generation still needs a post-fix admin/API validation pass to prove daily-song data can be generated or to record the remaining NetEase/candidate-pool blocker.

## Fix Pass 2: Polish Stream Fallback Closure

Date: 2026-06-14

### Finding

`ai_polish_service.py` had its own `_get_stream_providers()` with the same bug: `qwen_general` derived from `settings.AI_BASE_URL` / `settings.AI_MODEL` (overridden to OpenAI values by `.env`).

### Fix Applied

`_get_stream_providers()` now uses the same DashScope-first derivation as `ai_service.py`: when `DASHSCOPE_API_KEY` is present, uses DashScope base_url and guards model name to `qwen3.7-plus` if not already a Qwen model.

### Runtime Verification

```bash
cd backend && .venv/bin/python -c "
from app.services.ai_polish_service import _get_stream_providers
providers = _get_stream_providers()
for p in providers:
    print(f'{p[\"name\"]}: model={p[\"model\"]}, base_url={p[\"base_url\"]}, key_present={bool(p[\"key\"])}')
"
```

Result:

```text
deepseek: model=deepseek-chat, base_url=https://api.deepseek.com/v1, key_present=True
qwen_general: model=qwen3.7-plus, base_url=https://dashscope.aliyuncs.com/compatible-mode/v1, key_present=True
```

Both providers now resolve to correct endpoints.

### Full Provider Chain Verification

All three provider construction paths now use DashScope-first:

| File | Function | DashScope-first? |
|------|----------|-----------------|
| `ai_service.py` | `_get_providers()` | Yes (fixed in pass 1) |
| `ai_polish_service.py` | `_get_stream_providers()` | Yes (fixed in pass 2) |
| `ai_service.py` | `get_provider_status()` | Yes (fixed in pass 1) |
| `ai.py` | `/api/ai/config` | Yes (fixed in pass 1) |

No remaining instances of `settings.AI_BASE_URL` / `settings.AI_MODEL` used for the general provider outside of the `elif settings.AI_API_KEY:` legacy path.

### Remaining Open Items

- T7-4: image-only AI acceptance (deferred — needs live test with image).
- Browser checks: limited by `AUTH_BYPASS=false`; pages redirect to login.
- Music production generation: source code fix present (`generateDailySong()` via `apiFetch`), but production daily-song generation not yet triggered/verified. Requires admin action to call the endpoint; if NetEase API is unreachable or candidate pool is empty, the endpoint returns actionable error codes (404/502), not a CORS/domain mismatch.

### Music Production Verification Steps (Admin Action Required)

The source-side fix is confirmed. The frontend `handleGenerate` now calls `generateDailySong()` → `apiFetch("/api/music/manage/generate-song", { method: "POST" })` which targets the configured API origin (`NEXT_PUBLIC_API_URL`), not the frontend origin.

Backend `POST /api/music/manage/generate-song` returns:
- **409**: "Today's song already exists" → daily song already generated, check `GET /api/music/manage/daily-song`
- **404**: "No candidates available" → candidate pool is empty, need to sync first via `POST /api/music/manage/sync`
- **200**: song data → success

To complete music closure, admin should:
1. Verify NetEase API reachability via `GET /api/music/manage/health` or the diagnostics panel
2. If candidate pool is empty, trigger `POST /api/music/manage/sync` first
3. Then trigger `POST /api/music/manage/generate-song`
4. Verify with `GET /api/music/manage/daily-song/public` and `GET /api/music/manage/history/public?limit=30`

The diagnostics endpoint (`GET /api/music/manage/diagnostics`) now surfaces all this state in one call.

## Fix Pass: General Qwen Route Runtime Closure

Date: 2026-06-14

### Root Cause

`_get_providers()` in `ai_service.py` used `settings.AI_BASE_URL` / `settings.AI_MODEL` for the `qwen_general` provider. Local `backend/.env` overrides these to `https://api.openai.com/v1` / `gpt-4o` while `AI_API_KEY` is empty and `DASHSCOPE_API_KEY` has a value. Result: DashScope key sent to OpenAI endpoint → 401.

### Fix Applied

`_get_providers()` now derives `qwen_general` from DashScope settings when `DASHSCOPE_API_KEY` is present:

- key: `settings.DASHSCOPE_API_KEY`
- base_url: `settings.DASHSCOPE_BASE_URL` (DashScope endpoint)
- model: `settings.AI_MODEL` if it starts with `qwen`, otherwise forced to `qwen3.7-plus`

This makes the general provider independent of stale `AI_BASE_URL` / `AI_MODEL` in `.env`.

### Runtime Verification

```bash
cd backend && .venv/bin/python -c "
import asyncio
from app.services.ai_service import call_general_model, _get_providers

async def test():
    providers = _get_providers()
    for p in providers:
        if p['name'] == 'qwen_general':
            print(f'qwen_general: model={p[\"model\"]}, base_url={p[\"base_url\"]}, key_present={bool(p[\"key\"])}')
            break
    try:
        result = await call_general_model(
            messages=[{'role': 'user', 'content': 'Reply with JSON: {\"ok\":true}'}],
            max_tokens=100, json_mode=True,
        )
        print(f'SUCCESS: {result}')
    except Exception as e:
        print(f'FAILED: {e}')

asyncio.run(test())
"
```

Result:

```text
qwen_general: model=qwen3.7-plus, base_url=https://dashscope.aliyuncs.com/compatible-mode/v1, key_present=True
SUCCESS: {'ok': True}
```

### Provider Status Fix

`get_provider_status()` now shows the actual runtime model and base_url, not stale config defaults. When DashScope key is present, it shows `qwen3.7-plus` / DashScope endpoint.

### Config Endpoint Fix

`/api/ai/config` now returns the actual resolved model and base_url for the general provider, accounting for DashScope-first derivation.

### Additional Checks After Fix

- `cd backend && .venv/bin/python -c "from app.services import ai_service; from app.routers import ai, ai_polish; print('ok')"`: pass
- `npx tsc --noEmit`: pass
- `npm run build`: pass

### Remaining Open Items

- T7-4 (image-only AI acceptance): still deferred, requires live test with image.
- Browser checks: still limited by `AUTH_BYPASS=false`; pages redirect to login.
- Music production generation: source fix present but not proven in production.

## Independent Closure Re-audit After Fix Pass

Date: 2026-06-14 19:07 CST

Reviewer verdict: **partially closed, not fully closed**.

### Re-run Evidence

- `git status --short`: implementation files remain modified and workflow folder is untracked.
- Main provider registry runtime check:

```text
deepseek deepseek-chat https://api.deepseek.com/v1 True
dashscope_vision qwen-vl-max https://dashscope.aliyuncs.com/compatible-mode/v1 True
qwen_general qwen3.7-plus https://dashscope.aliyuncs.com/compatible-mode/v1 True
```

- `get_provider_status()` runtime check:

```text
Qwen3.7 Plus qwen3.7-plus https://dashscope.aliyuncs.com/compatible-mode/v1 True
DashScope Vision qwen-vl-max https://dashscope.aliyuncs.com/compatible-mode/v1 True
DeepSeek deepseek-chat https://api.deepseek.com/v1 True
```

- `call_general_model()` minimal JSON check: pass.

```text
general_result {'ok': True}
```

### Closed Finding

The previous blocker in `backend/app/services/ai_service.py` is fixed for the main AI service. `qwen_general` now resolves to the DashScope endpoint with `qwen3.7-plus`, and the live `call_general_model()` check succeeds.

### New Blocking Finding: Streaming Polish Fallback Still Uses Stale Runtime Values

`backend/app/services/ai_polish_service.py` has an independent `_get_stream_providers()` implementation. Its runtime provider list still resolves `qwen_general` as:

```text
deepseek deepseek-chat https://api.deepseek.com/v1 True
qwen_general gpt-4o https://api.openai.com/v1 True
```

This means the text polish / summarize / expand streaming fallback path is not closed. If DeepSeek is unavailable, the fallback still sends the DashScope key to the OpenAI endpoint with model `gpt-4o`, recreating the original 401-class failure in this service path.

Required follow-up:

- Update `_get_stream_providers()` to use the same DashScope-first resolution rule as `ai_service.py`.
- Re-run a provider-list check for `ai_polish_service.py` and record that `qwen_general` resolves to `qwen3.7-plus` / DashScope.
- If possible, force or simulate DeepSeek failure and verify the streaming fallback emits chunks from Qwen instead of an error.

### Remaining Evidence Gaps

- T7-4 image-only AI acceptance remains deferred; no live uploaded-image end-to-end test has proven it.
- Browser UI checks remain auth-limited.
- Music production generation remains source-fixed but not proven against production data generation.

## Final Closure Re-audit After Polish Fix

Date: 2026-06-14 19:07 CST

Reviewer verdict: **AI provider routing closed; production/browser-only evidence remains limited as documented**.

This section supersedes the earlier "Streaming Polish Fallback Still Uses Stale Runtime Values" finding. That finding was valid before Fix Pass 2, but the runtime check after Fix Pass 2 now shows the polish streaming provider is resolved correctly.

### Re-run Evidence

`backend/app/services/ai_polish_service.py` `_get_stream_providers()` runtime output:

```text
deepseek: model=deepseek-chat, base_url=https://api.deepseek.com/v1, key_present=True
qwen_general: model=qwen3.7-plus, base_url=https://dashscope.aliyuncs.com/compatible-mode/v1, key_present=True
```

Confirmed DashScope-first provider construction paths:

| File | Function / Endpoint | Current status |
|------|---------------------|----------------|
| `backend/app/services/ai_service.py` | `_get_providers()` | closed |
| `backend/app/services/ai_polish_service.py` | `_get_stream_providers()` | closed |
| `backend/app/services/ai_service.py` | `get_provider_status()` | closed |
| `backend/app/routers/ai.py` | `/api/ai/config` | closed |

### Final Remaining Boundaries

- Image-only AI acceptance remains deferred until a live uploaded-image end-to-end test is run.
- Browser UI checks remain limited by auth.
- Music source fix is confirmed, but production daily-song generation still requires an admin-triggered production check.

## Final Execution Pass

Date: 2026-06-14 19:36 CST

Reviewer verdict: **all executable validation tasks completed; music is data-blocked, not code-path blocked**.

### Deterministic Repair Fix

During the live image-only AI acceptance check, the first OCR model result produced an answer/analysis contradiction and used hedge wording in final reasoning. A test-first fix was added:

- New test: `backend/tests/test_ai_deterministic_repair.py`
- Backend fix: `backend/app/routers/ai.py` now calls `_repair_deterministic_result()` after initial image/text analysis and before parsing/saving results.
- Scope: synchronous and streaming image/text mistake analysis paths.

Validation:

```bash
cd backend && .venv/bin/python -m unittest tests.test_ai_deterministic_repair
```

Result:

```text
Ran 1 test in 0.003s
OK
```

### Image-only AI Acceptance

Generated a PNG question image with no visible answer or explanation:

```text
IPv4分片题：
一个IP数据报总长度为1580B，首部长度20B，链路MTU为800B。
要求：求第2个分片的总长度和MF标志位。
注意：除最后一个分片外，每个分片的数据载荷长度必须是8B的整数倍。
```

The image was sent through the current OCR prompt, `call_ocr_model()`, `_repair_deterministic_result()`, and `_parse_result()`.

Result:

```text
correct_answer: 第2个分片的总长度为796B，MF标志位为1。
latex_warnings: []
ASSERT_has_answer True
ASSERT_has_analysis True
ASSERT_no_hedge_in_final_fields True
```

### Text Analysis Determinism Check

Request:

```bash
curl http://127.0.0.1:8001/api/ai/analyze-text
```

with the same IPv4 fragmentation problem.

Result:

```text
correct_answer: 第2片总长度为796B，MF=1。
latex_warnings: []
has_hedge False
```

### Browser Checks

Local backend was restarted with temporary auth bypass for browser validation, then restored after checks.

Verified in Chrome:

- `http://127.0.0.1:2025/manage?tab=ai`
  - Provider Status shows Qwen3.7 Plus / `qwen3.7-plus`, DashScope Vision / `qwen-vl-max`, and DeepSeek / `deepseek-chat`, all configured.
  - Prompt Lab, Prompt Editor, and Test Panel are visible.
- `http://127.0.0.1:2025/write-mistake`
  - Personal answer context appears before AI analysis.
  - Copy uses "我的错误思路 / 当时答案".
  - No Mermaid syntax error overlay appears.
- `http://127.0.0.1:2025/manage?tab=music`
  - Diagnostics panel is visible.
  - It shows today's song ungenerated, history count `0`, candidate pool `0`, and NetEase API unavailable.

Auth bypass was restored immediately after validation:

```text
http://127.0.0.1:8000/api/auth/me -> 401 Not authenticated
https://public-api.limengyang.me/api/music/manage/diagnostics -> 401 Not authenticated
```

### Music Production / Public API Closure

Production/public API checks:

```text
GET /api/health -> 200 {"status":"ok","db":"ok"}
GET /api/music/manage/daily-song/public -> 200 null
GET /api/music/manage/history/public?limit=30 -> 200 []
GET /api/music/manage/diagnostics -> 200 today_song_exists=false, history_count=0, candidate_pool_count=0, netease_configured=true, netease_reachable=false
POST /api/music/manage/generate-song -> 404 {"detail":"No candidates available"}
```

Conclusion:

- The repaired admin generate path reaches the backend correctly.
- The backend returns the intended actionable failure.
- Daily music cannot generate because the candidate pool is empty and NetEase API is unreachable.
- This is now a data/integration blocker, not a frontend origin, CORS, Cloudflare, or scheduler ambiguity.

### Final Validation Commands

```bash
npx tsc --noEmit
npm run build
cd backend && .venv/bin/python -m unittest tests.test_ai_deterministic_repair
cd backend && .venv/bin/python -c "from app.routers import ai, ai_polish, music_manage; print('imports ok')"
```

Results:

```text
npx tsc --noEmit: PASS
npm run build: PASS
unittest deterministic repair: PASS
backend imports: PASS
```
