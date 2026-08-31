# C10 Browser Testing

Date: 2026-07-29

Environment:

- Frontend: `http://localhost:3000`, local Next.js development server.
- Backend: `http://127.0.0.1:18000`, bound to loopback and connected only to `i_series_c10_acceptance_20260729_125558`.
- Auth: real password login and cookie session with `AUTH_BYPASS=false` and `AUTH_BYPASS_ALLOW=false`.
- Network containment: browser allowlist limited to `localhost,127.0.0.1`.

## Results

| Scenario | Result | Evidence |
|---|---|---|
| Anonymous `/manage/dashboard` | PASS | Redirected to `/manage`; login form exposed username/password controls rather than workspace content. |
| Password administrator login | PASS | Form login returned to the authenticated manage panel and displayed `c10-admin`; `/manage/dashboard` rendered the learning dashboard. |
| Mobile 375x812 | PASS | `scrollWidth=clientWidth=375`; mobile header and bottom navigation were usable; no visible overlap or clipping. Screenshot: `c10-mobile-375x812.png`. |
| Tablet 768x1024 | PASS | `scrollWidth=clientWidth=768`; side navigation and dashboard content remained readable. Screenshot: `c10-tablet-768x1024.png`. |
| Desktop 1280x800 | PASS | `scrollWidth=clientWidth=1280`; full navigation and dashboard content rendered without overlap. Screenshot: `c10-desktop-1280x800.png`. |
| Keyboard navigation | PASS | Six consecutive real Tab presses reached visible links for home, blog, notes, mistakes, discover, and guestbook. Each icon-only link exposed an `aria-label`. |
| Browser errors | PASS | Agent-browser error buffer was empty. |

Visual inspection confirmed that on-screen text, controls, navigation, and content did not overlap at any tested size. The development console contained only HMR/React development messages and an existing Next.js LCP suggestion for `/images/avatar.png`; the LCP suggestion is a non-blocking performance follow-up, not an acceptance failure.

Agent-browser 0.33.1 established and drove the real browser session successfully. Its accessibility `snapshot` and npm-wrapped `wait` client commands did not exit reliably on this Next.js page, so the run used the same browser session with direct CLI `open`, CSS-selector form interaction, DOM evaluation, real key presses, screenshots, console, and error-buffer inspection. This tooling limitation did not alter application behavior or validation results.

Conclusion: `PASS`.
