# Validation

Status: `COMPLETE — D2 OPTION A; E1～E5 COMPLETE; G4 PASS FOR F4 INPUT ONLY`

The parent F4-before workspace was reorganized on 2026-08-16 and D1 option B was selected. G2 and G3 now pass for F3 evidence only. This planning workspace has not changed UI behavior, content contracts, authentication, or any production renderer.

## E1 validation (2026-08-16)

Conclusion: `PASS — read-only current-source inventory`.

- Read `README.md`, `design.md`, `requirements.md`, `tasks.md` and `validation.md` in this workflow before beginning; `audit.md` did not previously exist and is created as the E1 evidence record.
- Source inventory commands: `rg --files src/app | rg '/(write|write-note|write-mistake)/|blog-preview|rich-text|markdown' | sort`; structural `rg` across all write/write-note/write-mistake pages, components and hooks; full reads of principal blog store/publish/preview, note create/edit/editor hook, mistake forms/pages, `src/lib/api/notes.ts`, `backend/app/schemas/note.py`, `backend/app/routers/notes.py`, and `src/components/auth-gate.tsx`.
- Verified facts are in `audit.md`: separate blog/note/mistake owner paths, typed Note save APIs, production preview owners, mutation-level `get_current_admin`, typed mistake fields/review attributes, and page-level AuthGate coverage. The legacy `/write/[slug]` page-level gap is recorded as a later E3 constraint, not fixed here.
- No source files or dependencies were edited; no test/server/browser, real data/API, credential, `AUTH_BYPASS`, route, renderer, schema, Git, deployment or visual action was used. E2 is the only next item.

## E2 validation (2026-08-16)

Conclusion: `PASS — evidence-backed capability matrix only`.

- Read additional current owners: `src/app/write/components/sidebar.tsx`, `editor.tsx`, `actions.tsx`, `preview.tsx`, `src/app/write-note/components/note-toolbar.tsx`, `slash-command-menu.tsx`, and the relevant field/save regions of both mistake forms. The command set searched `textarea|tags|summary|category|cover|preview|save|createNote|updateNote|status|hidden|revision|version` across the three editor paths.
- The E2 matrix in `audit.md` cites only observed owner/API behavior. It limits future shared candidates to mutation DTO boundary, tag/save-state support and a blog/note-only selection/insert/wrap core; it excludes a universal editor, preview, AI, uploads, versioning, review fields and route access from any common primitive claim.
- No implementation, source/test dependency, schema, route, backend permission, Markdown renderer, browser/service, real data/API/credential, `AUTH_BYPASS`, Git, deployment or visual change occurred. E3 is the only next item.

## E3 validation (2026-08-16)

Conclusion: `PASS — source-backed fields, save, preview and permission freeze`.

- Read and searched current `backend/app/schemas/note.py`, `backend/app/routers/notes.py`, `backend/app/routers/review.py`, `backend/app/routers/ai.py`, `src/lib/api/notes.ts`, the note edit payload, both mistake forms, and preview/AuthGate owners. The targeted search covers `expected_revision`, review attributes, `get_current_admin`, optional public reads, upload, AI and staged mistake routes.
- `audit.md` records every requested matrix: fields, save/concurrency, preview and public/private/route/backend boundary. It explicitly preserves all required mistake fields and review attributes as first-class data, identifies the two current update-concurrency modes, and states that AI/upload/review remain protected and optional to save.
- No source/schema/API/permission/route/renderer/preview behavior changed; no test/server/browser, real data/API/credential, `AUTH_BYPASS`, Git, deployment, visual work or F4 action occurred. E4 is the only next item.

## E4 validation (2026-08-16)

Conclusion: `PASS — two evidence-bounded directions and rollback boundary; D2 REQUIRED`.

- `design.md` compares Option A (minimal shared primitives + domain-editor coexistence) and Option B (larger unified owner) against the E1 inventory, E2 matrix and E3 contracts. Option A is the only supported future direction; Option B remains a documented high-risk alternative, not a recommendation or authorization.
- Option A rollback is import/adaptor level and preserves all current schema, typed DTOs, route owners, renderer owners, mutation protection and first-class mistake/review data. Option B cannot claim a rollback or validation plan without a later approved prototype/design because its required contract normalization is not evidenced.
- No source/schema/API/permission/route/renderer/preview/test/service/browser/real data/API/credential/`AUTH_BYPASS`/Git/deployment/visual/F4 action occurred. E5 and G4 are blocked until the user chooses D2.

## D2 validation (2026-08-16)

Conclusion: `PASS — user decision recorded; E5 documentation only`.

- User selected Option A: minimal shared primitives with domain-editor coexistence.
- This decision releases E5 to write an implementation task list only. It does not release source implementation, route/AuthGate changes, schema/API/renderer changes, visual work, Git, deployment or F4.
- E1–E4 evidence and all frozen field/save/preview/permission boundaries remain the required inputs for E5; G4 waits for that list.

## E5 validation (2026-08-16)

Conclusion: `PASS — separately gated implementation list only`.

- Created [Option A implementation task list](implementation-tasks.md). It has an explicit `NOT APPROVED FOR IMPLEMENTATION` status, requires fresh approval/worktree inventory, and gives every future task a narrow boundary, test-first expectation, validation and import/adaptor rollback condition.
- It expressly excludes a unified editor, schema/API/route/renderer migration, mistake flattening, permission relaxation, production Markdown work, visual work, Git and deployment. The legacy blog edit page gate issue is a separate security task, not a hidden extraction side effect.
- No implementation or source/test/runtime action occurred. G4 is the only next item.

## G4 validation (2026-08-16)

Conclusion: `PASS — F4 input only`.

- Evidence chain: E1 source inventory, E2 capability matrix, E3 field/save/preview/permission matrices, E4 comparison/rollback, D2 Option A, and E5 separately gated implementation tasks. All current editor contracts requested by the parent are represented in `audit.md`, `design.md` and `implementation-tasks.md`.
- Residual risk remains visible: legacy `/write/[slug]` source lacks page-level `AuthGate`; current optimistic-concurrency behavior differs by owner; preview remains on the unchanged production renderer. Existing backend `get_current_admin`, AI/upload/review protection, public-read filtering, typed mistake/review fields and route owners are unchanged.
- No runtime/source implementation was performed. G4 permits only the parent F4 input package, never F4 execution, editor extraction, security remediation, schema/route/renderer work, Git or deployment.
