# Tasks

Implementation must not start until this task list is explicitly approved in the conversation.

## Phase 0: Scope Audit

- [x] **C0-01** Capture baseline branch, upstream relation, staged state, and full worktree path inventory. Baseline: branch `notes-workspace-ux-upgrade`, upstream `mine/notes-workspace-ux-upgrade`, ahead 1/behind 0, no staged paths; mixed tracked and untracked changes remain.
- [x] **C0-02** Classify changed paths into proposed commit groups, exclusions, and `待人工确认`; identify any overlap with existing task groups. Classification is recorded in `diff-report.md`.
- [x] **C0-03** Present the exact proposed path scope and commit message(s) for user approval. User approved groups A–H, including migrations and deletion of `backend/app/routers/chapters.py`.

## Phase 1: Precise Staging

- [x] **C1-01** Stage only the user-approved explicit paths; leave excluded and uncertain paths untouched. Staged 256 explicit baseline paths; no unstaged or untracked paths remain.
- [x] **C1-02** Verify cached names, diff summary, patch correctness, and whitespace errors. Cached scope is 190 added, 65 modified, 1 deleted; `git diff --cached --check` reports existing whitespace issues in approved docs and one migration line.

## Phase 2: Validation And Commit

- [x] **C2-01** Run validation appropriate to the approved staged domains and record failures as pre-existing, in-scope, or blocked. TypeScript passed; full backend tests passed (244); frontend tests passed (26); Alembic `check` remains failed on knowledge-point index/constraint drift; cached whitespace check remains failed on approved docs and one migration line.
- [x] **C2-02** Create the approved commit(s) with clear messages. Primary commit: `d02764c feat: close personal learning system batches 2-7`.
- [x] **C2-03** Record commit hash, validation evidence, remaining dirty paths, and whether push was intentionally not performed. Primary commit was created successfully; post-commit worktree is clean and push was intentionally not performed.

## Phase 3: Optional Publish

- [ ] **C3-01** Only if separately requested: push the specific committed branch and verify the remote result.
