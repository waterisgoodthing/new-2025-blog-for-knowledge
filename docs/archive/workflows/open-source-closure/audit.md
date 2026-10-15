# Open-Source Structure Audit

Date: 2026-06-16

## Scope

This audit reviews the repository as an open-source project structure. It does not assess product correctness or production deployment health.

Touched domain: shared infrastructure.

Evidence checked:

- `git status --short`
- `git ls-files`
- tracked repository file inventory
- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `LICENSE`
- `package.json`
- `.gitignore`
- `backend/.env.example`
- `backend/app/config.py`
- backend migrations and tests

## Existing Open-Source Baseline

Present:

- Chinese-first `README.md`
- MIT `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `.gitignore`
- frontend package manifest and lockfile
- backend dependency file
- backend Alembic migrations
- several backend tests
- architecture/workflow documentation under `docs/`

Not tracked, but present locally and correctly ignored:

- `backend/.env`
- `backend/.venv/`
- Python `__pycache__/` and `*.pyc`

## Required Gaps

These are the main missing items before the repository feels structurally ready for external contributors.

1. No CI workflow.
   - `.github/` is absent.
   - There is no tracked GitHub Actions workflow for TypeScript checking, frontend build, backend import checks, backend tests, or migration checks.
   - This means contributors cannot see an automated baseline for PR health.

2. No issue or pull request templates.
   - `.github/ISSUE_TEMPLATE/` and `.github/pull_request_template.md` are absent.
   - `CONTRIBUTING.md` describes what to include, but GitHub does not guide reporters or PR authors at submission time.

3. Frontend/public environment template is missing.
   - `backend/.env.example` exists.
   - There is no root `.env.example` documenting frontend variables such as `NEXT_PUBLIC_API_URL` or deployment-facing public URLs.
   - New contributors can install dependencies but still have to infer runtime API configuration.

4. `backend/.env.example` does not cover all settings in `backend/app/config.py`.
   - Missing examples include `ENV`, `ALLOWED_ORIGINS`, `ENABLE_REGISTRATION`, `REGISTRATION_KEY`, `KEEP_ALIVE_*`, `AUTH_BYPASS`, `AUTH_BYPASS_ALLOW`, `WEBAUTHN_*`, and `IMAGE_BASE_URL`.
   - This makes local setup and production hardening less reproducible.

5. Database bootstrap is under-documented.
   - README explains dependency install and backend start.
   - It does not include `alembic upgrade head`, PostgreSQL setup options, or first admin/operator account bootstrap.
   - Without this, a clean clone can start the backend only after the user reverse-engineers database initialization.

6. `package.json` still marks the package as private and has sparse open-source metadata.
   - Current manifest has `"private": true`.
   - It lacks `license`, `repository`, `bugs`, `homepage`, and author/maintainer metadata.
   - This is not a runtime bug, but it is incomplete as a public repository identity.

## Recommended Gaps

These are not blockers, but they would make the project much easier to evaluate and contribute to.

1. No documented test command matrix.
   - Backend tests exist under `backend/tests/`.
   - Frontend checks rely on ad-hoc commands in docs and package scripts.
   - Root JavaScript test files exist, but they are not wired into a standard `npm test` or documented validation command.

2. No containerized local development path.
   - There is no `docker-compose.yml` for PostgreSQL plus backend/frontend.
   - Since the backend requires PostgreSQL, a minimal database compose file would reduce setup friction.

3. No explicit architecture map in README for contributor navigation.
   - README states `src/` and `backend/`.
   - It does not link to `SYSTEM_MAP.md`, backend routers/services/models, frontend API clients, or workflow rules.

4. Attribution is honest but still incomplete.
   - README states the project is adapted from an original open-source project and does not invent an upstream URL.
   - There is still no `NOTICE`, `AUTHORS`, or `CREDITS` file, and the upstream project URL remains unknown.

5. Repository has legacy top-level planning/audit documents that may confuse new contributors.
   - Examples include top-level `design.md`, `SYSTEM_AUDIT_REPORT.md`, and older `docs/*-tasks.md` files.
   - They may be useful history, but a public contributor needs a clear index of which docs are current.

6. No CODEOWNERS or support policy.
   - Optional for a small personal project.
   - Useful if external PRs/issues are expected.

## Current Verdict

The repository already has the core open-source baseline: README, license, contributing guide, security policy, dependency files, migrations, and some tests.

The main missing content is operational scaffolding for external contributors:

- CI
- GitHub issue/PR templates
- complete environment examples
- database bootstrap instructions
- package metadata
- clearer test and contributor validation commands

No product-code change is required to close this audit. The next best task is a shared-infrastructure documentation and CI pass.
