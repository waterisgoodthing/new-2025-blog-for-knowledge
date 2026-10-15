# PSS-06 final isolated-browser pass

Date: 2026-08-16

Command:

```sh
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test --config=docs/workflows/public-session-state-optimization/playwright.config.ts
```

Result: `3 passed (7.8s)`.

The matrix starts only a local Next development server on `127.0.0.1:3000` and an in-memory-session FastAPI harness on `127.0.0.1:8001`. It uses the already-installed Chromium browser and two synthetic Cookie values (`pss-browser-admin`, `pss-browser-expired`); it does not contact a real database, account, production API, credential, or enable `AUTH_BYPASS`.

Coverage and observations:

- Anonymous `/blog`, `/notes`, and `/mistakes` remain visible. Each full page navigation makes exactly one optional `/api/auth/session-state` request, with zero strict `/api/auth/me` requests, zero `/api/folders`, `/api/review`, `/api/admin`, `/api/ai`, or `/api/attachments` requests, and zero page errors.
- A valid synthetic `admin_session` shows the public edit control. After `POST /api/auth/logout` and reload, that control is gone.
- An expired synthetic Cookie resolves public `/blog` as anonymous; strict `/api/auth/me` remains `401`; `/manage` renders only the password-login state. API responses observed during the strict-page check contain no `5xx` responses.

Harness details: a synthetic public settings response supplies only non-personal layout dimensions, and the unrelated public Passkey-status probe is fulfilled as `{ "registered": false }`. The harness models the existing session resolver's revoked-session filter so logout evidence reflects the production query contract.

Warnings: the final run reported no assertion, browser-console, page-error, dialog, download, navigation, or server-error warning. Playwright shut down both servers; subsequent `lsof` checks found no listeners on 3000 or 8001.
