# Temporary Admin Bootstrap Design

## Context

The current backend auth model uses `users.is_admin = true` for admin authorization. Password login through `/api/auth/login` creates an `admin_session` only after a username/password pair matches a row in `users`.

The existing `backend/app/cli.py set-password` command updates the admin password store and an existing admin user, but it does not create an admin user when none exists. That makes clean or recovered environments awkward: a user can set a password but still have no login-capable admin account.

## Proposed Approach

Add an explicit backend CLI command for temporary admin bootstrap.

The command should:

- create a temporary admin user if it does not exist,
- rotate that user's password if it already exists,
- set `is_admin=True`,
- generate a strong random password by default,
- print the password once to stdout,
- avoid writing plaintext credentials to any repository file,
- be clearly marked as local/operator bootstrap tooling,
- support an optional username with a conservative default such as `temp-admin`,
- avoid enabling broad registration or auth bypass.

## Safety Shape

This should be a controlled operational tool, not a web endpoint. Keeping it in the CLI avoids exposing a remote account-creation surface.

The implementation should not:

- hard-code a password,
- commit real credentials,
- silently enable `AUTH_BYPASS`,
- make public registration easier,
- change frontend auth assumptions unless necessary.

## Expected Usage

From `backend/`, after env and database are configured:

```bash
python -m app.cli create-temp-admin
```

Expected output should include the username and one-time plaintext password. The password should then be used at `/manage` and rotated or cleared after recovery.

Cleanup after recovery:

```bash
python -m app.cli disable-temp-admin
```

This disables the default temporary admin account by setting `is_admin=False` and replacing its password hash with a non-login sentinel value.

## Open Decision

Whether the temporary account should include an expiration timestamp is currently blocked by the existing schema: `users` has no expiration field. For this first narrow change, expiration should be handled operationally by documenting a cleanup command or by re-running a future schema-backed task if automatic expiry is required.
