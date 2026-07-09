# Validation — Public Deployment Config Restore

Status: `in progress`

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
