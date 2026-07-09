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

Status: `completed with deployment blocked`.

The working tree is very large and dirty. Initial inspection found:

- current branch: `notes-workspace-ux-upgrade`
- remote: `mine`
- no `deploy` / `build:cf` script in current `package.json`
- `wrangler.toml` is currently deleted
- `open-next.config.ts` is currently deleted

Git commit and push completed. Public deployment is blocked because deployment config is absent from the pushed commit; the intended deployment path must be confirmed or restored in a separately approved scope.

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
