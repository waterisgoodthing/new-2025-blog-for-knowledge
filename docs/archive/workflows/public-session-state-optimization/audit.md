# PSS-01 Contract and Consumer Audit

Current status: `COMPLETE — PSS-01～06 HISTORICAL COMPLETE; FIX-01/G3 PASS; FIX-03～05 COMPLETE; strict permission boundary unchanged; F4 input ready for separate approval; F4 not executed`.

## Frozen server contract

| Concern                   | Current source evidence                                                                                                                                    | PSS-01 decision                                                                                                                      | Boundary retained                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| Session transport         | `backend/app/routers/auth.py` sets and reads the HttpOnly `admin_session` Cookie with path `/api`; `src/lib/api/client.ts` sends `credentials: 'include'`. | Reuse the current Cookie and `AdminSession` resolver only.                                                                           | No JWT/Bearer migration or CORS expansion.                                       |
| Resolution                | `_resolve_session_user` hashes the cookie token, rejects revoked/expired sessions, and resolves the associated `User`.                                     | Add a thin optional route that calls this resolver once.                                                                             | Do not duplicate cookie parsing or alter `get_current_admin`.                    |
| Anonymous/invalid session | `get_current_user`, `get_current_admin`, and `/api/auth/me` currently turn a missing resolution into 401.                                                  | Optional route returns `200 { authenticated: false, is_admin: false }` for missing, invalid, expired, revoked, or orphaned sessions. | `/api/auth/me` remains strict 401.                                               |
| Valid session             | The resolver returns `User` plus auth level; `User.is_admin` is authoritative.                                                                             | Optional route returns only `{ authenticated: true, is_admin: user.is_admin }`.                                                      | No username, ID, auth level, expiry, session identifier, or credential material. |
| Infrastructure failure    | The resolver currently does not catch database failures.                                                                                                   | Preserve propagation as a visible server error.                                                                                      | Never translate a resolver/database fault into anonymous.                        |
| Bypass                    | Resolver has existing two-flag bypass behavior.                                                                                                            | No test or implementation activates or changes it.                                                                                   | `AUTH_BYPASS` is not a validation mechanism.                                     |

## Consumer matrix

| Runtime surface                              | Current request path                                       | Classification             | PSS-05 target    | Reason                                                                                                       |
| -------------------------------------------- | ---------------------------------------------------------- | -------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------ |
| `src/app/(home)/learning-space-card.tsx`     | `useAdminAuth()` → strict `/api/auth/me`                   | Public home                | Optional         | Display-only learning/management affordance.                                                                 |
| `src/app/about/about-content.tsx`            | same                                                       | Public about               | Optional         | Edit control must stay hidden anonymously.                                                                   |
| `src/app/blog/page.tsx`                      | same                                                       | Public blog index          | Optional         | Public reading must not be gated.                                                                            |
| `src/app/blog/[id]/blog-detail-content.tsx`  | same                                                       | Public blog detail         | Optional         | Display-only edit affordance.                                                                                |
| `src/app/bloggers/page.tsx`                  | same                                                       | Public static-content page | Optional         | Editor controls are display-only.                                                                            |
| `src/app/mistakes/page.tsx`                  | same                                                       | Public mistake index       | Optional         | Public reading remains open; no review API is authorized here.                                               |
| `src/app/notes/page.tsx`                     | same                                                       | Public notes index         | Optional         | Public reading must not be gated.                                                                            |
| `src/app/notes/[id]/note-detail-content.tsx` | same                                                       | Public note/mistake detail | Optional         | Edit/delete visibility only; backend remains the write boundary.                                             |
| `src/app/pictures/page.tsx`                  | same                                                       | Public static-content page | Optional         | Upload/edit controls stay hidden anonymously.                                                                |
| `src/app/projects/page.tsx`                  | same                                                       | Public static-content page | Optional         | Create/edit controls stay hidden anonymously.                                                                |
| `src/app/share/page.tsx`                     | same                                                       | Public static-content page | Optional         | Create/edit controls stay hidden anonymously.                                                                |
| `src/app/snippets/page.tsx`                  | same                                                       | Public static-content page | Optional         | Create/edit controls stay hidden anonymously.                                                                |
| `src/components/mobile-nav.tsx`              | same                                                       | Shared navigation          | Optional         | Only controls display of the management link.                                                                |
| `src/components/auth-gate.tsx`               | `useAdminAuth({ mode: 'strict' })` → strict `/api/auth/me` | Protected boundary         | Strict           | It must redirect rather than render a protected editor/review surface.                                       |
| `src/app/manage/page.tsx`                    | direct `getMe()` → strict `/api/auth/me`                   | Protected management/login | Strict unchanged | Login state and management access are not a public display probe.                                            |
| `src/hooks/use-blog-index.ts`                | shared `useAdminAuth({ mode: 'optional' })`                | Public blog-index helper   | Optional         | Its hidden-item display filter is a public display-state probe and must stop generating anonymous 401 noise. |

