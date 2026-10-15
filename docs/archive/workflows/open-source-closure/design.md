# Design

## Problem Summary

The repository currently mixes two persistence models:

- legacy static-file publishing under `src/` and `public/`
- backend-managed content under `backend/`

GitHub sync acts as the bridge between them, but it also keeps sensitive write credentials in the architecture, exposes private-content export risk, and makes the project harder for open-source contributors to understand.

## Target State

The project should move toward this simpler model:

- backend database is the source of truth for active managed content
- frontend writes through backend APIs only
- public reads come from explicit backend/public routes or intentionally static assets
- GitHub repository write automation is not part of the default product architecture
- GitHub visitors can understand the repository in Chinese
- repository authorship is represented honestly as an adaptation of an original open-source project
- contributors have CI, setup templates, issue/PR templates, and validation commands before opening changes
- GitHub-facing materials are mixed Chinese/English, with Chinese carrying the main explanation and English labels/aliases helping non-Chinese tooling and contributors

## Architectural Approach

### 1. Remove the sync domain from active code paths

- Remove frontend calls through `src/lib/api/sync.ts`.
- Remove backend `/api/sync/*` routes from the supported app flow.
- Remove backend GitHub write service usage.
- Replace any save/publish UX that depends on sync with backend-native save behavior or retire the UI affordance.

### 2. Reclassify content domains

Each user-facing domain should be placed in one of two buckets:

- backend-managed domain
- intentionally static legacy domain

This task should focus first on the active managed domains:

- `notes`
- `mistakes`
- `review`
- `manage`
- `blog` if it is still presented as an editable workflow

Legacy static domains can stay temporarily static if they are clearly documented and no longer depend on GitHub sync writes.

Current classification from source inspection on 2026-06-10:

- Backend-managed now:
  - `notes`
  - `mistakes`
  - `review`
  - `manage`
  - `blog`
- Static-source now:
  - home site settings (`src/config/site-content.json`, `src/config/card-styles.json`)
  - `about`
  - `share`
  - `projects`
  - `pictures`
  - `snippets`
  - `bloggers`

Chosen implementation direction on 2026-06-10:

- This task will maximize full-project migration, not retire edit features.
- Static-source editable domains will be migrated onto backend APIs in this round where feasible.
- Read-only preservation without editing is not the default strategy for this task.

Implementation consequence:

- GitHub sync removal can proceed immediately for backend-managed domains.
- Static-source editable domains need route-by-route backend API replacement before sync code is deleted from the supported UI.

### 2A. Migration strategy for legacy static editable domains

Preferred order:

1. Introduce backend contracts for each static editable domain.
2. Switch frontend pages from local `list.json` save pipelines to backend read/write APIs.
3. Preserve existing public rendering shape where possible so UI churn stays low.
4. Only after frontend migration is complete, remove the matching GitHub sync helpers and route dependencies.

Likely migration buckets:

- Structured list domains:
  - `share`
  - `projects`
  - `bloggers`
- Media-backed structured domains:
  - `pictures`
- Simple text/config domains:
  - `about`
  - `snippets`
  - home site settings

Shared backend primitives may be introduced if they reduce duplication, but the design should avoid a vague "misc JSON blob" architecture unless the schema is still explicit at the API layer.

### 3. Tighten public read boundaries

Because sync removal changes the public exposure story, note APIs must enforce:

- anonymous access only to public-safe content
- admin-only access to hidden/draft/internal content

This is a required companion change, not an optional cleanup.

### 4. Finish open-source release hygiene

After the write-path removal, contributors still need a coherent setup story:

- package manager instructions
- backend/frontend env expectations
- security reporting guidance
- contribution guidance

### 5. Chinese GitHub-facing content and upstream attribution

This extension should update repository-facing content, not runtime product flows.

Primary targets:

- `README.md`: Chinese overview, project lines, local setup, content source-of-truth model, configuration, and a visible source/thanks section.
- `CONTRIBUTING.md`: Chinese contribution workflow and architecture boundaries.
- `SECURITY.md`: Chinese security reporting and environment security guidance.
- `LICENSE`: preserve existing license text unless the original project attribution requires an additional notice.

Attribution strategy:

