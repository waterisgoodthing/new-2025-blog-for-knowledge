# Diff Report: AI Mistake And Prompt Management Upgrade

Status: Planned only.

## Expected Backend Files

- `backend/app/config.py`
  - General Qwen defaults.

- `backend/.env.example`
  - Updated example model/base URL guidance.

- `backend/app/services/ai_service.py`
  - Provider registry and fallback routing.

- `backend/app/services/ai_polish_service.py`
  - Route-aware streaming/fallback.

- `backend/app/services/recommendation.py`
  - General Qwen route for recommendations.

- `backend/app/services/ai_prompt_registry.py` or equivalent
  - Prompt template registry.

- `backend/app/routers/ai.py`
  - Image prompt update, personal-context helper, deterministic guard, provider status, and prompt test endpoints.

- backend music router/service files
  - Daily song diagnostics, generation/backfill response clarity, candidate/NetEase status if needed.

- `backend/app/schemas/ai.py` or new admin schema file
  - Visual context fields and structured provider/prompt/test response contracts.

## Expected Frontend Files

- `src/app/write-mistake/components/mistake-form.tsx`
  - Wrong-thought copy, AI generation context flow, persisted metadata fields.

- `src/app/notes/[id]/note-detail-content.tsx`
  - Visual context display.

- `src/components/mermaid-block.tsx`
  - Invalid Mermaid containment.

- `src/app/manage/ai-tab.tsx`
  - Provider cards, prompt workspace, test result panel.

- `src/app/manage/music-tab.tsx`
  - Correct API-origin usage for "生成今日歌曲" and admin-facing diagnostics if needed.

- `src/lib/api/ai.ts`
  - Visual context response type additions.

- `src/lib/api/ai-admin.ts` or equivalent
  - Typed admin AI API calls.

## Explicitly Out Of Scope

- Database migrations unless explicitly approved.
- New top-level routes.
- Unrelated home/blog refactors.
- Deployment changes.
- Public prompt editing.
- Exposing API keys.
- Removing DeepSeek or DashScope dedicated model support.
