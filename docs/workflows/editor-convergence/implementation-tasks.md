# Option A Editor Convergence Implementation Tasks

Status: `DESIGN OUTPUT ONLY — NOT APPROVED FOR IMPLEMENTATION`.

This is the D2 Option A task list: minimal shared primitives with domain-editor coexistence. It is a future implementation proposal, not implementation authorization. Before any checkbox can be executed, the user must explicitly approve this file (or a scoped successor) in conversation after reviewing the exact source/test file list and current dirty worktree.

## Non-negotiable scope

- Keep `/write*`, `/write-note*` and `/write-mistake*` as separate route/component owners.
- Keep `note`, `blog` and `mistake` as typed Note contracts. Never replace the mistake fields or review state with Markdown `content`.
- Preserve current backend `get_current_admin`, strict `AuthGate` pages, public read filtering, HttpOnly Cookie session, protected AI/upload/review dependencies, existing preview owners and no production Markdown migration.
- Do not include a route move, visual redesign, unified editor, schema migration, JWT/Bearer/CORS work, data migration, Git or deployment.

## Separate approval gate

- [ ] EC-A0. Obtain explicit implementation approval after re-reading `AGENTS.md`, current `git status --short`, this task list, the E1–E4 audit and the exact candidate source/test files. Stop if the dirty worktree conflicts with any target.

## Characterize before extraction

- [ ] EC-A1. Add focused characterization tests for the two candidate domains only: blog and note selection/insert/wrap behavior, image-placeholder or paste behavior, tag/save pending/error outcomes, and each route's preview handoff. Retain any first failing evidence; do not test against personal content or a production API.
- [ ] EC-A2. Add contract tests proving `NoteCreate`/`NoteUpdate` payloads preserve each owner’s current fields and keep note edit `expected_revision` behavior distinct from legacy blog and standard mistake update behavior.
- [ ] EC-A3. Add negative contract tests that mistake’s `subject`, `difficulty`, `question`, `my_answer`, `correct_answer`, `analysis`, `knowledge_points`, `images`, `ai_metadata`, `ef`, `interval`, `repetitions`, `next_review` and `last_reviewed` are not flattened, reset or made dependent on AI.

## Minimal shared primitives only

- [ ] EC-A4. Extract a pure, blog/note-only selection/insert/wrap helper behind explicit adapters. Do not move toolbar, slash-command, preview or route ownership; retain focused tests and a direct rollback path.
- [ ] EC-A5. Extract only evidence-backed tag normalization and save-state support if EC-A1 proves equivalent inputs/outputs. Keep each route’s labels, metadata fields, confirmation UX and navigation owner local.
- [ ] EC-A6. Adopt each primitive in one owner at a time, first blog or note as chosen by fresh evidence, then rerun the characterization suite before considering the second owner. Do not change mistake owners.

## Deferred separate security work

- [ ] EC-SEC-01. Treat the legacy `/write/[slug]` missing page-level `AuthGate` as a separately approved security task. It must verify route behavior and preserve backend `get_current_admin`; it must not be bundled into primitive extraction or use a UI-only protection substitute.

## Validation and rollback

- [ ] EC-A7. Run affected Vitest/TypeScript/Prettier and appropriate isolated browser checks. Verify public routes stay public, private pages remain strict, no public page requests admin-only APIs, and backend write/AI/upload/review protections remain unchanged.
- [ ] EC-A8. Record exact commands, counts, warnings, artifacts and residual risks in the new implementation workspace. If a candidate changes field/save/preview/permission semantics, revert that candidate’s imports/adapters and mark it BLOCKED rather than broadening scope.

## Out of scope / stop conditions

- Any unified editor owner, mobile route move, schema/API migration, renderer cutover, production Markdown consumer switch, visual work, real data/credential/API, `AUTH_BYPASS`, dependency change, Git, deployment or a new persistent browser download requires separate authority.
- No later green test authorizes F4. F4 remains a separate input-package and execution gate.