`src/components/mobile-nav.test.tsx` mocks the hook; it is test-only and not a runtime consumer. `src/hooks/use-admin-auth.ts` and `src/lib/api/auth.ts` are shared implementation surfaces rather than additional page owners.

## Explicit next-test contract

PSS-02 must first create focused failing backend tests for anonymous 200, valid admin 200, expired/revoked 200 anonymous state, an injected database failure that remains 5xx, and unchanged strict `/api/auth/me` 401. It must use only isolated fake sessions/users and keep `AUTH_BYPASS` disabled.

## PSS-02/PSS-03 closure

- Failing-first result: `tests/test_optional_session_state.py` produced `4 failed, 1 passed, 3 warnings` because the optional route did not exist. The first evidence is [PSS-02 first failure](assets/pss-02-first-failure.md).
- Minimal implementation: `SessionStateOut` contains only the two frozen booleans. `GET /api/auth/session-state` calls `_resolve_session_user` and returns those booleans without catching resolver/database failures. `/api/auth/me`, `get_current_admin`, and all mutation dependencies remain untouched.
- Final evidence: optional contract `5 passed in 0.61s`; existing auth-error and protected-write regression `9 passed in 0.45s`; cookie harness warnings removed. See [PSS-03 final pass](assets/pss-03-final-pass.md).

## PSS-04 closure

- `src/lib/api/auth.ts` exposes `SessionState` and `getSessionState()` for `/api/auth/session-state`.
- `src/hooks/use-admin-auth.ts` has explicit `optional` and `strict` modes, distinct SWR keys, a strict compatibility default, and an `error` result. Optional failure keeps `isAdmin` false while preserving the diagnostic; strict mode continues to request `/api/auth/me`.
- The named invalidator refreshes both keys after successful management login and logout. The protected `AuthGate` is explicitly `mode: 'strict'`.
- Final focused validation is 14/14 plus source TypeScript PASS. See [PSS-04 final pass](assets/pss-04-final-pass.md). The separate test-only TypeScript check remains blocked by 11 existing Markdown PoC test errors and is not attributed to PSS. Prettier still reports the three pre-existing mixed-style source files (`auth.ts`, `manage/page.tsx`, `auth-gate.tsx`); they were deliberately restored to minimal semantic diffs rather than reformatted wholesale.

## PSS-05 closure

- All 12 public pages/details and `src/components/mobile-nav.tsx` now use `useAdminAuth({ mode: 'optional' })` explicitly. This makes their display-state probe impossible to silently fall back to strict mode.
- `src/hooks/use-blog-index.ts` now shares `useAdminAuth({ mode: 'optional' })` rather than keeping a separate optional SWR key or calling strict `/api/auth/me`.
- Static contract, hook/API, strict AuthGate, `/manage`, mobile navigation, and Batch 7 regression pass 31/31; source TypeScript passes. [PSS-05 final pass](assets/pss-05-final-pass.md) preserves the initial focused result; PSS-06 revalidated the corrected shared-key source.

## PSS-06 closure

- The first isolated browser failure retained six anonymous `/api/folders` requests. Public folder loads now stop before calling `listFolders` when there is no optional administrator display state; no backend permission or endpoint behavior changed.
- The second failure showed `useBlogIndex` had a separate optional SWR key. It now consumes the shared optional hook, so each full anonymous page navigation makes exactly one optional state request instead of fan-out across public consumers.
- Final local Playwright acceptance is `3 passed (7.8s)`: anonymous `/blog`, `/notes`, `/mistakes` have no strict `/api/auth/me`, administrator API noise, or page errors; valid admin display state is removed after logout; expired Cookie resolves anonymous and `/manage` shows only login while strict `/api/auth/me` remains 401. No 5xx response occurred in the strict-page check. [PSS-06 final pass](assets/pss-06-final-pass.md) has isolation, cleanup, and warning details.

## Residual risks

- The existing resolver's bypass branch is unchanged; this work neither enables nor validates it.
- Existing public static pages contain management actions, so PSS-05 must verify only display-state selection changes and no handler or backend permission is broadened.
- G3 is PASS from the combined strict-permission and browser evidence. It is not a production migration authorization; it only releases the parent workflow's F3 evidence sequence.
