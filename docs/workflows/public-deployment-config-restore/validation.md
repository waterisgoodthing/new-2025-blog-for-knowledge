# Validation — Public Deployment Config Restore

Status: `completed`

Validation date: 2026-07-09.

## Restore

Restored:

- `open-next.config.ts`
- `wrangler.toml`
- `package.json` scripts: `build:cf`, `preview`, `deploy`, `deploy:full`, `cf-typegen`
- dependencies: `@opennextjs/cloudflare`, `wrangler`

Lockfile update:

```text
npm install
```

Result:

- Added 300 packages.
- npm audit reports `5 vulnerabilities (3 moderate, 2 high)`.

## Local Validation

| Check | Command | Result |
| --- | --- | --- |
| TypeScript | `npx tsc --noEmit` | Passed. |
| Next build | `npm run build` | Passed. Next.js generated 37 app routes. Existing warnings: stale `baseline-browser-mapping` and Node `DEP0205 module.register()` deprecation. |
| Cloudflare/OpenNext build | `npm run build:cf` | Passed. OpenNext generated `.open-next/worker.js`. |
| Diff whitespace | `git diff --check` | Passed. |

OpenNext notes:

- `@opennextjs/cloudflare` resolved to `1.20.1`.
- OpenNext warned that `workerd compatibility_date: 2025-03-25` could be updated later. This is not blocking deployment restore.

## Git Commit And Push

Restore commit:

```text
8619fdf fix: restore Cloudflare deployment config
```

Push result:

```text
84e9df3..8619fdf  notes-workspace-ux-upgrade -> notes-workspace-ux-upgrade
```

Note:

- Initial push failed because Git HTTPS credentials were not available to raw Git.
- `gh auth status` confirmed an active GitHub login with `repo` and `workflow` scopes.
- `gh auth setup-git` configured Git credentials, then push succeeded.

## Deploy

Cloudflare auth:

```text
npx wrangler whoami
```

Result:

- Logged in with a User API Token from `CLOUDFLARE_API_TOKEN`.
- Account ID: `47df03d68ab34399f66ba563672e3382`.

Deploy command:

```text
npm run deploy:full
```

Result:

- `npx tsc --noEmit`: passed as part of `deploy:full`.
- `opennextjs-cloudflare build`: passed.
- `wrangler deploy --route 'blog.limengyang.me/*'`: passed.
- Uploaded 40 new or modified static assets.
- Worker: `2025-blog-public`.
- Route: `blog.limengyang.me/*`.
- Worker URL: `https://2025-blog-public.17527677392.workers.dev`.
- Current Version ID: `29fb09bf-1a78-4d4d-934c-9a82753fcce3`.

Deploy note:

- Wrangler output listed `/.DS_Store` among uploaded static assets. This does not block the deployment but should be cleaned up in a small follow-up static-assets hygiene task.

## Public Verification

| Target | Result |
| --- | --- |
| `https://blog.limengyang.me/` | `HTTP/2 200`, `x-opennext: 1`. |
| `https://blog.limengyang.me/blog` | `HTTP/2 200`, `x-opennext: 1`. |
| `https://blog.limengyang.me/notes` | `HTTP/2 200`, `x-opennext: 1`. |
| `https://blog.limengyang.me/manage` | `HTTP/2 200`, `x-opennext: 1`. |
| `https://public-api.limengyang.me/api/health` | `HTTP/2 200`, body `{"status":"ok","db":"ok"}`. |
| `https://blog.limengyang.me/BUILD_ID` | `R4bPqm8bDVqN3D9B20Iam`. |
