# PSS-02 first failing evidence

Command:

```text
cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_optional_session_state.py -q
```

Result: `4 failed, 1 passed, 3 warnings in 0.68s`.

The first four focused optional-session tests received `404 Not Found` from the intentionally absent `/api/auth/session-state` route: anonymous 200, valid-admin 200, expired-session anonymous downgrade, and visible infrastructure failure. The unchanged strict anonymous `/api/auth/me` regression passed.

Warnings were three Starlette `DeprecationWarning` messages for per-request test cookies. They do not change the missing-route cause and will be removed after the endpoint implementation without altering the session contract.
