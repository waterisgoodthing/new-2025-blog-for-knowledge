# Public Session State Optimization

## Goal

Remove expected anonymous 401 noise from public pages while preserving administrator-only UI and every existing backend authorization boundary.

## Evidence Source

- [Render timing acceptance](../page-render-timing-validation/acceptance.md)
- [Residual risk RISK-RT-001](../page-render-timing-validation/risks.md)
- [Next requirement REQ-RT-001](../page-render-timing-validation/next-requirements.md)

The browser probe verified that anonymous `/notes` renders successfully but calls strict `GET /api/auth/me` and receives 401. Source inventory shows that the same shared hook is used across multiple public routes and shared navigation components, so this is a shared auth-state concern rather than a single-page patch.

## Touched Domains

- `auth`: optional session-state contract only;
- public `notes`, `blog`, `mistakes` and other current `useAdminAuth` consumers;
- shared frontend API and authentication hook;
- tests and browser validation.

## Status

`COMPLETE — PSS-01～06 HISTORICAL COMPLETE; FIX-01/G3 PASS; FIX-03～05 COMPLETE; F4 INPUT READY FOR SEPARATE APPROVAL; F4 NOT EXECUTED`

The user explicitly approved the repair checklist for this Goal. G2 remains an isolated PoC result only. PSS-01 through PSS-06 are historical Cookie-session and list/session evidence; FIX-01's current isolated Chromium `5 passed (12.6s)` adds public blog detail, public note detail, and a 390px actual shared-mobile-navigation mount. G3 is PASS only for completing the F4-input repair, not for a Cookie-to-Bearer migration, any permission relaxation, F4, Git, or deployment.

## Documents

- [Design](design.md)
- [Requirements](requirements.md)
- [Tasks](tasks.md)
- [Audit](audit.md)
- [Validation](validation.md)

## Hard Boundary

This task must not weaken `GET /api/auth/me`, `AuthGate`, `get_current_admin`, mutation permissions, review permissions, AI permissions, uploads, or `AUTH_BYPASS` rules.
