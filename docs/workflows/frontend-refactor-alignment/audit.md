# Initial Differential Audit

## Baseline

- Current repository and supplied worktree both resolve to commit 202ea14d3362a84a491a7a8e32d2afd5d2e0bc1f.
- Current worktree contains unrelated untracked documents. They are out of scope and must be preserved.
- This audit is source-only. No runtime, database, browser, or deployment claim is made.

## Findings

| Topic | Documentation claim | Source evidence | Status |
| --- | --- | --- | --- |
| Workspace route | Older refactor plans propose src/app/workspace and /workspace as the unified entry. | src/app/workspace is absent; src/app/manage/(workspace) exists; legacy write routes remain. | Historical proposal, not current implementation. |
| Unified editor | Older plans propose one UnifiedEditor for note, blog, and mistake. | No UnifiedEditor exists. write-note has NoteToolbar, useNoteEditor, preview, slash commands, and AI panel; write and write-mistake remain separate. | Partially realized only for notes. |
| GitHub sync removal | Older implementation plans list sync removal as future work. | backend/app/services/github_sync.py and backend/app/routers/sync.py are absent; README says PostgreSQL/backend API is the supported content path. | Implemented; stale task text remains. |
| Visual system | Design plan proposes a central glassmorphism stylesheet and Tailwind extension. | No proposed stylesheet, demo component, or Tailwind config exists; source uses runtime theme variables and component-level backdrop-blur classes. | Direction is present, centralized implementation is absent. |
| Markdown security PoC | Supplied workspace proposes a unified/remark/rehype proof of concept. | Current source still uses marked and html-react-parser; target packages are not installed. | Planned only; not an implementation delta. |

## Implication

The broad refactor plan must be decomposed into current-state follow-ups. A future task must not infer that /workspace, a one-editor architecture, or a centralized design system already exists. A future Markdown task must not claim a security-boundary migration from the existing renderer.

## Document-to-Source Matrix

| Document set | Material assertion | Current source comparison | Classification |
| --- | --- | --- | --- |
| docs/refactor-plan/00-CORRECTED-PHASED-PLAN.md | A new /workspace route exists or should be the immediate shared owner. | src/app/workspace is absent. The existing private work area is the route group src/app/manage/(workspace); its existence does not create the URL /workspace. | Contradicted as present state; retain only as a historical option. |
| docs/refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md | Legacy write routes can be deleted after a new unified create route is introduced. | src/app/write, src/app/write-note, and src/app/write-mistake all remain. No replacement create route or compatibility decision was found in this audit. | Planned, not executable. |
| docs/refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md | A UnifiedEditor will own note, blog, and mistake editing. | No UnifiedEditor symbol exists. The note editor is enriched, while blog and mistake edit flows remain independently owned. | Partially implemented at capability level only. |
| docs/refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md | GitHub sync removal is a future deletion step. | The named sync router and service are absent. Root README identifies PostgreSQL and backend APIs as the supported content path. | Completed implementation; future-tense wording is stale. |
| docs/refactor-plan/02-UI-DESIGN-SYSTEM-BLUE-WHITE.md | A dedicated glassmorphism stylesheet and Tailwind extension establish the system. | The proposed files do not exist. src/app/layout.tsx supplies theme CSS variables and components independently use backdrop-blur and related utility classes. | Design direction partially present; proposed implementation absent. |
| docs/note-editor-tasks.md | Toolbar, editor hook, preview, slash command, and AI panel are pending implementation items. | Both write-note pages import and use useNoteEditorTab, useNoteEditor, NoteToolbar, NotePreviewContent, SlashCommandMenu, and AIAssistantPanel. | Stale task state; source shows implementation present. |
| docs/roadmap-design.md | The note-editor capability set is complete at the feature level. | Source imports establish integration for the listed note-editor components, but this audit did not run browser or failure-path validation. | Source-backed partial verification; runtime acceptance remains unverified. |
| Supplied markdown-rendering-security-poc | unified/remark/rehype is the target security boundary. | package.json and source still use marked and html-react-parser. The target packages are absent. | Planned only. |
| Supplied markdown-rendering-security-poc | Existing rendering must not be treated as a proven security fallback. | Current renderer creates HTML strings; MarkdownMath inserts generated HTML with dangerouslySetInnerHTML. | Supported concern; production migration must remain separately gated. |

## Correction Ledger

| Stale location | Safe replacement statement | Evidence owner |
| --- | --- | --- |
| refactor-plan/00-CORRECTED-PHASED-PLAN.md sections 2A, 3, and 4 | /workspace is a proposed route family, not a current route. Legacy writer routes remain until a separately approved compatibility task decides otherwise. | src/app route inventory |
| refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md route and editor sections | Current implementation has a private manage workspace plus separate writer surfaces; no shared UnifiedEditor has been adopted. | src/app/manage/(workspace), src/app/write, src/app/write-note, src/app/write-mistake |
| refactor-plan/03-IMPLEMENTATION-PLAN-KEEP-VISUAL.md sync-removal section | GitHub sync removal is complete in source; do not plan a second deletion. Verify any old document reference before removing related text. | root README and backend/app file inventory |
| note-editor-tasks.md pending component items | Listed note-editor building blocks are source-present. Keep test and browser acceptance status separate from source presence. | src/app/write-note pages and components |
| roadmap-tasks.md historical GitHub-sync references | Do not treat historical sync tasks as active product behavior; root README declares the supported persistence path. | root README |
| markdown-rendering-security-poc | The PoC is a future isolated renderer experiment. It is not proof of a production migration or a license to replace consumers. | package.json and current renderer |
