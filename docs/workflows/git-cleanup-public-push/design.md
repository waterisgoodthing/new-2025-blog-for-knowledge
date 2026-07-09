# Design — Git Cleanup And Public Push

## Release Shape

This release should be evidence-first:

1. inspect current working tree
2. run validation
3. stage intentionally
4. commit
5. push
6. deploy from the pushed commit in an isolated worktree if possible
7. verify public routes

## Git Cleanup Strategy

The current tree contains many modified, deleted, and untracked files from multiple accepted batches. The user asked for all updates, so this workflow can stage broadly after validation, but it must still avoid generated caches and secrets.

Before staging:

- inspect ignored/untracked risk
- ensure no real `.env`, private keys, database dumps, or build caches are staged
- confirm `git diff --check` is clean

Staging plan after approval:

```bash
git add -A
git status --short
git diff --cached --stat
```

If secrets or generated caches appear staged, unstage only those files and record the exclusion.

## Deployment Strategy

Prior successful deployments in this repo used a clean detached worktree and Cloudflare/OpenNext commands. That protects the public site from uncommitted or local-only state.

However, current inspection found that `package.json` no longer has `deploy` / `build:cf`, and `wrangler.toml` plus `open-next.config.ts` are currently deleted. Therefore deployment has a likely blocker.

Approved deployment behavior:

- If the current update set intentionally removes Cloudflare deployment config, do not deploy and record the blocker.
- If validation shows deployment config exists after staging/commit, deploy from a clean worktree from the pushed commit.
- Do not reconstruct Cloudflare/OpenNext config inside this workflow without separate user approval.

## Public Verification

If deployment succeeds, verify:

- public pages return HTTP 200
- `/manage` loads as login/admin boundary, not public data
- public API health returns ok
- no obvious deployment route mismatch

## Risk Controls

- No `git reset --hard`.
- No `git checkout --`.
- No force push unless explicitly approved later.
- No `AUTH_BYPASS`.
- No backend schema or migration changes in this workflow.
