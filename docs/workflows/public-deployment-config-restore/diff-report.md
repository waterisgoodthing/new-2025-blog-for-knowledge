# Diff Report — Public Deployment Config Restore

Status: `completed`

## Files Changed

Deployment restore:

- `open-next.config.ts`
- `wrangler.toml`
- `package.json`
- `package-lock.json`

Workflow evidence:

- `docs/workflows/public-deployment-config-restore/README.md`
- `docs/workflows/public-deployment-config-restore/requirements.md`
- `docs/workflows/public-deployment-config-restore/design.md`
- `docs/workflows/public-deployment-config-restore/tasks.md`
- `docs/workflows/public-deployment-config-restore/validation.md`
- `docs/workflows/public-deployment-config-restore/diff-report.md`
- `docs/workflows/public-deployment-config-restore/handoff-prompt.md`

## Restored Deployment Surface

- Restored `@opennextjs/cloudflare`.
- Restored `wrangler`.
- Restored scripts:
  - `build:cf`
  - `preview`
  - `deploy`
  - `deploy:full`
  - `cf-typegen`
- Restored `wrangler.toml` route-compatible Worker config.
- Restored minimal `open-next.config.ts`.

## Explicit Non-Changes

- No business feature was added.
- No migration was added.
- No database table was added.
- No AI Gateway / Prompt Registry / `ai_runs` / `ai_call_logs` main logic was changed.
- No backend permission model was changed.
- No `AUTH_BYPASS` validation path was used.

## Deploy Result

- Restore commit pushed: `8619fdf fix: restore Cloudflare deployment config`.
- Public deployment succeeded.
- Cloudflare Worker Version ID: `29fb09bf-1a78-4d4d-934c-9a82753fcce3`.
- Public BUILD_ID: `R4bPqm8bDVqN3D9B20Iam`.

## Follow-Up

- Remove `.DS_Store` from public/static asset upload path and add ignore coverage if needed.
- Consider updating `compatibility_date` in a separate deployment hygiene task.
