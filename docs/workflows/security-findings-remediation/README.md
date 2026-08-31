# Security Findings Remediation (2026-08-29)

## Goal

Remediate the security findings produced by the 2026-08-29 full-repository scan, in repository code and tests only.

## Approval Basis

User instruction (2026-08-29): 「自主迭代完成这些安全隐患」 — autonomous iteration to completion for the security findings. This authorizes repository-local code/test changes and their validation.

## Explicitly NOT Authorized (requires separate approval)

- `git commit` / `git push` — working tree stays uncommitted.
- Executing migration 026 against any database (including local dev DBs beyond what tests need).
- Deployment, production configuration, or production writes.

## Gates Triggered

- **G2 (DATA_DATABASE)**: migration 026 downgrade guard; `EXPECTED_ALEMBIC_REVISION` bump. No migration is executed; production execution stays with G5.
- **G3 (SECURITY_AUTH)**: fail-closed startup guards, constant-time key comparison, endpoint removal, error-text sanitization. Auth contract (stateful `admin_session` cookie + `get_current_admin`) is unchanged.

## Scope (findings from the scan, security subset)

| ID | Finding | Severity |
|----|---------|----------|
| S1 | `EXPECTED_ALEMBIC_REVISION = "025"` vs migration `026` — startup hard-block after upgrade | P0 |
| S2 | Migration 026 has no `downgrade()`; irreversible by omission | P0 |
| S3 | Default JWT secret / AUTH_BYPASS only guarded when `ENV == "production"` | P1 |
| S4 | Registration/operator key comparison not constant-time | P1 |
| S5 | Orphaned unauthenticated `GET /api/auth/passkey/reg-options` | P1 |
| S6 | 15 error-text leak sites (`detail=str(e)` / response message) | P1 |

## Files

- `requirements.md` — requirements and acceptance criteria per finding.
- `design.md` — approach per finding, including preserved contracts and residual risks.
- `tasks.md` — serial task list with live status.
- `validation.md` — executed validation evidence.
