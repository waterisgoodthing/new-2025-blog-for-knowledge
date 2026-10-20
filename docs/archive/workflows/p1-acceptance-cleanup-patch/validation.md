# Validation — P1 Acceptance Cleanup Patch

Status: `completed`

Validation date: 2026-07-09.

## Command Results

| Check | Command | Result |
| --- | --- | --- |
| TypeScript | `npx tsc --noEmit` | Passed. |
| Frontend build | `npm run build` | Passed. Next.js generated 37 app routes. Existing warnings: stale `baseline-browser-mapping` data and Node `DEP0205 module.register()` deprecation. |
| Diff whitespace | `git diff --check` | Passed. |
| Setup check | `npm run check` | Passed with warnings. The script now warns that Python 3.14.5 is unsupported and selects Python 3.12.13 via `python3.12`. Existing environment warnings: Docker not found, root `.env` missing, ports 2025 and 8000 in use. |

## Browser Validation

Temporary frontend:

```text
http://127.0.0.1:3027
```

Environment:

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_IMAGE_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SITE_URL=http://127.0.0.1:3027
SITE_URL=http://127.0.0.1:3027
```

Anonymous browser context was used. No `AUTH_BYPASS` was used.

Routes checked:

| Route | Result |
| --- | --- |
| `/` | No visible `管理` text and no public `/manage` link found. |
| `/blog` | No visible `管理` text and no public `/manage` link found. |
| `/notes` | No visible `管理` text and no public `/manage` link found. No `新建笔记`, `工作区`, or `采集错题` admin action found for anonymous context. |
| `/manage` | Login page still loads as the explicit management login entry. It does not expose management data. |

## Setup Check Evidence

`npm run check` now reports:

```text
Python 3.14.5 (via python3) is not supported by the current backend dependency set. Use Python 3.12 or 3.13.
Python 3.12.13 (via python3.12)
venv module: available
```

This directly addresses the fresh setup failure mode where default `python3` selected Python 3.14.

## Validation Notes

- Backend permissions were not changed.
- No migration was added.
- No database table was added.
- AI Gateway, Prompt Registry, `ai_runs`, and `ai_call_logs` main logic were not modified.
- P2 backlog items remain deferred and are not treated as current blockers.
