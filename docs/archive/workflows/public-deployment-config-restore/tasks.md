# Tasks — Public Deployment Config Restore

> Status: `completed`
>
> Rule: Do not restore config, install dependencies, commit, push, or deploy until this task list is explicitly approved by the user.

## Approval Gate

- [x] User approves this `tasks.md` for execution.

## PDR-01 — Restore Deployment Config

- [x] Restore `open-next.config.ts`.
- [x] Restore `wrangler.toml`.
- [x] Restore package scripts for `build:cf`, `preview`, `deploy`, `deploy:full`, and `cf-typegen`.
- [x] Restore required package dependencies for OpenNext/Cloudflare.
- [x] Update lockfile through package manager, not by manual editing.

## PDR-02 — Local Validation

- [x] Run `npx tsc --noEmit`.
- [x] Run `npm run build`.
- [x] Run `npm run build:cf`.
- [x] Run `git diff --check`.

## PDR-03 — Commit And Push Restore

- [x] Stage only deployment restore and workflow evidence.
- [x] Commit restore.
- [x] Push to `mine/notes-workspace-ux-upgrade`.

## PDR-04 — Public Deploy

- [x] Run `npx wrangler whoami`.
- [x] Run `npm run deploy:full`.
- [x] Record Cloudflare deployment output.

## PDR-05 — Public Verification

- [x] Verify `https://blog.limengyang.me/`.
- [x] Verify `https://blog.limengyang.me/blog`.
- [x] Verify `https://blog.limengyang.me/notes`.
- [x] Verify `https://blog.limengyang.me/manage`.
- [x] Verify `https://public-api.limengyang.me/api/health`.
- [x] Record verification in `validation.md`.

## Closure

- [x] Update `diff-report.md`.
- [x] Update final workflow status.

## Stop Rule

- [x] If restore, validation, push, deploy, or public verification is blocked, record evidence and stop without speculative fixes.
