# Tasks — Git Cleanup And Public Push

> Status: `in progress`
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

- [ ] Stage the approved current update set.
- [ ] Inspect staged stat and ensure no secrets/caches are staged.
- [ ] Commit with a release/acceptance message.
- [ ] Push to the configured remote branch.

## GCP-04 — Public Deployment

- [ ] Create an isolated deployment worktree from the pushed commit if deployment config exists.
- [ ] Install dependencies in the deploy worktree.
- [ ] Prepare required generated/ignored build inputs without copying unrelated local state.
- [ ] Run the existing Cloudflare/OpenNext deploy command if available.
- [ ] If deploy config is missing, record blocker instead of inventing a new deploy path.

## GCP-05 — Public Verification

- [ ] Verify `https://blog.limengyang.me/`.
- [ ] Verify `https://blog.limengyang.me/blog`.
- [ ] Verify `https://blog.limengyang.me/notes`.
- [ ] Verify `https://blog.limengyang.me/manage`.
- [ ] Verify `https://public-api.limengyang.me/api/health`.
- [ ] Record deployment and verification results.

## Closure

- [ ] Update `validation.md`.
- [ ] Update `diff-report.md`.
- [ ] Update final workflow status.

## Stop Rule

- [ ] If validation, git push, or deployment is blocked, record evidence and stop instead of using destructive or speculative fixes.
