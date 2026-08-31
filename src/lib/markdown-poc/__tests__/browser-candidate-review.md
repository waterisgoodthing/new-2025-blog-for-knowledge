# Browser Test Runner — Deferred Decision

## Current state (2026-08-10)

- Project uses vitest + jsdom for all tests.
- No Playwright, Puppeteer, or WebdriverIO installed.
- jsdom does not execute scripts, does not render SVG, and does not
  fully simulate browser event delegation or navigation interception.
- For M3, jsdom is sufficient to test HTML string output.
- jsdom 只能验证 DOM/HTML 结构，不能证明真实浏览器执行。

## Deferred decision

Real browser runner selection is **deferred to M5/M6**. Before installing:

- Must re-query official npm metadata (e.g. `npm view @playwright/test version`,
  `npm view puppeteer version`) to determine the current stable release.
- Must re-evaluate install size, license, advisories, and peer dependencies
  against the current project lockfile.
- No version numbers, "latest stable" claims, or security/size assertions in
  this document should be relied upon without a fresh query.

## jsdom applicability (M3 only)

- jsdom is sufficient for M3 HTML/assertion tests.
- jsdom does NOT execute `<script>` tags, so any script-survival test must
  rely on HTML string inspection, not on a `__markdownPocXss` global flag.
- SVG rendering, Canvas drawing, real event dispatch, and dangerous navigation
  interception require a real browser runner.
- These capabilities are required for M5/M6 and are a hard gate (G2) before
  any go/no-go decision.

## Notes

- M3 dom-safety.test.ts uses jsdom for HTML structure validation only.
- Real browser SVG/Canvas/event/navigation testing → M5/M6 (Playwright or
  Puppeteer, to be decided at that time).
- No dependency install in M3 or M4.
