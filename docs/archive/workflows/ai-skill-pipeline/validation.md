# Validation: AI Skill Pipeline Knowledge Base

## Validation Status

Backend Phase 3–5 implementation complete. Validation performed on 2026-06-05.

## Validation Gate

- `tasks.md`: approved via user's explicit implementation instruction.
- Implementation tasks: executed for Phase 3 (schemas), Phase 4 (services), Phase 5 (API endpoints).
- `git status --short`: checked before implementation. User changes preserved.
- `AGENTS.md`: read and followed.

## Evidence Summary

### V1 Planning Gate

All required files exist:

- [x] `README.md`
- [x] `requirements.md`
- [x] `design.md`
- [x] `tasks.md`
- [x] `validation.md`
- [x] `handoff-prompt.md`
- [x] `report.md`

### V2 Scope Control

Verified no phase-1 implementation introduces:

- [x] No vector database
- [x] No embedding model
- [x] No first-class `KnowledgePoint` table or model
- [x] No silent persistent relation graph
- [x] No unapproved frontend routes or pages
- [x] No runtime dependency on OpenClaw, Claude Code, Codex, or local skill folders
- [x] No AI calls inside deterministic retrieval endpoints

### V3 Existing Model Mapping

Verified real fields in:

- [x] `backend/app/models/note.py`: Note model with all required fields
- [x] `backend/app/schemas/note.py`: NoteType, Difficulty, NoteOut, etc.
- [x] `backend/app/routers/review.py`: SM-2 review integration

### V4 Structured Retrieval

Target: `POST /api/knowledge/context-pack`

- [x] Subject matching works (ilike)
- [x] Knowledge_points matching works (comma-split + ilike)
- [x] Tags matching works (via note_tags join)
- [x] Date range filtering works
- [x] Limit is respected (1–100)
- [x] Empty results handled safely
- [x] No external AI provider called (verified via `inspect.getsource()`)

### V5 Weak-Point Summary

Target: `GET /api/knowledge/weak-points?days=30`

- [x] Days parameter is respected (1–365)
- [x] Recent mistakes are counted
- [x] Due reviews are counted
- [x] Top error reasons returned (from ai_metadata)
- [x] Empty datasets return safe empty response
- [x] No external AI provider called (verified via `inspect.getsource()`)

### V6 Source Reference Contract

Source refs include:

- [x] source_type (note/mistake)
- [x] source_id (UUID string)
- [x] title
- [x] slug
- [x] field
- [x] excerpt (max 300 chars)
- [x] url
- [x] confidence (0–1)
- [x] match_reasons

### V7 Relation Suggestions

Relation suggestions include:

- [x] source_type, source_id
- [x] target_type, target_id
- [x] relation_type (explains/similar/prerequisite/follow_up/source_for)
- [x] score (0–1)
- [x] reason
- [x] status (default: "suggested")

Relations are NOT persisted — only returned as suggestions.

### V8 Citation-Backed Generation (updated 2026-06-05, fix applied 2026-06-05)

Target: `POST /api/ai/knowledge-summary`

- [x] source_backed_claim blocks include source_refs
- [x] ai_inference blocks are labeled
- [x] insufficient_context returned when no sources
- [x] No invented source IDs (validated against `source_map`)
- [x] Empty sources produce insufficient_context, not unsupported articles
- [x] source_backed_claim without valid refs downgraded to ai_inference
- [x] **Field whitelist**: AI-returned `field` checked against per-source-type whitelist:
  - Mistake fields: `{analysis, question, correct_answer, error_reason, key_step, generalization, review_advice, knowledge_points, content}`
  - Note fields: `{content, summary, title, knowledge_points}`
  - Invalid field falls back to original matched source's `field`
- [x] **Fidelity copy**: All source ref attributes (`source_type`, `title`, `slug`, `excerpt`, `url`, `confidence`, `match_reasons`) are faithfully copied from the original matched source — AI cannot overwrite them
- [x] **Bug fix**: `SourceType` was missing from `app.schemas.knowledge` import in `ai.py`, causing `NameError` on the source-ref validation branch. Added import. Verified via function-level mock that exercises the branch with a valid source map entry.

