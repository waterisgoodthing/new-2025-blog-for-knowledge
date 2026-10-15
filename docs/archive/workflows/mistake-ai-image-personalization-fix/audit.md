# Audit: AI Mistake And Prompt Management Upgrade

Date: 2026-06-14

## Evidence Reviewed

- User screenshots:
  - `/notes/ip` shows generic analysis: "图片中未提供答案或解析。"
  - `/write-mistake` shows fields including "我的错误答案..." and a Mermaid `Syntax error in text` overlay.
  - `/manage?tab=ai` shows static AI status cards, passive feature cards, and one polish test input.
- User-provided production evidence for daily music:
  - `GET https://public-api.limengyang.me/api/health` returns `200 {"status":"ok","db":"ok"}`.
  - `GET https://public-api.limengyang.me/api/music/manage/daily-song/public` returns `200 null`.
  - `GET https://public-api.limengyang.me/api/music/manage/history/public?limit=30` returns `200 []`.
- Source files:
  - `backend/app/config.py`
  - `backend/app/services/ai_service.py`
  - `backend/app/services/ai_polish_service.py`
  - `backend/app/services/recommendation.py`
  - `backend/app/routers/ai.py`
  - `src/app/write-mistake/components/mistake-form.tsx`
  - `src/app/manage/ai-tab.tsx`
  - `src/app/manage/music-tab.tsx`
  - `backend/main.py`
  - `src/components/mermaid-block.tsx`
  - `src/app/notes/[id]/note-detail-content.tsx`

## Findings

### F1: AI upload can run before learner context exists

`MistakeForm` places the AI text/image analysis card above the structured fields. `uploadAndAnalyzeFiles()` sends `form.my_answer`, `form.correct_answer`, and `form.user_error_analysis` only if they already exist. In the common upload-first flow, those fields are still empty.

Impact: personalized diagnosis is absent or generic.

### F2: Field wording still centers "wrong answer" instead of "wrong thought"

The structured field and saved content still use user-facing wording like `我的错误答案`. The separate `user_error_analysis` field exists, but the primary red field still nudges the user to enter only a final answer.

Impact: the AI receives weaker context and the record reads less like a real mistake-learning note.

### F3: OCR prompt intentionally avoids solving when image lacks answer or explanation

`OCR_SYSTEM_PROMPT` says the OCR assistant should not make up missing information and "你只负责识别与结构化提取，不负责完整解题".

Impact: screenshot symptom "图片中未提供答案或解析" is consistent with current prompt design.

### F4: Image-based visual context is not preserved in the main study record

The API supports saved `images` and `diagrams`, but the generated `question` remains text-only. There is no explicit `visual_context` or image-dependency summary.

Impact: topology, geometry, screenshot, or figure-dependent questions lose critical context when reviewed later.

### F5: AI-generated Mermaid can surface as an intrusive syntax error

The AI prompts require Mermaid diagrams for network/geometry/flow topics. Invalid Mermaid can surface as a large parser error graphic on `/write-mistake`.

Impact: the upload page is visually broken and confusing.

### F6: Final explanations can hide contradictions behind uncertain wording

The user-provided IP fragmentation example uses "可能因偏移单位为8字节导致实际填充调整" while still concluding a concrete answer.

Impact: the learner may save an explanation that sounds plausible but contains an unresolved arithmetic/protocol contradiction.

### F7: General AI is still `gpt-4o` and unconfigured

`backend/app/config.py` defaults `AI_MODEL` to `gpt-4o`, while the management screenshot shows the general AI card as unconfigured. `AI_API_KEY` is empty locally; dedicated DashScope and DeepSeek keys exist.

Impact: general AI features can miss the available Qwen provider.

### F8: Text/OCR routes do not share fallback routing

`call_text_model()` is bound to DeepSeek, `call_ocr_model()` is bound to DashScope vision, and `ai_polish_service.py` performs its own DeepSeek streaming call.

Impact: if DeepSeek or the dedicated vision model is temporarily unavailable, features fail instead of falling back to `qwen3.7-plus`.

### F9: AI management is not a prompt lab yet

`src/app/manage/ai-tab.tsx` currently renders static provider cards, passive feature cards, and one polish test input.

Impact: prompt improvement is still code-edit driven instead of visually testable from the management console.

### F10: Daily music public API is healthy but no daily song data exists

Production evidence shows the public backend and database are reachable, but the daily-song public endpoint returns `null` and public history returns `[]`.

Impact: `/music` can open, but it can only show "今日歌曲尚未生成".

### F11: Daily music generation is request-triggered, not scheduled

The reported code evidence is that `backend/main.py` registers routes but does not run a scheduler/cron. `get_or_create_today_song()` only attempts generation when called. If the candidate pool is empty, `generate_daily_song()` returns `None`.

Impact: a quiet day or empty candidate pool leaves production with no daily song.

### F12: Candidate pool sync likely depends on unavailable NetEase API configuration

The reported code evidence is that the default NetEase API config points to `http://localhost:3000`. In production, if NeteaseCloudMusicApi is not deployed/configured, candidate sync cannot populate songs.

Impact: daily generation has no candidates and returns `null`.

### F13: Manage music generate button can hit the wrong domain

The reported frontend bug is `src/app/manage/music-tab.tsx:134`, where "生成今日歌曲" directly calls `fetch('/api/music/manage/generate-song', ...)`. On `https://blog.limengyang.me`, that path returns 404 because write/manage API calls should go through the configured API base, currently `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me`, via `generateDailySong()` / `apiFetch()`.

Impact: even an authenticated admin may fail to repair daily music from `/manage`.

## Initial Root Cause Summary

The issue spans five layers:

1. UX sequencing: upload-first generation does not gather mistake-thinking context.
2. Prompt contract: OCR extraction is separated from solving, but the UI expects a complete explanation.
3. Rendering resilience: generated Mermaid is accepted and rendered without enough isolation.
4. Output quality control: final reasoning is not guarded against hedge words that mask contradictions.
5. AI infrastructure: provider routing, fallback, prompt registry, and management UI are fragmented.
6. Music operations: daily generation lacks an active schedule/backfill path, candidate sync may be empty, and the admin repair button may call the wrong origin.
