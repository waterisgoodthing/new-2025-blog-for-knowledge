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

## Risks

1. Some routes may still assume static-file publish outputs exist.
2. Migrating many static domains in one round can encourage over-generic backend abstractions if not kept explicit.
3. Removing sync too early without replacing save flows could strand management UI actions.
4. Documentation cleanup alone will not fix architectural ambiguity unless each supported domain is explicitly classified.
5. Some public routes may still import checked-in JSON during the migration window, so read path and write path may briefly diverge unless each domain is migrated end-to-end.
6. Attribution can become inaccurate if upstream project identity is guessed instead of verified from repository evidence.
7. Translating docs can accidentally weaken security warnings if the wording becomes too casual.

## Validation Strategy

- Static validation: `npx tsc --noEmit`
- Targeted backend import or startup checks where environment allows
- Source inspection for removed sync imports and routes
- Browser verification for public notes behavior and admin management paths when implementation starts
- For documentation-only Phase 5: source inspection of changed docs, link/path checks, and no code validation unless implementation files change