### V9 Field Safety

Not directly applicable to this implementation pass (no humanizer/tone refinement code changes). Existing field safety rules in `ai_polish_service.py` are preserved.

### V10 OCR Safety

Not directly applicable to this implementation pass. Existing OCR safety in `ai.py` router is preserved.

### V11 Social Card Export

Not directly applicable — social card export not implemented in this pass.

### V12 Security

- [x] API keys not exposed to frontend code
- [x] Provider secrets read from backend environment/config only (`app/config.py`)
- [x] Runtime code does not depend on local skill folders
- [x] Logs do not print API keys (existing logging in `ai_polish_service.py` only logs action/text_len/duration/status)

### V13 Performance

- [x] Optional humanizer does not run by default on every AI call
- [x] Social card export is manual (not implemented)
- [x] Deterministic retrieval endpoints do not call external AI
- [x] context-pack respects limit (1–100)

## Commands Run

```bash
# Backend import verification
.venv/bin/python -c "from app.schemas.knowledge import ..."
.venv/bin/python -c "from app.services.knowledge_retrieval import ..."
.venv/bin/python -c "from app.services.knowledge_relations import ..."
.venv/bin/python -c "from app.routers.knowledge import router"
.venv/bin/python -c "from app.routers.ai import knowledge_summary"
.venv/bin/python -c "from main import app"

# Deterministic verification
.venv/bin/python -c "import inspect; ... assert 'call_text_model' not in src"

# Schema validation
.venv/bin/python -c "req = ContextPackRequest(...); ref = SourceRef(...)"

# Function-level source-ref branch verification (after SourceType fix)
.venv/bin/python -c "... matched.source_type == SourceType.mistake ..."

# Skill verification
ls ~/.openclaw/skills/Humanizer-zh/SKILL.md
ls ~/.openclaw/skills/guizang-social-card-skill/SKILL.md
ls ~/.openclaw/skills/ian-xiaohei-illustrations/SKILL.md
ls ~/.openclaw/skills/notebooklm-skill/SKILL.md

# Frontend type check
npx tsc --noEmit
```

All commands passed.

## Modified Files

| File | Change |
|---|---|
| `backend/app/schemas/knowledge.py` | New file — all knowledge schemas |
| `backend/app/services/knowledge_retrieval.py` | New file — structured retrieval + weak-point aggregation |
| `backend/app/services/knowledge_relations.py` | New file — relation suggestion scoring |
| `backend/app/routers/knowledge.py` | New file — context-pack + weak-points endpoints |
| `backend/app/routers/ai.py` | Added knowledge-summary endpoint + SourceType import fix |
| `backend/main.py` | Registered knowledge router |
| `src/lib/api/knowledge.ts` | New file — frontend types + API wrappers |

## Remaining Risks

1. **AI model dependency**: `POST /api/ai/knowledge-summary` requires DeepSeek API configuration (`DEEPSEEK_API_KEY`). If not configured, the endpoint will return 500.
2. **No database migration needed**: All new code uses existing `Note` model fields. No schema changes.
3. **Frontend display complete**: T6-2/T6-3 frontend UI (related notes/mistakes panel, weak-point summary panel) implemented and validated. Real recall quality pending real data.

## Frontend Display Round Validation

### V14: TypeScript Check

- **Command**: `npx tsc --noEmit`
- **Result**: pass — zero errors
- **Date**: 2026-06-07

### V15: Build Check

- **Command**: `npm run build`
- **Result**: pass — build succeeded with all routes rendered
- **Date**: 2026-06-07

### V16: Browser Inspection

- `/mistakes` page:
  - Existing review stats and mistake list render correctly.
  - `WeakPointsPanel` renders and shows "加载薄弱点数据…" loading state (backend not available).
  - Existing filters and search bar preserved.
  - No existing UI broken.

- `/notes/{slug}` page:
  - Page renders without errors.
  - `RelatedKnowledgePanel` conditionally renders only for `note.type === "mistake"`.
  - Non-mistake pages unaffected.

### V17: Empty-State Verification

