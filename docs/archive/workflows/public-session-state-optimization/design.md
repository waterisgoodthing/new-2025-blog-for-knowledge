# Design

## 1. Verified Current Flow

```text
public page/component
    -> useAdminAuth()
    -> SWR "admin-session-check"
    -> getMe()
    -> GET /api/auth/me
    -> anonymous response 401
    -> hook catches error and returns false
```

The UI is safe, but strict identity semantics are being used as a public display-state probe.

## 2. Target Flow

```text
public page/component
    -> useAdminAuth({ mode: "optional" })
    -> shared SWR optional-session key
    -> GET /api/auth/session-state
    -> 200 { authenticated: false, is_admin: false }

AuthGate / manage / protected tools
    -> useAdminAuth({ mode: "strict" })
    -> GET /api/auth/me
    -> existing 200 / 401 / 403 semantics

all writes
    -> backend get_current_admin
```

## 3. Backend Contract

Add a minimal response schema such as:

```json
{
	"authenticated": false,
	"is_admin": false
}
```

The optional endpoint may inspect the existing HttpOnly session cookie. Missing, expired, revoked, or invalid sessions return the anonymous boolean state. Database or unexpected validation failures return an error and are not silently hidden.

The implementation should reuse existing session validation logic through an optional helper rather than duplicate cookie parsing. It must not change `GET /api/auth/me` or any mutation dependency.

Expected ownership:

- `backend/app/schemas/auth.py`: minimal response contract;
- `backend/app/routers/auth.py`: thin optional-session route;
- `backend/app/utils/auth.py` or an existing auth service: reusable optional session lookup;
- backend auth/permission tests.

## 4. Frontend Contract

- `src/lib/api/auth.ts` adds a typed optional-session request.
- `src/hooks/use-admin-auth.ts` exposes explicit `optional` and `strict` modes. Its compatibility default is `strict` until PSS-05 changes every public consumer to explicit `optional`; this prevents mode-splitting from silently performing the consumer migration one item early.
- Public consumers use optional mode.
- `AuthGate` continues strict mode.
- Login success and logout invalidate both strict and optional SWR keys so public controls update without reload.

## 5. Current Consumer Classification

The implementation task must verify, not blindly bulk-replace, current consumers including:

- public content: `/notes`, `/blog`, `/mistakes` and public detail components;
- public/static surfaces: home learning card, about, bloggers, pictures, projects, share, snippets;
- shared navigation: mobile navigation;
- protected boundary: `AuthGate` and `/manage`.

## 6. Failure and Security Rules

- Anonymous optional state: public UI renders with administrator controls hidden.
- Optional-state network failure: same safe UI result, with diagnostics available to tests/logging.
- Valid administrator: public controls may appear, but backend still validates every operation.
- Stale/revoked session: optional state becomes anonymous; strict pages reject access.
- Never cache a valid administrator state across users or browser contexts.

## 7. Rollback

Rollback removes the optional endpoint and restores public consumers to the previous hook behavior. Backend strict permissions remain unchanged throughout, so rollback cannot be used to justify weakening authorization.
