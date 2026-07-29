# Tasks — Git Cleanup And Public Push

> Status: `completed with deployment blocked`
>
> Rule: Do not stage, commit, push, or deploy until this task list is explicitly approved by the user.

## Approval Gate

- [x] User approves this `tasks.md` for execution.

## GCP-01 — Preflight And Scope Check

- [x] Record current branch, remote, and dirty status.
- [x] Check for secrets/build caches that must not be staged.
- [x] Check whether deploy config and deployment scripts exist.
- [x] Decide whether deployment can proceed or must be blocked on missing config.

## GCP-02 — Local Validation

- [x] Run backend pytest: `cd backend && .venv/bin/python -m pytest tests/ -ra`.
- [x] Run Alembic current: `cd backend && PYTHONPATH=. .venv/bin/alembic current`.
- [x] Run TypeScript: `npx tsc --noEmit`.
- [x] Run frontend build: `npm run build`.
- [x] Run setup check: `npm run check`.
- [x] Run whitespace check: `git diff --check`.

## GCP-03 — Git Cleanup, Commit, Push

- [x] Stage the approved current update set.
- [x] Inspect staged stat and ensure no secrets/caches are staged.
- [x] Commit with a release/acceptance message.
- [x] Push to the configured remote branch.

## GCP-04 — Public Deployment

- [x] Create an isolated deployment worktree from the pushed commit if deployment config exists. Skipped: deployment config does not exist in the pushed commit.
- [x] Install dependencies in the deploy worktree. Skipped: deployment config does not exist in the pushed commit.
- [x] Prepare required generated/ignored build inputs without copying unrelated local state. Skipped: deployment config does not exist in the pushed commit.
- [x] Run the existing Cloudflare/OpenNext deploy command if available. Skipped: no existing deploy command is available in the pushed commit.
- [x] If deploy config is missing, record blocker instead of inventing a new deploy path.

## GCP-05 — Public Verification

- [x] Verify `https://blog.limengyang.me/`. Skipped: no new public deployment was run.
- [x] Verify `https://blog.limengyang.me/blog`. Skipped: no new public deployment was run.
- [x] Verify `https://blog.limengyang.me/notes`. Skipped: no new public deployment was run.
- [x] Verify `https://blog.limengyang.me/manage`. Skipped: no new public deployment was run.
- [x] Verify `https://public-api.limengyang.me/api/health`. Skipped: no new public deployment was run.
- [x] Record deployment and verification results.

## Closure

- [x] Update `validation.md`.
- [x] Update `diff-report.md`.
- [x] Update final workflow status.

## Stop Rule

- [x] If validation, git push, or deployment is blocked, record evidence and stop instead of using destructive or speculative fixes.

---

## 2026-07-29 Release Run

> Status: `GCP-R2-03 passed; executing GCP-R2-04`
>
> Approval required: the user must explicitly approve `GCP-R2-01` through
> `GCP-R2-06`. The previous run's approval does not authorize this run.

### GCP-R2-01 — Publication Inventory And Safety Review

- [x] Fetch `mine` and confirm current ahead/behind state without rebasing or merging.
- [x] Record the exact modified and untracked file inventory.
- [x] Review authenticated screenshots and browser-observation JSON for personal,
      credential, session, internal-path, or private-data exposure.
- [x] Review migration/recovery manifests and reports for owner identifiers,
      database details, personal data, secrets, dumps, and local-only paths.
- [x] Classify every candidate as `publish`, `exclude`, or `needs user decision`.
- [x] Record the classification in `diff-report.md`.

### GCP-R2-02 — Non-destructive Tree Cleanup

- [x] Resolve the duplicated nested `C6-C12-REVIEW-REPORT.md` location only if its
      correct owner path is unambiguous; otherwise stop for a user decision.
- [x] Do not delete, reset, checkout, or discard any existing user file.
- [x] Confirm no cache, environment, key, database, dump, or credential file will
      be staged.

### GCP-R2-03 — Validation

- [x] Run `git diff --check`.
- [x] Run documentation/link checks available in the repository.
- [x] Run `npm run predeploy:check` from a clean commit candidate or isolated
      worktree; initial run was blocked by 10 high vulnerabilities, dependency
      remediation candidate revalidation passed with 0 vulnerabilities,
      frontend 58/58, backend 300/300, Alembic 025, TypeScript and Cloudflare
      build all passing.
- [x] Record the first relevant failure and stop if a fail-closed gate fails.

### GCP-R2-04 — Stage, Commit, And Push

- [x] Stage only paths classified `publish`.
- [x] Inspect `git diff --cached --name-status` and `--stat`.
- [x] Re-run the sensitive-file scan against the staged set.
- [x] Commit the approved documentation/release evidence.
- [ ] Push `notes-workspace-ux-upgrade` to `mine` without force.
- [ ] Confirm local HEAD equals the upstream branch after push.

### GCP-R2-05 — Isolated Public Deployment

- [ ] Create a detached isolated worktree from the exact pushed commit.
- [ ] Install dependencies using the repository lockfile.
- [ ] Prepare only required generated/ignored build inputs.
- [ ] Run the repository's fail-closed predeploy gate.
- [ ] Run the existing `deploy:full` command only if every prerequisite passes.

### GCP-R2-06 — Public Verification And Closure

- [ ] Verify the public home, blog, notes, mistakes, and manage boundaries.
- [ ] Verify `https://public-api.limengyang.me/api/health`.
- [ ] Record the deployed commit and Worker/version evidence.
- [ ] Update `validation.md`, `diff-report.md`, and this task status.
- [ ] Confirm whether `git status --short` is empty; if not, list every retained
      item and why it was not published or removed.
