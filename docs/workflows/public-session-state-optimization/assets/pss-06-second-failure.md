# PSS-06 second browser failure

Command: same isolated Playwright matrix as PSS-06 first browser run.

Result: anonymous public pages made zero strict `/api/auth/me` and zero administrator API requests, but made four `/api/auth/session-state` requests across `/blog`, `/notes`, and `/mistakes`.

The folder guard worked. The remaining failure is that `useBlogIndex` owns a second `admin-auth-check` SWR key instead of reusing `useAdminAuth({ mode: 'optional' })`. The next single change is to reuse that shared hook key. The test's synthetic site settings also exposed unrelated `MusicCard` console errors caused by an incomplete synthetic card-style object; that is deliberately deferred until the session-key fix is re-run.
