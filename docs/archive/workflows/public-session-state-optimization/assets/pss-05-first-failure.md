# PSS-05 first failing evidence

Command:

```text
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/app/public-session-state-consumers.test.ts --reporter=verbose
```

Result: `1 failed file / 14 failed tests` in `0.46s`.

All 13 public/shared `useAdminAuth()` consumers lack explicit optional mode. The public `use-blog-index` helper still imports `apiFetch` and calls strict `/api/auth/me`. This is an expected migration gap; protected `AuthGate` and `/manage` are not part of the failing list.
