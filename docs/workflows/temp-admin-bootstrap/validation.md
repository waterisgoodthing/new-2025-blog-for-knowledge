# Temporary Admin Bootstrap Validation

Validation date: 2026-06-23

## Code Validation

Command:

```bash
cd backend && .venv/bin/python -m pytest tests/test_temp_admin_bootstrap.py
```

Result: passed.

Evidence:

```text
collected 3 items
tests/test_temp_admin_bootstrap.py ... [100%]
3 passed in 0.83s
```

Command:

```bash
cd backend && .venv/bin/python -m app.cli --help
```

Result: passed.

Evidence: CLI help lists both `create-temp-admin` and `disable-temp-admin`.

Command:

```bash
cd backend && .venv/bin/python -m py_compile app/cli.py tests/test_temp_admin_bootstrap.py
```

Result: passed.

## Account Creation

Command:

```bash
cd backend && .venv/bin/python -m app.cli create-temp-admin
```

Result: passed.

Evidence:

```text
Temporary admin account created.
Username: temp-admin
This password is shown once. Rotate or disable this account after recovery.
```

The generated password was intentionally not recorded in this file.

## Production Boundary Check

The temporary admin account above was created against the local backend database configured by `backend/.env`.

Masked database target:

```text
scheme=postgresql+asyncpg
host=localhost
port=5432
database=blog_db
```

This means the generated account is a local development account, not a confirmed production account for `https://public-api.limengyang.me`.

## Public Runtime Check

Commands:

```bash
curl -D - https://public-api.limengyang.me/api/health
curl -D - https://public-api.limengyang.me/api/auth/passkey/status
curl -D - https://blog.limengyang.me/api/auth/passkey/status
```

Results:

- `https://public-api.limengyang.me/api/health` returned `200` with `{"status":"ok","db":"ok"}`.
- `https://public-api.limengyang.me/api/auth/passkey/status` returned `200` with `{"registered":true}`.
- `https://blog.limengyang.me/api/auth/passkey/status` returned `404` from the Next frontend.

Production frontend chunk inspection for `/manage` found relative auth API paths such as:

```text
/api/auth/login
/api/auth/login-passkey
/api/auth/me
/api/auth/passkey/status
```

It did not find `public-api.limengyang.me` in the inspected manage chunks. This confirms the production manage page is currently wired to `blog.limengyang.me/api/...`, while the working backend API is on `public-api.limengyang.me/api/...`.

## Public SSR / Metadata Check

Public HTML fetches for `/blog`, `/discover`, and `/manage` still expose `加载中...` as primary page text. The fetched metadata remains:

```text
title=My Blog
description=A personal blog
```

This supports the public-side audit finding that route content is weak for crawlers and social/search previews.

## Cleanup Command

After recovery, disable the temporary account with:

```bash
cd backend && .venv/bin/python -m app.cli disable-temp-admin
```

This command requires typing `yes` before it disables the account.
