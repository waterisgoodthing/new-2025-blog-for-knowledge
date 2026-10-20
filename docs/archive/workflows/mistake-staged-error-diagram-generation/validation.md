# Validation

## Baseline (T0-01) — 2026-06-15

- Branch: `notes-workspace-ux-upgrade`
- Untracked: `docs/workflows/mistake-staged-error-diagram-generation/`, `public/mymusic/0250孙燕姿-遇见.mp3`
- No staged/unstaged modifications to source code.
- Last commit: `c51da85 Update AI provider model defaults`

### Touched domains baseline

| Domain | Key files | Current state |
|--------|-----------|---------------|
| write-mistake form | `src/app/write-mistake/components/mistake-form.tsx` (620 lines) | One-shot analyze: upload image → SSE stream → full analysis in single call. No staged gates. |
| AI API client | `src/lib/api/ai.ts` (244 lines) | `analyzeMistakeStream`, `analyzeTextStream` — single-call pattern. No staged endpoints. |
| Backend AI router | `backend/app/routers/ai.py` (1353 lines) | `/api/ai/analyze-stream`, `/api/ai/analyze-text-stream` — one-shot OCR+analysis. |
| Backend AI schemas | `backend/app/schemas/ai.py` (56 lines) | `AnalyzeRequest`, `TextAnalyzeRequest`, `AnalyzeResponse` — flat, no staged fields. |
| Backend AI service | `backend/app/services/ai_service.py` (316 lines) | Multi-provider fallback (DeepSeek, DashScope Vision, Qwen). No image generation. |
| Note model | `backend/app/models/note.py` (110 lines) | `ai_metadata` JSON field stores diagrams, visual_context, etc. |
| Mermaid rendering | `src/components/mermaid-block.tsx` (96 lines) | Dynamic mermaid import, SVG render. |
| Diagram viewer | `src/components/diagram-viewer.tsx` (173 lines) | Zoom/fullscreen/download for SVG/images. |
| Mistake detail | `src/app/notes/[id]/note-detail-content.tsx` (376 lines) | Renders diagrams via `MermaidBlock`, AI metadata sections. |

## Planned validation

- Backend staged-AI tests.
- Backend diagram-strategy tests.
- `npx tsc --noEmit`.
- `npm run build`.
- Browser check for `/write-mistake`.
- Browser check for mistake detail page.
- Optional Qwen image fallback live test only if DashScope image credentials are configured.

## T0-04: Qwen Image Model Verification

- `qwen-image-2.0-pro` is **NOT configured** in the current environment.
- No `DASHSCOPE_IMAGE_API_KEY`, `DASHSCOPE_IMAGE_MODEL`, or `DASHSCOPE_IMAGE_BASE_URL` env vars exist in `backend/.env` or `backend/.env.example`.
- Existing DashScope config (`DASHSCOPE_API_KEY`) is for OpenAI-compatible text/vision API (qwen3.7-plus), not the image generation API.
- Image generation uses a different DashScope endpoint: `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- Decision: Add config support for image generation with disabled-by-default state. Backend will return `provider_disabled` status when no image key is configured.

## T7-01: Backend Tests (2026-06-15)

### Round 1 — initial implementation

```
Ran 27 tests in 0.007s — OK
```

### Round 2 — after review fixes

```
Ran 50 tests in 0.010s — OK
```

- 9 existing tests (deterministic repair, provider models, local music)
- 41 staged workflow tests:
  - QuestionDraftSchemaTest (4 tests)
  - ErrorInterpretationSchemaTest (4 tests)
  - StagedGateSchemaTest (2 tests)
  - InterpretationVersionBindingTest (3 tests)
  - DiagramSafetySchemaTest (7 tests)
  - DiagramStrategyClassifierTest (9 tests) — strategy routing for network/IP/algorithm/math vs fallback
  - QwenImageFallbackConfigTest (1 test) — verifies disabled by default
  - QuestionDraftNormalizationTest (4 tests) — options/key_conditions/title truncation/defaults
  - GateValidationTest (4 tests) — Pydantic `min_length=1` on user_error_reason/rejection_reason
  - InterpretationVersionBehaviorTest (2 tests) — version increment, stale detection

## T7-02: TypeScript Validation (2026-06-15)

```
npx tsc —noEmit — 0 errors
```

Fixed type errors across two rounds:
1. `uploadImage` returns `{ url: string }`, not `string`
2. `NoteCreateInput` requires `slug` field
3. `unknown` type used as ReactNode condition (multiple occurrences in staged metadata rendering)

## T7-03: Frontend Build (2026-06-15)

```
npm run build — success
```

All routes build cleanly including `/write-mistake` and `/write-mistake/[slug]`.

## T7-04/T7-05: Browser Checks

Not yet performed. Requires running `npm run dev` and manual walkthrough of:

- `/write-mistake`: image upload → draft → confirm → error reason → accept/reject → analysis → diagram → save
- `/notes/[id]` for a staged mistake: verify interpretation details, structured diagram SVG, table, mermaid render

## T7-07: Production Deploy

Performed on 2026-06-15 after explicit user request.

- Command: `source ~/.zshrc && npm run deploy:full`
- First deploy result: PASS, Worker version `678bff75-84ef-48a0-b752-bc648e8684f5`.
- Cleanup: removed ignored macOS `.DS_Store` metadata files from `public/` and `.open-next/assets/` after the first upload log showed they were included as static assets.
- Second deploy result: PASS, Worker version `d4690aa9-3013-426d-9223-0d6f1a472a97`.
- Public BUILD_ID after second deploy: `KlhA3CfUDl-Dksu4Iupbl`.
- `GET https://blog.limengyang.me/write-mistake`: PASS, `HTTP/2 200`, `x-opennext: 1`.
- `GET https://blog.limengyang.me/.DS_Store`: PASS, `404`.
- `GET https://blog.limengyang.me/mymusic/.DS_Store`: PASS, `404`.
- Backend restart: `launchctl kickstart -k gui/$(id -u)/com.blog.backend`, followed by local and public `/api/health` returning `{"status":"ok","db":"ok"}`.
- Build artifact check: local `.open-next/assets` contains staged mistake markers including `AI 对错因的理解`, `生成错因理解`, `不采纳，重写`, `结构化图解`, and `未配置（降级为结构化图表）`.

Limit: this is a public smoke test, not a logged-in browser walkthrough. T7-04/T7-05 remain open for the full image upload -> draft -> accept/reject -> analysis -> diagram -> save path and detail rendering.

## Known Remaining Gaps

- Edit mode stale marking: implemented but untested in browser (needs a saved staged mistake opened in edit form)
- Qwen image fallback: code path complete but `DASHSCOPE_IMAGE_API_KEY` not configured; end-to-end image generation untested
- Endpoint-level gate enforcement: Pydantic schemas reject empty `user_error_reason`/`rejection_reason`, but router endpoints also have explicit `HTTPException` checks — no integration test exercises the full HTTP path
