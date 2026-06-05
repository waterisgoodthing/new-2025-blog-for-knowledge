# Public Deploy Runbook

Last updated: 2026-06-05

## Scope

This repository deploys the frontend to Cloudflare with OpenNext.

Relevant files:

- `package.json`
- `wrangler.toml`
- `open-next.config.ts`

The backend is a separate FastAPI service and is not deployed by `npm run deploy`.

## Preconditions

Before a public deploy:

1. Run `git status --short` and identify unrelated dirty files.
2. Confirm the current deploy should include the whole working tree, not only one task folder.
3. Do not commit `.env`, private keys, tokens, database dumps, or local caches.
4. Run validation:
   - `npx tsc --noEmit`
   - `npm run build`
5. If the frontend uses backend APIs, confirm the production API environment is configured for the Cloudflare deployment.
6. Confirm Cloudflare authentication before deploying:
   - If using `CLOUDFLARE_API_TOKEN`, make sure the token allows the current network location.
   - If not using an API token, run `wrangler login` in an interactive terminal.

## Deploy Command

Use the repository script:

```bash
npm run deploy
```

If deployment fails with Cloudflare `code: 9109`, the configured API token is restricted by location/IP. Remove the restriction, use an allowed network, or authenticate with `wrangler login`.

This runs:

```bash
opennextjs-cloudflare deploy
```

The Cloudflare worker name is configured in `wrangler.toml`:

```toml
name = "2025-blog-public"
main = ".open-next/worker.js"
```

## Git Hygiene

For task-based work:

1. Keep task docs under `docs/workflows/<task-name>/`.
2. Commit task-scoped files when possible.
3. If the build depends on previous uncommitted changes, either commit the dependent changes together with a clear message or explicitly document that the deploy used the full dirty working tree.
4. After each task item is completed, update the task's `tasks.md`.
5. After deployment, record validation and deployment output in the task report or validation document.

## Recommended Command Sequence

```bash
git status --short
npx tsc --noEmit
npm run build
npm run deploy
```

Optional GitHub push after a clean commit:

```bash
git add <task-scoped-files>
git commit -m "<message>"
git push <remote> <branch>
```

## Rollback

If the public deploy is bad:

1. Identify the last known good Git commit or Cloudflare deployment.
2. Revert or checkout the good source state.
3. Run `npx tsc --noEmit` and `npm run build`.
4. Run `npm run deploy` again.