1. Keep the statement factual: this repository is adapted from an original open-source project.
2. If the upstream name or URL is discoverable in the repository, cite it directly.
3. If the upstream name or URL is not discoverable, use a placeholder-safe statement that does not invent details, and mark the missing upstream detail in validation.
4. Do not remove existing license text or imply the current maintainer authored the original project.

Chinese content style:

- Use Chinese as the primary language.
- Keep commands, paths, API names, and environment variable names unchanged.
- Avoid marketing-style copy; this is a personal knowledge/blog system and contributor-facing repository.

### 6. Full open-source preparation

This extension should fill the structural gaps from `audit.md` without changing product behavior.

Planned repository surfaces:

- `.github/workflows/ci.yml`
  - Run frontend dependency install, TypeScript check, and build where feasible.
  - Run backend dependency install, tests, and import/startup checks.
  - Avoid production secrets and deployment commands.
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/pull_request_template.md`
  - Use mixed Chinese/English fields.
  - Ask for scope, validation, screenshots when relevant, and security/env impact.
- `.env.example`
  - Document public frontend variables such as API URL.
- `backend/.env.example`
  - Align with `backend/app/config.py`.
  - Use placeholder values only.
- `README.md`
  - Add database bootstrap, Alembic migration, validation matrix, and contributor navigation.
- `package.json`
  - Add open-source metadata: `license`, `repository`, `bugs`, `homepage`.
  - Keep `"private": true` unless publishing to npm becomes an explicit goal.
- one-command local setup/check entry
  - Prefer platform-neutral scripts such as `npm run init` and `npm run check`.
  - Do not document any platform-specific deployment path in this phase.
  - Provide two setup levels:
    - `npm run init`: conservative guided setup for contributors who already have Node.js, Python, and PostgreSQL or want to configure them manually.
    - `npm run setup`: fuller local all-in-one setup that can use Docker-backed PostgreSQL when available and can offer to install missing prerequisites.
  - Detect prerequisites before acting:
    - Node.js and npm.
    - Python and virtual environment support.
    - PostgreSQL client/server or Docker.
    - Required ports for local development.
  - Installation policy:
    - Always provide check-only/dry-run output before changing local files or system state.
    - Automatic installation is allowed only for explicitly supported OS/package-manager combinations.
    - Unsupported environments should receive manual commands and stop before mutation.
    - `sudo` or administrator-level actions must never be implicit.
  - Database policy:
    - `npm run init` should work with an existing PostgreSQL URL.
    - `npm run setup` may offer Docker-backed PostgreSQL only if Docker is already installed or the user explicitly approves the documented install path.
    - If no Docker Compose file is implemented in this phase, setup must not pretend to provide full Docker database automation; it should print the exact manual next step.
  - Confirm AI configuration during setup:
    - Ask whether to configure AI now or skip.
    - If skipped, leave AI keys empty and explain that AI features will be disabled or degraded.
    - If configured, ask which providers to enable from a preset registry plus custom OpenAI-compatible endpoint.
    - Ask which capability/purpose each configured provider should serve:
      - General assistant / 通用模型.
      - Text generation and analysis / 文本生成与分析.
      - OCR and vision recognition / 图像识别.
      - Image generation / 图像生成.
    - Suggested presets:
      - OpenAI-compatible custom endpoint.
      - DashScope/Qwen.
      - DeepSeek.
      - OpenAI.
      - OpenRouter.
      - Gemini.
      - xAI.
      - Claude/Anthropic.
      - Moonshot/Kimi.
      - Zhipu/GLM.
      - SiliconFlow.
      - Volcengine/Doubao.
      - Tencent Hunyuan if an OpenAI-compatible endpoint is used.
      - Baidu Qianfan if an OpenAI-compatible endpoint is used.
      - Local OpenAI-compatible runtime, such as Ollama or LM Studio.
    - For every preset, allow overriding base URL and model before writing env.
    - For providers whose native API is not OpenAI-compatible in the current runtime, label the preset as requiring a compatible gateway or a future provider adapter.
    - Runtime mapping:
      - DashScope/Qwen maps to `DASHSCOPE_*`.
      - DeepSeek maps to `DEEPSEEK_*`.
      - Custom/OpenAI-compatible providers map to `AI_*`.
      - Image generation maps to `DASHSCOPE_IMAGE_*` in the current codebase.
      - Additional presets such as OpenAI, OpenRouter, Gemini, xAI, Claude/Anthropic, Moonshot/Kimi, Zhipu/GLM, SiliconFlow, Volcengine/Doubao, Hunyuan, Qianfan, Ollama, and LM Studio are setup presets only unless they use an OpenAI-compatible endpoint accepted by `AI_BASE_URL`.
    - Current runtime behavior to surface in setup copy:
      - General uses `call_general_model()` and currently reads `DASHSCOPE_*` or fallback `AI_*`.
      - Text generation/analysis uses `call_text_model()` / `call_text_model_no_json()` and prefers `DEEPSEEK_*`.
      - OCR/vision recognition uses `call_ocr_model()` and prefers `DASHSCOPE_*`.
      - Image generation uses `DASHSCOPE_IMAGE_*` in `diagram_service.py`; it is separate from OCR/vision recognition.
    - Write provider values to env files only after user confirmation.
    - Mask API keys in all summaries.
    - Do not require live API calls during setup; offer a separate check command if needed later.
  - Confirm administrator credentials and keys during setup:
    - Generate `JWT_SECRET_KEY` locally by default and never reuse the template value.
    - Ask whether public registration should be disabled, open for local development, or protected by a generated `REGISTRATION_KEY`.
    - Generate `REGISTRATION_KEY` only when the user chooses protected registration.
    - Ask whether to enable operator passkey registration; if yes, generate `OPERATOR_REGISTRATION_KEY` and show it once with a save warning.
    - Offer to run the existing backend admin CLI for password setup after migrations: `python -m app.cli set-password`.
    - Offer passkey registration as an optional follow-up using the existing CLI: `python -m app.cli register-passkey`.
    - Mask generated keys in normal summaries and write them only to local env files.
  - Ask for explicit permission before installing missing programs or changing system-level state.
  - Generate project configuration only from templates and placeholders, never from local secrets.

Docker Compose is useful but not required for the first complete preparation pass. It can be deferred if it would create new maintenance work or require decisions about local database defaults. If deferred, the setup wizard must clearly say Docker database automation is not enabled yet.

## Risks

1. Some routes may still assume static-file publish outputs exist.
2. Migrating many static domains in one round can encourage over-generic backend abstractions if not kept explicit.
3. Removing sync too early without replacing save flows could strand management UI actions.
4. Documentation cleanup alone will not fix architectural ambiguity unless each supported domain is explicitly classified.
5. Some public routes may still import checked-in JSON during the migration window, so read path and write path may briefly diverge unless each domain is migrated end-to-end.
6. Attribution can become inaccurate if upstream project identity is guessed instead of verified from repository evidence.
7. Translating docs can accidentally weaken security warnings if the wording becomes too casual.
8. CI can become noisy if it runs production deployment paths or checks that require unavailable secrets.
9. Environment templates can accidentally expose real local values if copied from `.env` instead of config defaults and placeholders.
10. Changing package metadata can overstate package publishability if `"private": true` is removed without an npm release plan.
11. One-command deployment can become misleading unless the target platform is explicitly chosen, so this phase should only provide one-command setup/check flow.
12. Automatic prerequisite installation can be unsafe if it silently mutates the user's machine, so every system-level action must be confirmed first.
13. AI keys are sensitive and provider-specific, so the setup wizard should treat AI configuration as optional and mask secrets in output.
14. Adding provider presets can create false confidence if APIs differ, so presets should use OpenAI-compatible endpoints only unless a provider-specific adapter is implemented.
15. Gemini, xAI, and Claude should be exposed carefully in setup copy because their native APIs may not match the existing OpenAI-compatible call path without an adapter or gateway.
16. Admin setup can lock users out if keys are lost, so generated registration/operator keys should be shown once, written to env, and accompanied by a clear "save this now" warning.

## Validation Strategy

- Static validation: `npx tsc --noEmit`
- Targeted backend import or startup checks where environment allows
- Source inspection for removed sync imports and routes
- Browser verification for public notes behavior and admin management paths when implementation starts
- For documentation-only Phase 5: source inspection of changed docs, link/path checks, and no code validation unless implementation files change
- For full open-source preparation: inspect new GitHub templates, run or dry-check CI commands locally where feasible, run `npx tsc --noEmit`, run backend import/test checks, and record blockers in `validation.md`
