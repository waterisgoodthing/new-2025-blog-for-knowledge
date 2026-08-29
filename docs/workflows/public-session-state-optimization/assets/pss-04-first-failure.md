# PSS-04 first failing evidence

Command:

```text
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/api/auth.test.ts src/hooks/use-admin-auth.test.tsx src/app/manage/manage-auth.test.tsx --reporter=verbose
```

Result: `3 failed files; 5 failed, 3 passed` in `1.71s`.

Failures prove four missing contracts: `getSessionState` does not exist; optional mode still does not call an optional fetcher; an optional network error is swallowed without diagnostic state; and successful login/logout do not invalidate session-state caches. Existing strict hook behavior and three existing management assertions passed.
