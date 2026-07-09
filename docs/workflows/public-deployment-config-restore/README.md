# Public Deployment Config Restore

## Task Goal

Restore the previously working Cloudflare/OpenNext public deployment path so the current frontend can be deployed to `blog.limengyang.me`.

This workflow exists because the Git cleanup release pushed commit `2b5453f`, then follow-up docs commits, but public deployment was blocked: the current tree removed `wrangler.toml`, `open-next.config.ts`, and the `build:cf` / `deploy` package scripts.

## Touched Domains

- `shared infrastructure`: deployment scripts and dependencies.
- `deploy`: Cloudflare/OpenNext configuration.
- `docs/workflows`: validation and release evidence.

## Current Status

Status: `tasks.md pending user approval`.

No code restore has been performed yet.

## Known Restore Source

The previous working deployment path exists in commit `1cb7c7a`:

- `package.json` scripts: `build:cf`, `preview`, `deploy`, `deploy:full`, `cf-typegen`
- dependency: `@opennextjs/cloudflare`
- dev dependency: `wrangler`
- `wrangler.toml`
- `open-next.config.ts`

## Workflow Files

- [Requirements](requirements.md)
- [Design](design.md)
- [Tasks](tasks.md)
- [Validation](validation.md)
- [Diff Report](diff-report.md)
- [Handoff Prompt](handoff-prompt.md)

## Planned Output

- Restored deployment config.
- Local validation.
- Cloudflare deploy attempt from the restored current tree.
- Public verification or blocker report.
