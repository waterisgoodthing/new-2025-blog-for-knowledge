# Temporary Admin Bootstrap Requirements

## Functional Requirements

1. Provide a code-level backend CLI command to create or rotate a temporary admin account.
2. Default username must be stable and obvious, such as `temp-admin`.
3. The command must generate a strong random password by default.
4. The command must print the generated password exactly once and must not save plaintext credentials.
5. If the target username already exists, the command must update its password and ensure `is_admin=True`.
6. If the target username does not exist, the command must create it with `is_admin=True`.
7. The command must use the existing password hashing helper.
8. The command must use the existing database settings and async SQLAlchemy setup pattern from `backend/app/cli.py`.
9. The command must not enable or depend on `AUTH_BYPASS`.
10. The command must not enable public registration or weaken passkey-only sensitive actions.

## Non-Functional Requirements

1. Keep the change backend-scoped unless frontend validation exposes a contract mismatch.
2. Preserve current user changes and avoid unrelated refactors.
3. Keep implementation small and aligned with existing CLI style.
4. Add focused tests or an import/CLI validation path appropriate for this repository.
5. Record validation results in `validation.md`.

## Security Requirements

1. Do not commit generated passwords, tokens, `.env`, private keys, database dumps, or personal data.
2. Avoid any new network-exposed route for bootstrap.
3. Output must clearly warn that the account is temporary and should be removed or rotated after use.
4. If a user-supplied password option is added, it must remain optional and must not echo the password back unnecessarily.

## Acceptance Criteria

1. A maintainer can run a documented command to create or rotate a temporary admin account.
2. The resulting user has `is_admin=True` and can be used by the existing `/api/auth/login` flow.
3. Existing auth bypass and passkey behavior are not loosened.
4. Validation evidence documents syntax/import checks and any runtime limitations.
