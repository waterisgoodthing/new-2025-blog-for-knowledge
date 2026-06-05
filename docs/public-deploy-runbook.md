# Public Deploy Runbook

Last updated: 2026-06-05

## Latest Deployment

The latest confirmed public deployment was completed on 2026-06-05.

- Worker: `2025-blog-public`
- URL: `https://2025-blog-public.17527677392.workers.dev`
- Version ID: `9d46eb7b-71be-4bd1-9155-12c074806b96`
- Assets uploaded: 34 new or modified files, 510 already uploaded
- Worker startup time: 21 ms

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

## Cloudflare Authentication Methods

Use Method A first. Use Method B only when a browser OAuth login is easier than creating a token.

### Method A: API Token, Recommended

Create a Cloudflare API token that is not restricted away from the current network location.

Minimum practical permissions for this project:

- `Account: Account Settings: Read`
- `User: User Details: Read`
- `Account: Workers Scripts: Edit`
- `Account: Workers Routes: Edit`

Then run:

```bash
cd /Users/limengyang/2025-blog-public
export CLOUDFLARE_API_TOKEN='paste-token-here'
npx wrangler whoami
npm run deploy
```

If `whoami` fails with `code: 9109`, the token is still blocked by IP/location. Remove the IP restriction or add the current egress IP.

### Method B: Browser OAuth Login

Use this only in the user's own Terminal, not from a separate agent process, because Chrome must be able to reach Wrangler's temporary local callback server.

```bash
cd /Users/limengyang/2025-blog-public
unset CLOUDFLARE_API_TOKEN
npx wrangler login --browser=false --callback-host localhost --callback-port 8976
```

Keep that terminal open. Copy the `Visit this link to authenticate:` URL into Chrome and grant consent.

If Chrome reports that `localhost:8976` refused the connection, the callback server is not listening. Check in another terminal:

```bash
lsof -iTCP:8976 -sTCP:LISTEN
```

If there is no output, restart login with another port:

```bash
unset CLOUDFLARE_API_TOKEN
npx wrangler login --browser=false --callback-host localhost --callback-port 9876
```

After login:

```bash
unset CLOUDFLARE_API_TOKEN
npx wrangler whoami
npm run deploy
```

### Method C: Agent-Assisted Deploy After User Auth

If the user authenticates in their own Terminal, the agent can continue only after this command passes locally:

```bash
unset CLOUDFLARE_API_TOKEN
npx wrangler whoami
```

Once `whoami` shows the Cloudflare account, the agent can run:

```bash
env -u CLOUDFLARE_API_TOKEN npm run deploy
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
