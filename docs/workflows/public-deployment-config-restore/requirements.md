# Requirements — Public Deployment Config Restore

## Scope

Restore public deployment capability only.

## Functional Requirements

- Restore the previous Cloudflare/OpenNext deployment scripts and config.
- Keep current application code and accepted release content unchanged.
- Do not revert current feature or documentation commits.
- Reinstall/update lockfile only as needed for the restored deployment dependencies.
- Validate locally before deploy.
- Deploy only through the restored existing deployment path.
- Record public verification results.

## Non-Requirements

- No new business feature.
- No new migration.
- No new database table.
- No AI Gateway / Prompt Registry / `ai_runs` / `ai_call_logs` main-logic change.
- No backend permission model change.
- No replacement deployment architecture.
- No `AUTH_BYPASS`.

## Validation Requirements

Local validation:

```bash
npx tsc --noEmit
npm run build
npm run build:cf
git diff --check
```

Deploy preflight:

```bash
npx wrangler whoami
```

Deploy:

```bash
npm run deploy:full
```

Public verification:

- `https://blog.limengyang.me/`
- `https://blog.limengyang.me/blog`
- `https://blog.limengyang.me/notes`
- `https://blog.limengyang.me/manage`
- `https://public-api.limengyang.me/api/health`

## Stop Conditions

- Restored dependency install fails.
- `build:cf` fails.
- Cloudflare auth is unavailable.
- Wrangler deploy fails with account/auth/IP restrictions.
- Public verification fails.
