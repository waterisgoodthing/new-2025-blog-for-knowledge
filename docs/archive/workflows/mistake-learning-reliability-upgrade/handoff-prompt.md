# Implementation Agent Prompt

Use this prompt for a coding agent that will implement the approved task list.

```text
You are working in /Users/limengyang/2025-blog-public.

First read AGENTS.md and obey it. This task is in:

docs/workflows/mistake-learning-reliability-upgrade/

Read these files before touching code:

1. README.md
2. audit.md
3. requirements.md
4. design.md
5. tasks.md
6. validation.md

Critical workflow rule:

- Do not implement anything unless the conversation explicitly approved tasks.md or a specific phase subset.
- Before editing, run git status --short.
- Preserve unrelated dirty files. Do not revert, format, or move unrelated changes.
- After completing each task item, immediately update tasks.md and mark exactly that item complete.
- Record validation in validation.md as you go.

Touched domains:

- auth
- mistakes
- review
- notes
- shared infrastructure

Main goals:

1. Fix public API/login reliability diagnostics so browser failures are not generic Failed to fetch.
2. Fix `Note` datetime failures in review submit and adjacent note update/type-conversion paths covered by the task list.
3. Fix duplicate slug creation failures for Chinese/ASCII mistake titles.
4. Normalize tags and weak-point concepts so the UI does not show fragmented raw tags.
5. Convert weak-point diagnosis into a drawer-style interaction.
6. Replace template-like diagnosis copy with evidence-aware and personalized content.
7. Move knowledge-point summary below tags in the mistake detail right rail.
8. Make AI formula output reliable LaTeX and verify RichText/KaTeX rendering.
9. Pass my_answer and user_error_analysis into AI analysis as structured fields.

Implementation constraints:

- Do not introduce a full KnowledgePoint table in this iteration unless the user approves a scope expansion.
- Keep weak-point aggregation deterministic. Do not make GET /api/knowledge/weak-points call an AI provider.
- Do not rely only on display-layer tag grouping. Also prevent obvious low-value AI tags such as quality labels or duplicate aliases from being saved as primary tags.
- Preserve user_error_analysis separately from generic analysis and AI personalized diagnosis.
- If AI is used for personalized diagnosis, make it an explicit action or endpoint and use validated source/personal fields.
- Do not expose secrets, Cloudflare tunnel credentials, tokens, or .env values.
- External Cloudflare tunnel changes are operational. Do not edit files outside the repo unless the user explicitly approves.
- Use existing API wrappers under src/lib/api/ and existing backend router/service/schema boundaries.
- Keep routers thin; move business logic into backend services/helpers.
- Keep frontend operational pages dense and readable. Do not add marketing-style pages.

Suggested implementation order:

1. Phase 0 baseline and reproduction.
2. Phase 1 P0 runtime reliability:
   - API error classification
   - API base/auth verification
   - Note datetime write fix
   - slug uniqueness
3. Phase 2 AI contract:
   - extend schemas/types
   - send personal fields
   - capture and persist user_error_analysis
   - store/display personalized diagnosis
   - LaTeX output validation/repair
4. Phase 3 tag/weak-point normalization.
5. Phase 4 drawer and detail layout.
6. Phase 5 validation and workflow doc updates.

Validation expectations:

- Run npx tsc --noEmit for frontend TypeScript changes.
- Run npm run build for build-sensitive frontend changes.
- Run backend import/start checks or targeted tests for backend changes.
- Browser-check:
  - login/auth status
  - create two similar-title IPv4 mistakes
  - submit one review
  - inspect /mistakes weak-point drawer
  - inspect /notes/[id] layout
  - inspect LaTeX rendering

When reporting back:

- Lead with findings or completed tasks.
- Explicitly list failed or unverified checks.
- Do not claim complete if validation.md lacks evidence.
```