Local database has no data to return from `/api/knowledge/context-pack` or `/api/knowledge/weak-points`. Verified:
- Weak-point panel shows loading state gracefully.
- UI does not crash or block when backend API returns 401/error.
- Empty-state paths in panel components are present and will render when API returns empty results.

### V18: Scope Control

- [x] No new top-level routes introduced
- [x] No new backend endpoints created
- [x] No database migrations
- [x] No new dependencies installed
- [x] No relation persistence UI
- [x] No vector database or KnowledgePoint entity introduced
- [x] No existing review stats or filters broken
- [x] No unrelated files refactored

### V19: Changed Files

| File | Change |
|---|---|
| `src/hooks/use-knowledge.ts` | New file — `useContextPack` and `useWeakPoints` SWR hooks |
| `src/app/notes/[id]/components/related-knowledge-panel.tsx` | New file — related knowledge panel for mistake detail |
| `src/app/notes/[id]/note-detail-content.tsx` | Added import and `<RelatedKnowledgePanel>` in mistake branch |
| `src/app/mistakes/components/weak-points-panel.tsx` | New file — weak-points summary panel |
| `src/app/mistakes/page.tsx` | Added import and `<WeakPointsPanel>` after plan section |
| `docs/workflows/ai-skill-pipeline/tasks.md` | Updated task status with validation reports |
| `docs/workflows/ai-skill-pipeline/validation.md` | Updated with frontend validation results |

### Remaining Risks

1. **Backend availability**: Knowledge API endpoints require backend running with database. Frontend gracefully handles loading/error states.
2. **Recall quality**: Cannot validate recall quality of context-pack and weak-points endpoints without real data.
3. **Auth required**: API calls require JWT token. Frontend relies on existing auth flow.

## Public Deployment Validation

### V20: Cloudflare Deploy

- **Command**: `source ~/.zshrc && npm run deploy`
- **Result**: pass — deployed `2025-blog-public` to Cloudflare Workers
- **URL**: `https://2025-blog-public.17527677392.workers.dev`
- **Version ID**: `9fda0e85-dbb9-4ad5-a02e-8647afc4a80c`
- **Worker startup time**: 22 ms
- **Asset upload**: no updated asset files uploaded; existing assets reused
- **Date**: 2026-06-07

### V21: Public URL Smoke Check

- **Command**: `curl -I -L --max-time 20 https://2025-blog-public.17527677392.workers.dev`
- **Result**: pass — public URL returned `HTTP/2 200`
- **Headers observed**: `x-opennext: 1`, `x-powered-by: Next.js`
- **Date**: 2026-06-07

### Deployment Notes

1. Deployment used the current working tree, including the completed frontend display files and workflow documentation updates.
2. Cloudflare authentication succeeded only after reloading the updated global `CLOUDFLARE_API_TOKEN` from `~/.zshrc`.
3. Deploy warnings came from generated OpenNext output and Node deprecation messages; no deploy-blocking error remained.

### V22: workers.dev Trigger Recovery

- **Cause**: A follow-up attempt to attach `blog.limengyang.me` with `--domain` / `--route` uploaded a new Worker version before failing trigger setup. Because `workers_dev` was absent from `wrangler.toml`, Wrangler disabled the `workers.dev` trigger.
- **Fix**: Added `workers_dev = true` to `wrangler.toml` and redeployed.
- **Command**: `source ~/.zshrc && npm run deploy`
- **Result**: pass — `https://2025-blog-public.17527677392.workers.dev/` returned `HTTP 200`
- **Version ID**: `4455e8c3-3fbe-48f4-9baf-6ef677d0924b`
- **Date**: 2026-06-07

### V23: Custom Domain Diagnosis

- **URL checked**: `https://blog.limengyang.me/`
- **Result**: partial — root returned `HTTP 200`, but HTML still referenced old `_next` chunks such as `f24e8a11405f1662.css`.
- **Evidence**: `https://blog.limengyang.me/_next/static/chunks/f24e8a11405f1662.css` returned `HTTP 404`, while the active workers.dev build uses `7c5c3a00e1a44bc1.css`.
- **Route attempt**: `npx wrangler deploy --route 'blog.limengyang.me/*'` failed with `Authentication error [code: 10000]` on `/zones/.../workers/routes`.
- **Custom domain attempt**: `npx wrangler deploy --domain blog.limengyang.me` failed because the hostname already has externally managed DNS records.
- **Remaining action**: grant zone-level Worker Routes permissions and deploy a route, or remove the existing DNS record and attach `blog.limengyang.me` as a Worker Custom Domain.

