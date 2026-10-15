# Requirements

## Background and Roles

Public visitors need published content without authentication error noise. The personal administrator needs edit and management affordances to appear when a valid session exists. Backend authorization remains the real security boundary.

## Functional Requirements

### PSS-REQ-01 Optional session state

- Input: a request with no cookie, an expired cookie, or a valid administrator session cookie;
- Processing: validate the cookie when present without throwing an authentication error for an anonymous request;
- Output: a minimal boolean session-state response; do not return private profile data to anonymous callers;
- Failure: backend or database failures remain explicit server errors and must not be converted to “anonymous”;
- Proof: API tests cover anonymous, expired, valid-admin, and infrastructure-failure behavior.

### PSS-REQ-02 Strict identity preservation

- Input: calls to strict identity and protected mutation endpoints;
- Processing: continue using existing strict authentication dependencies;
- Output: existing 401/403 behavior remains unchanged;
- Failure: any test showing anonymous access to protected data blocks completion;
- Proof: existing permission tests plus targeted regression tests pass.

### PSS-REQ-03 Shared frontend state

- Input: public components requesting administrator display state;
- Processing: use one deduplicated optional-session key; protected components use strict mode;
- Output: anonymous public pages resolve to non-admin without expected 401 noise, while valid administrators retain management controls;
- Failure: network failures degrade public UI safely without exposing controls;
- Proof: hook tests and browser request logs.

### PSS-REQ-04 Public route coverage

- Input: all current `useAdminAuth` consumers outside protected management flows;
- Processing: classify each as public, protected, or shared navigation and migrate it to the correct mode;
- Output: no public content route becomes gated and no protected route becomes optional;
- Failure: ambiguous ownership is recorded and left unchanged until resolved;
- Proof: route matrix and browser checks for `/notes`, `/blog`, `/mistakes`, public details, and shared navigation.

## Non-functional Requirements

- Security: frontend state is display-only and never authorizes a backend operation.
- Performance: one shared optional-session request per SWR dedupe window; no request fan-out by component count.
- Privacy: optional response contains no username, session identifier, expiry time, or credential material unless separately justified.
- Compatibility: login, logout, cookie sessions, Passkey sessions, and protected pages retain current behavior.
- Auditability: request status and public/admin DOM outcomes are recorded in `validation.md`.

## Exclusions

- No auth-provider migration, JWT conversion, registration change, CORS expansion, route redesign, or authentication bypass.
- No unrelated UI refactor or performance optimization.
