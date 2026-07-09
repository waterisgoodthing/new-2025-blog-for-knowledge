# Requirements — Git Cleanup And Public Push

## Scope

The user requested:

```text
开始清理 git 并将所有更新内容推送到公网
```

This workflow interprets that as:

1. cleanly review and stage the current update set
2. commit and push to the configured GitHub remote
3. deploy the frontend publicly only if a valid deploy path exists
4. record validation and public verification

## Functional Requirements

- Preserve all existing user/generated changes; do not discard or revert unrelated files.
- Avoid destructive Git operations such as `git reset --hard` or `git checkout --`.
- Before staging, run release validation appropriate to the changed surface.
- Confirm whether deployment configuration exists in the current update set.
- If deployment configuration is missing, record the blocker and do not invent a new deployment architecture.
- If committing, stage the approved current update set intentionally and report the staged scope.
- Push to the current configured remote/branch unless a blocker is found.
- For public deployment, prefer an isolated clean worktree from the pushed commit so deployment does not accidentally include uncommitted local state.
- Do not use `AUTH_BYPASS` as validation.

## Non-Requirements

- No new business feature.
- No new migration.
- No new database table.
- No AI Gateway / Prompt Registry / `ai_runs` / `ai_call_logs` refactor.
- No backend permission model change.
- No Cloudflare deployment config recreation unless the user approves that as a repair task.
- No P2 backlog cleanup.

## Validation Requirements

Minimum local validation before commit/push:

```bash
cd backend && .venv/bin/python -m pytest tests/ -ra
cd backend && PYTHONPATH=. .venv/bin/alembic current
npx tsc --noEmit
npm run build
git diff --check
npm run check
```

Deployment preflight:

```bash
git status --short
git diff --cached --stat
npx wrangler whoami
```

Deployment only if config exists:

- current package script for Cloudflare/OpenNext deployment, or
- documented existing command path using existing config files.

Post-deploy verification if deployment runs:

- `https://blog.limengyang.me/`
- `https://blog.limengyang.me/blog`
- `https://blog.limengyang.me/notes`
- `https://blog.limengyang.me/manage`
- `https://public-api.limengyang.me/api/health`

## Stop Conditions

- Validation failure.
- Missing deploy config.
- Git push rejected and requires merge/rebase decision.
- Cloudflare authentication unavailable.
- Any step requires destructive cleanup.
