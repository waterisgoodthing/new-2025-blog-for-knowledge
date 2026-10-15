# PSS-06 first browser failure

Command:

```text
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test --config=docs/workflows/public-session-state-optimization/playwright.config.ts
```

Result: `1 failed, 2 did not run` in `9.4s`.

The anonymous browser correctly made no strict `/api/auth/me` request, but the public `/notes` and `/mistakes` surfaces made six requests to `/api/folders`. The failure is the exact assertion that public pages must have no administrator API noise. Playwright retained the screenshot, trace, and error-context bundle in `assets/playwright-test-results/public-session-state.brows-93bfd--administrator-API-requests/`.

The isolated harness used only in-memory synthetic sessions on `127.0.0.1:8001`; the frontend ran locally on `127.0.0.1:3000`. Both Playwright-managed processes exited after the failure. Existing `SiteSettingsLoader` emitted unrelated console errors because the harness intentionally has no content-store database; the next test revision will fulfill that public response synthetically rather than mistake it for an auth result.
