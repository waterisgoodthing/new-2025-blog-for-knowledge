# Validation

Validation date: 2026-06-15.

## Scope

Validated the new music auto-deploy script without running a live deployment.

## Commands

- `test -f scripts/watch-mymusic-deploy.sh && bash -n scripts/watch-mymusic-deploy.sh`
  - Result: initial RED check failed because the script did not exist yet.

- `chmod +x scripts/watch-mymusic-deploy.sh`
  - Result: PASS.

- `bash -n scripts/watch-mymusic-deploy.sh`
  - Result: PASS.

- `scripts/watch-mymusic-deploy.sh --check`
  - Result: PASS.
  - Observed supported audio files: `1`.
  - Observed selected audio file: `0250孙燕姿-遇见.mp3`.
  - Observed behavior: normalized `public/mymusic` permissions, created a clean temporary Git worktree from `HEAD`, overlaid `public/mymusic`, skipped deployment and public verification in no-deploy mode.

- `git worktree list`
  - Result: PASS.
  - Observed no lingering `mymusic-deploy` temporary worktree after the cleanup fix.

- `stat -f '%OLp %N' public/mymusic/0250孙燕姿-遇见.mp3`
  - Result: PASS.
  - Observed mode: `644`.

- `scripts/watch-mymusic-deploy.sh --verify-build`
  - Initial result: FAIL.
  - Initial failure: temporary clean worktree could run `npx tsc`, but lacked ignored Next type declarations, causing PNG imports in `src/components/liquid-grass/index.tsx` to fail.
  - Fix: script now links active `node_modules`, generates a temporary minimal `next-env.d.ts`, and copies production env files into the temporary worktree.
  - Follow-up failure: live build exposed a Next/Turbopack panic because symlinked `node_modules` pointed outside the temporary worktree filesystem root.
  - Final fix: script now runs `npm ci --prefer-offline --no-audit --no-fund` inside the temporary worktree instead of symlinking `node_modules`.
  - Final result: PASS.
  - Coverage: dependency install and `npx tsc --noEmit` succeed from the temporary clean worktree without live deployment.

## Not Run

- Live deployment was not run.
- Public static audio and public API verification were not run, because those checks are intentionally tied to a real deployment cycle.

## Notes

- The first `--check` run exposed a stale prunable worktree record because the cleanup check expected `.git` to be a directory. In Git worktrees `.git` is a file, so the script now removes the temporary worktree when the worktree path exists.
- A later deploy attempt exposed that the temporary clean worktree did not have local npm dependencies or ignored Next/env files. Symlinking `node_modules` fixed `tsc` but failed Next/Turbopack, so the script now installs a real dependency tree inside the temporary worktree and prepares ignored Next/env files without copying unrelated source changes.
