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

## 2026-07-29 Release Run

This run reuses the workflow but does not reuse the previous completion status.
The current dirty surface is documentation-only and spans multiple workflow
owners, so the release is split into two gates:

1. **Git publication gate**
   - fetch the configured upstream and confirm divergence
   - inventory every modified and untracked path
   - review authenticated screenshots, JSON observations, migration manifests,
     owner identifiers, database counts, local paths, and recovery evidence for
     public-repository safety
   - resolve the duplicated nested review-report path without destructive cleanup
   - stage only the reviewed set and verify the exact cached list
   - commit and push without force
2. **Public deployment gate**
   - use the pushed commit, not the dirty checkout
   - create a detached isolated worktree
   - run the repository's fail-closed `predeploy:check`
   - run the existing `deploy:full` path only after the gate passes
   - verify public routes and the API health boundary

The default safety decision for material that has not passed public review is to
leave it unstaged and report that the Git tree is not yet fully clean. The
workflow must not delete, redact, relocate, or publish ambiguous evidence merely
to make `git status` empty.

Because this run currently changes documentation only, frontend deployment may
produce no user-visible application change. It is still permitted after approval
as an operational consistency check, but its source must be the pushed commit.
