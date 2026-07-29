# Handoff Prompt: AI Mistake And Prompt Management Upgrade

You are working in `/Users/limengyang/2025-blog-public`.

Read `AGENTS.md` first. Then read the workflow files in:

```text
docs/workflows/mistake-ai-image-personalization-fix/
```

Do not implement until `tasks.md` has explicit user approval in the conversation.

Primary objective:

Complete one combined AI upgrade:

- Fix the mistake entry AI flow so uploaded/image-based mistakes preserve visual context, generate answer/analysis when the visible question is sufficient, collect the learner's wrong thought before or alongside AI generation, and prevent Mermaid syntax errors from breaking `/write-mistake`.
- Change general AI to DashScope `qwen3.7-plus`.
- Add fallback from DeepSeek text and DashScope vision routes to `qwen3.7-plus`.
- Turn `/manage?tab=ai` into a visual prompt editing and testing lab.

Respect these boundaries:

- Touched domains: `mistakes`, `notes`, `manage`, backend AI, shared Mermaid rendering.
- The callable model ID is `qwen3.7-plus`, not `Qwen3.7plus`.
- Current credentials were verified to call `qwen3.7-plus` successfully on 2026-06-14.
- Keep provider routing in backend services, not React components.
- Preserve DeepSeek and DashScope as dedicated primary routes.
- Do not expose API keys.
- Preserve existing `my_answer` data contract unless a migration is explicitly approved.
- Keep routers thin enough; avoid unrelated refactors.
- Update `tasks.md` immediately after each completed task item.
- Record validation in `validation.md`.

Expected validation:

```bash
cd backend && .venv/bin/python -c "from app.services import ai_service; from app.routers import ai, ai_polish; print('ai imports ok')"
npx tsc --noEmit
npm run build
```

Also inspect `/write-mistake` and `/manage?tab=ai` in a browser and record results.