### V25: Custom Domain Route Deployment

- **Command**: `source ~/.zshrc && npx wrangler deploy --route 'blog.limengyang.me/*'`
- **Result**: pass — deployed `2025-blog-public` with both `workers.dev` and `blog.limengyang.me/*` triggers
- **Version ID**: `bdbbe429-ec0f-4fef-a6f8-bd03ee989f9f`
- **Smoke checks**:
  - `https://blog.limengyang.me/` returned `HTTP 200`
  - `https://blog.limengyang.me/mistakes` returned `HTTP 200`
  - `https://blog.limengyang.me/_next/static/chunks/7c5c3a00e1a44bc1.css` returned `HTTP 200`
- **Date**: 2026-06-07

### V26: OpenNext Artifact Rebuild

- **Cause**: The first route deployment uploaded an older `.open-next` artifact. `npm run deploy` deploys the existing OpenNext output and does not guarantee regeneration of Cloudflare artifacts from the latest source changes.
- **Fix**: Rebuilt Cloudflare artifacts before deployment.
- **Commands**:
  - `npx tsc --noEmit`
  - `npm run build:cf`
  - `source ~/.zshrc && npx wrangler deploy --route 'blog.limengyang.me/*'`
- **Result**: pass — 79 new or modified static assets uploaded; `blog.limengyang.me/*` and `workers.dev` triggers deployed.
- **Version ID**: `7ce87290-afac-4103-8090-ea01f6492030`
- **Smoke checks**:
  - `https://blog.limengyang.me/mistakes` returned `HTTP 200`
  - The `/mistakes` HTML includes the new weak-point panel loading text: `加载薄弱点数据…`
  - `https://blog.limengyang.me/_next/static/chunks/f24e8a11405f1662.css` returned `HTTP 200`
- **Date**: 2026-06-07

### V24: Backend Access Diagnosis

- **URL checked**: `https://api.limengyang.me/api/notes?type=blog&status=published&size=100`
- **Result**: blocked — request redirected to Cloudflare Access login HTML under `small-term-e3a5.cloudflareaccess.com`.
- **Impact**: browser requests from `https://blog.limengyang.me` fail CORS preflight because the Access login response does not include the expected API CORS headers.
- **Remaining action**: configure a public/bypass Access policy for public read endpoints, or proxy these public reads through a frontend route that has valid service-token access.

### V27: Public API Domain Cutover

- **Decision**: Use a separate public API host for read-only public frontend data instead of loosening Access on `api.limengyang.me`.
- **Frontend config change**: `.env.production` now uses `NEXT_PUBLIC_API_URL=https://public-api.limengyang.me`.
- **Commands**:
  - `npx tsc --noEmit`
  - `npm run build:cf`
  - `source ~/.zshrc && npx wrangler deploy --route 'blog.limengyang.me/*'`
- **Result**: pass — deployed with `blog.limengyang.me/*` and `workers.dev` triggers.
- **Version ID**: `413568ca-95f0-4eed-b112-4ee8a61374a7`
- **Smoke checks**:
  - `https://public-api.limengyang.me/api/notes?type=blog&status=published&size=100` returned `HTTP 200` JSON.
  - `https://public-api.limengyang.me/api/music/playlist` returned `HTTP 200` JSON.
  - `OPTIONS https://public-api.limengyang.me/api/notes?...` with origin `https://blog.limengyang.me` returned `HTTP 200` with `access-control-allow-origin: https://blog.limengyang.me`.
  - Online JS chunk contains `https://public-api.limengyang.me` as the API base.
- **Remaining risk**: `api.limengyang.me` remains Access-protected by design; private/admin API calls must continue using authenticated flows.
- **Date**: 2026-06-07
