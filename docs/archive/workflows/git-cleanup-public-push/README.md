# Git Cleanup And Public Push

## Task Goal

Clean up the current Git state, commit and push the approved update set, and deploy the frontend to the public site if the repository still contains a valid public deployment path.

This is an operational release workflow. It must preserve unrelated user changes, avoid destructive Git commands, and clearly separate GitHub push from public Cloudflare deployment.

## Touched Domains

- `shared infrastructure`: Git, package scripts, deployment configuration, setup docs.
- `docs/workflows`: release evidence and validation.
- `src`, `backend`, `docs`: staging candidates only; no new feature implementation in this workflow.
- `deploy`: public frontend deployment to `blog.limengyang.me` if deploy config is available.

## Current Status

Status: `2026-07-29 release run completed: Git push, Cloudflare deployment, and public verification passed`.

The 2026-07-09 run completed its Git push but correctly stopped before deployment
because the deployment path was absent at that time.

The new preflight snapshot found:

- current branch: `notes-workspace-ux-upgrade`
- upstream: `mine/notes-workspace-ux-upgrade`
- branch position before fetch: 3 commits ahead, 0 behind
- tracked dirty files: 8 modified documentation files
- untracked files: 334, all under `docs/`
- public deployment files and scripts now exist:
  `wrangler.toml`, `open-next.config.ts`, `scripts/predeploy-audit.mjs`,
  `build:cf`, `predeploy:check`, `deploy`, and `deploy:full`
- the untracked set contains authenticated UI screenshots and data/migration
  evidence that require a public-safety review before staging
- one review report is under a suspicious duplicated path:
  `docs/workflows/i-series-completion-plan/docs/workflows/i-series-completion-plan/`

The user approved GCP-R2-01 through GCP-R2-06. Inventory, public-safety
classification, non-destructive cleanup, whitespace checks, and documentation
checks completed. The isolated `predeploy:check` then stopped the release because
the live production audit reported 10 high vulnerabilities. No files were
staged, committed, pushed, deleted, or deployed in the 2026-07-29 run.

## Workflow Files

- [Requirements](requirements.md)
- [Design](design.md)
- [Tasks](tasks.md)
- [Validation](validation.md)
- [Diff Report](diff-report.md)
- [Handoff Prompt](handoff-prompt.md)

## Planned Output

- Clean release checklist.
- Validation results before staging.
- Explicit staged file list.
- Git commit and push result if approved.
- Public deployment result, or a blocker report if deployment config is missing.
