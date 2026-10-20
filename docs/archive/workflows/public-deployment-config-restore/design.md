# Design — Public Deployment Config Restore

## Restore Strategy

Use the previously working deployment configuration from commit `1cb7c7a` as the baseline.

Restore:

- `open-next.config.ts`
- `wrangler.toml`
- `package.json` deployment scripts
- `@opennextjs/cloudflare`
- `wrangler`
- corresponding `package-lock.json` dependency graph via `npm install`

Do not use `git checkout --` against the working tree. Apply changes explicitly and keep them reviewable.

## Deployment Strategy

After restoring and validating:

1. commit and push the deployment restore
2. deploy from the current branch
3. verify public pages and API health

If the deploy command requires generated files, use the existing command path to generate them. Do not copy ignored local build artifacts into Git.

## Risk Controls

- Keep changes scoped to deployment config and workflow evidence.
- Do not touch backend models, migrations, AI services, or app feature logic.
- Do not use `AUTH_BYPASS`.
- If deployment fails for Cloudflare auth/account reasons, record the blocker and stop.
