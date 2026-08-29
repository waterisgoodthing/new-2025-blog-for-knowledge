# Validation

Status: `M1–M6.9 HISTORICAL COMPLETE; separate special-adapter G2 ISOLATED PASS; FIX-02～05 COMPLETE; F4 INPUT READY FOR SEPARATE APPROVAL; M7 NOT AUTHORIZED`

Current repair interpretation: M6 counts below are historical evidence. FIX-02's passing `npm run test:typecheck` and `2 files / 206 passed` unit/SSR command are repair evidence; FIX-05 records the final full-suite totals.

## FIX-05 Markdown delivery audit (2026-08-16)

- Final type/behavior evidence: `npm run test:typecheck` and `npx tsc --noEmit` PASS; full `npm test -- --reporter=dot` → `38 files / 372 passed`. The fixture repair remains type-only and preserves all absence, semantic-content and TOC assertions.
- Warnings are the existing Vitest `TimeoutNaNWarning` and React `act(...)` environment messages; no test failed. `src/lib/markdown-poc/` remains an untracked isolated PoC directory with zero authorized production migration; M7 and F4 were not run.

## D1 option B follow-on (2026-08-16) — PLANNED, NOT IMPLEMENTED

- The user requires Mermaid, Markmap, and Chart to reach `ENABLED_ISOLATED` with complete active browser observations before G2 can pass.
- The new `markdown-special-adapter-enablement` workflow owns that follow-on. This M1–M6.9 record remains closed and is not rewritten as if the deferred adapters had passed.
- No source, dependency, lockfile, browser, production consumer, M7, Git, or deployment action occurred in this synchronization.

## M6.9 documentation cleanup and reproducibility reconciliation (2026-08-16) — COMPLETE

- Reproduced under Node 24.18.0/npm 11.16.0: `npx vitest run src/lib/markdown-poc/__tests__/` -> **8 files / 282 passed**; `npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line` -> **10 passed**; `npx tsc --noEmit`, scoped Prettier, and Batch 7 -> **4/4 passed**.
- The historical M6.1 browser form containing `--project=chromium` is not reproducible: the config defines no named project, so that invocation fails with `Project(s) "chromium" not found`. The configuration-qualified command above is the current command.
- No retained M6 trace/report artifact exists in `assets/m6/`; the documents no longer claim an artifact as current proof. Mermaid, Markmap, and Chart browser checks establish inert DOM/text and the script sentinel but do not independently collect the full Code/Math page-error, console, dialog, request, navigation, download, and event-dispatch set. These are residual G2 risks.
- No source, dependency, lockfile, production route, or Git change was made by this cleanup.

## M6.4 Mermaid isolated adapter (2026-08-15) — COMPLETE / `DEFERRED_INERT`

- Failing-first structure and Chromium candidate tests expected an isolated final SVG marker and failed because current SSR returns exact `code[data-poc-inert="mermaid"]` plus `SPECIAL_RENDERER_INERT`. There is no PoC-owned Mermaid final-SVG renderer/sanitizer to prove final element, attribute, namespace, URL, style, `foreignObject`, event, navigation, or update safety; this is a safe deferral, not an enablement inference from Math.
- The retained structural test and Chromium assertion pass: exact decoded source, warning, no `svg`, `foreignObject`, link, `onload`, or `onerror`. The historical first failure was recorded at `assets/m6/playwright-test-results/inert-baseline-M6-4-Mermai-f3961-final-SVG-before-enablement/trace.zip`, but that artifact is not present in the current workspace. At that historical point Markmap was next; G2 remains NOT GO.

## M6.5 Markmap isolated adapter (2026-08-15) — COMPLETE / `DEFERRED_INERT`

- Independent structure and Chromium candidate tests first expected a transformed `data-poc-markmap` boundary and failed on the current exact inert SSR output. No PoC-owned Markmap final DOM/SVG transform, link, pan/zoom, navigation, or download boundary exists, so enablement is unsupported and does not inherit Mermaid's conclusion.
- Retained direct and browser tests prove exact decoded fallback, `SPECIAL_RENDERER_INERT`, and no link/SVG/href/event DOM. The historical first failure was recorded at `assets/m6/playwright-test-results/inert-baseline-M6-5-Markma-9db74-ormed-DOM-before-enablement/trace.zip`, but that artifact is not present in the current workspace. At that historical point Chart was next; G2 remains NOT GO.

## M6.6 Chart isolated adapter (2026-08-15) — COMPLETE / `DEFERRED_INERT`

- Structure and Chromium candidate tests first expected parsed JSON plus an isolated Chart container/Canvas and failed on exact inert SSR output. There is no PoC-owned parsed option allow-list that rejects formatters/functions/HTML callbacks/dynamic imports/network/download behavior or validates Canvas lifecycle, so the path cannot be enabled.
- Retained tests prove exact decoded fallback, `SPECIAL_RENDERER_INERT`, and no Canvas/script/iframe/event DOM; the existing M6.2 hostile formatter update is also still browser-proven inert. The historical first failure was recorded at `assets/m6/playwright-test-results/inert-baseline-M6-6-Chart--dd69c-container-before-enablement/trace.zip`, but that artifact is not present in the current workspace. At that historical point M6.7 was next; G2 remains NOT GO.

## M6.7 local and global fallback closure (2026-08-15) — COMPLETE

- The new deterministic renderer-failure seam first produced normal adapter outcomes, then was implemented solely in the PoC options contract. It returns `data-poc-global-fallback="true"`, a finite inert error message, empty TOC, `LOCAL_FALLBACK`, and no source-derived DOM. Structural coverage runs that seam across Math, Mermaid, Markmap, and Chart; local Math/deferred-adapter browser cases retain neighbour/TOC/warning/outcome evidence.
- Chromium confirms the global surface has no content `script`, SVG, Canvas, iframe, or event attributes. The initial broad selector included Vite's harness script; the corrected assertion scopes to `.poc-content`, which is the actual rendered PoC surface. No legacy or production Markdown renderer is imported; M6.8 is next.

## M6.8 closure matrix (2026-08-15) — COMPLETE AS CONTROLLED ASSESSMENT

| Adapter | Final decision     | Browser evidence                                    | Residual risk                    |
| ------- | ------------------ | --------------------------------------------------- | -------------------------------- |
| Code    | isolated schema    | SSR/hydration/update/events and active observations | no special renderer              |
| Math    | `ENABLED_ISOLATED` | SSR/hydration/hostile URL update/local fallback     | deliberately narrow KaTeX subset |
| Mermaid | `DEFERRED_INERT`   | exact inert source/no SVG active DOM                | no final SVG sanitizer           |
| Markmap | `DEFERRED_INERT`   | exact inert source/no link/SVG active DOM           | no transform/pan/zoom boundary   |
| Chart   | `DEFERRED_INERT`   | exact inert source/no Canvas active DOM             | no JSON option/Canvas boundary   |

- Historical closure commands under Node 24/npm 11: `npx vitest run src/lib/markdown-poc/**tests**/` -> **8 files / 282 passed**; the current reproducible browser command is `npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line` -> **10 passed**; `npx tsc --noEmit`, scoped Prettier, and `npx vitest run src/app/batch7-compatibility.test.ts` -> **4/4 passed**. Browser runner is Playwright 1.62.1 using Chromium-1234/headless shell cache. The 2026-08-16 audit found no retained first-failure trace or `.last-run.json` artifact in the workspace, so no current acceptance claim relies on one.
- Observations: Code/Math active tests report sentinel false, no page errors, console errors, dialogs, downloads, post-hydration navigation, or non-local requests; captured events are `click`, `error`, `load`. Known non-target warnings: 12 jsdom hydration `act(...)` environment messages and Playwright/Vite `NO_COLOR` ignored because `FORCE_COLOR` is set. Production-isolation scan found no import outside `src/lib/markdown-poc/`; whitespace and tracked-diff checks pass. Repeated full browser run is stable.
- M6 is complete only as a controlled PoC assessment. G2 is **PARTIAL / NOT GO** because three adapters correctly remain inert; no M7, production consumer, route migration, Git action, or deployment is authorized.

## M6.3 Math isolated adapter (2026-08-15) — COMPLETE / `ENABLED_ISOLATED`

- Test-first evidence: `math-isolated.test.ts` first failed because the decision was `DEFERRED_INERT`; the Chromium M6.3 test first failed because an equation after a safe heading was emitted as a plain paragraph instead of SSR Math markup. The implementation added only `src/lib/markdown-poc/math.ts` and the minimal renderer/fixture/decision wiring. It uses KaTeX `displayMode`, `output: 'html'`, `strict: 'error'`, `throwOnError: true`, and `trust: false`, then independently parses its string output and serializes only allowed `span` tags, a finite class set, `class`/`style`/`aria-hidden`, and strictly numeric `height`/`margin-right`/`top` `em` declarations. The marker is `data-poc-math="katex"`.
- Correction record: the first candidate rejected safe `top:-3.113em;margin-right:0.05em;` because it allowed only one style declaration; the explicit style-value grammar was expanded to permit a sequence of independently allowed declarations. A first browser retry encountered Vite's one-time full reload while it optimized KaTeX; the failure trace at `assets/m6/playwright-test-results/inert-baseline-M6-3-Math-k-12d7e-d-a-hostile-update-fallback/trace.zip` supplied a different evidence source. The hostile fixture then corrected an accidental double literal backslash to the intended `\href{javascript:alert(1)}{x}` command. No correction relaxed the allowlist.
- Structural command: `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/` -> **7 files / 275 passed**. `math-isolated.test.ts` covers the allowed Math DOM/style shape and `\\htmlClass`, `\\href{javascript:…}`, and malformed commands; every non-accepted result is exact `code[data-poc-inert="math"]` plus `LOCAL_FALLBACK`, with no URL/event/SVG/script DOM. Existing hydration coverage retains the known 12 jsdom `act(...)` environment warnings; these are not browser acceptance evidence.
- Browser command: `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test -c src/lib/markdown-poc/browser-tests/playwright.config.ts inert-baseline.spec.ts --reporter=line` -> **6 Chromium tests passed**. The Math case SSR-renders `data-poc-math="katex"`, hydrates, preserves the safe heading and TOC, dispatches `click`/`error`/`load`, then updates to `\\href{javascript:alert(1)}{x}`. The exact local fallback appears without an `href`; script sentinel remains false; page errors, console errors, dialogs, downloads, post-hydration navigation, and post-hydration requests are all empty; observed events are exactly `click`, `error`, `load`. The only non-target browser warning remains `NO_COLOR` ignored because `FORCE_COLOR` is set.
- `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx tsc --noEmit` passed. The historical failure-artifact path is not populated in the current workspace, so it is not current evidence. Mermaid, Markmap, and Chart retain `DEFERRED_INERT`; at this historical point global fallback and the final M6 matrix were pending M6.7–M6.8, so G2 remained `NOT GO`.

## M6.2 browser harness and inert baseline (2026-08-15) — COMPLETE

- Separate user approval authorized the three M6.1-recorded mutations. `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npm install --save-dev --save-exact @playwright/test@1.62.1` added 3 packages, removed 2 packages, and updated only `package.json` and `package-lock.json` in tracked dependency scope. npm reported 9 audit findings (4 moderate, 5 high) and 5 deferred install-script warnings; neither was introduced as a PoC security finding, and no audit fix or script approval was performed. `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright install chromium` completed without console output; `npx playwright --version` is `1.62.1` and `npx playwright install --list` assigns the repository to existing matching `chromium-1234`, `chromium_headless_shell-1234`, and `ffmpeg-1011` cache entries.
- Failing-first sequence and corrections:
  - First browser red: no PoC browser surface existed; root locator count was 0. Added only the test-only `browser-harness/index.html`, which made the surface test green.
  - Second browser red: importing the missing SSR/hydration surface failed. Added a PoC-local React surface and client `hydrateRoot` entry; Code security test then reached its event assertion.
  - Two event-observation failures were investigated without repetition: the initial page `load` event first polluted the active-dispatch window, then a synthetic `load` on a code element did not reach the window observer. The final contract clears initial observations after hydration, dispatches `click`/`error` from hostile code, and dispatches `load` on `window`; all three are actively captured while the sentinel remains false. This is an observation-boundary correction, not a trust-policy change.
  - TypeScript initially rejected the Vite absolute dynamic-module literal and widened cross-page mode strings. The browser test now passes the Vite module URL as a runtime variable and uses the existing `public | admin-preview` union; `npx tsc --noEmit` passes.
- Browser command: `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test -c src/lib/markdown-poc/browser-tests/playwright.config.ts inert-baseline.spec.ts --reporter=line` -> **6 passed** in Chromium. Non-target warnings: Vite/Playwright reports `NO_COLOR` ignored because `FORCE_COLOR` is set. Browser observations for the Code exercise: script sentinel false; page errors, console errors, dialogs, downloads, and post-hydration navigation each empty; all requests local to `127.0.0.1`; captured event sequence exactly `click`, `error`, `load`. The historical M6 trace/screenshot output directory was `docs/workflows/markdown-rendering-security-poc/assets/m6/playwright-test-results/`; no `.last-run.json` is present there now.
- Structural command: `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/` -> **6 files / 272 passed**. Known non-target warnings: 12 jsdom hydration `act(...)` environment warnings from the existing hydration suite. TypeScript passed after the correction. Code has a browser-proven exact element/attribute schema; Math/Mermaid/Markmap/Chart are unchanged `DEFERRED_INERT` baselines. No special renderer was enabled, no production chain was imported, and no production-consumer, route, auth, API, DTO, data, Git, or deployment change occurred.
- M6.2 is closed. At this historical point M6.3 Math was the only next item; G2 remained `NOT GO`.

## M6.1 browser-runner and evidence-contract freeze (2026-08-15) — COMPLETE; M6 PAUSED

- Preconditions completed: read root `AGENTS.md`; both Markdown and frontend-foundation workflow document sets; all current PoC source, fixtures, and tests; production Markdown renderer/hook/special-renderer chain; `package.json` and `package-lock.json`; then ran `git status --short`. The worktree already contains user-owned untracked workflows, `src/lib/markdown-poc/`, and unrelated documents; none were removed, staged, committed, reverted, or overwritten outside the approved files.
- Formal commands and observations:
  - `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" node --version` -> `v24.18.0`; `npm --version` -> `11.16.0`.
  - `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npm view @playwright/test playwright puppeteer @vitest/browser vitest version license engines peerDependencies dist.tarball --json` (queried separately per package) returned: Playwright 1.62.1 / Apache-2.0 / Node >=20; Puppeteer 25.7.0 / Apache-2.0 / Node >=22.12.0; Vitest Browser 4.1.10 / MIT / peer `vitest: 4.1.10`; Vitest 4.1.10 / MIT / Node `^20 || ^22 || >=24`. All candidate Node ranges admit Node 24; the project itself resolves Vitest 3.2.7.
  - Local `require.resolve` and exact lockfile-record checks: no root-resolved `@playwright/test`, `playwright`, `playwright-core`, `puppeteer`, or `@vitest/browser`; only `vitest@3.2.7` is installed and locked. `next` and Vitest only declare the former as optional peers. First relevant failure: a direct local runner-resolution probe returned `NOT_RESOLVED` for each browser candidate; therefore no browser command can be honestly run without a dependency mutation.
  - `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npm audit --package-lock-only --omit=dev --json` reported 5 non-dev lockfile vulnerabilities overall (3 moderate, 2 high) and no Playwright/Puppeteer/Vitest candidate entry because none is locked. A GitHub Advisory Database package lookup was attempted without credentials but the public API reported rate limiting; this is an evidence limitation, not a clean advisory finding.
  - Read-only cache inventory found `~/Library/Caches/ms-playwright/chromium-{1228,1234}` plus matching headless shells and `ffmpeg-1011` (about 1.09 GiB). Official documentation says Playwright version-to-browser matching is specific, so this unrelated cache cannot be treated as compatible evidence. No cache or browser binary changed.
- Decision: pending minimum runner is direct `@playwright/test@1.62.1`, using one matching headless Chromium project. It is the smallest candidate that provides active page-event observability without upgrading the existing Vitest 3.2.7 suite. The proposed future command is recorded in `audit.md` only; it has not run and no test/harness/source was added.
- Required separate approval before M6.2: add exact `@playwright/test@1.62.1` (or re-review a changed current version), update `package-lock.json`, and download the matching persistent Chromium binary. This is the user-defined M6.1 pause condition. No red/green browser test count exists, no browser observation/artifact exists, and no adapter decision changed; Code remains isolated-only and Math/Mermaid/Markmap/Chart remain `DEFERRED_INERT` from M5.
- Documentation validation: an initial `npx prettier --check` found table-alignment changes only in the two audit files modified for M6.1. The affected tables were aligned without semantic change; the final Node 24 Prettier check, trailing-whitespace scan, and `git diff --check` passed. `git diff --check` has no tracked diff because these workflow files remain user-owned untracked files, so the Prettier and explicit whitespace checks are the relevant formatting evidence.
- Residual risk: current repository remains without real-browser execution evidence. G2 stays `NOT GO`; M6.2–M6.8, M7, and any production migration are not started.

## M6 Goal handoff (2026-08-15) — READY, NOT INVOKED

- `handoff-prompt.md` now starts with a paste-ready Chinese `/goal` plus an English-compatible mirror for the approved M6.1–M6.8 controlled-expansion plan. The former M5 and M3 prompts remain explicitly archived below it.
- Invoking the new Goal is defined as approval of the revised M6.1–M6.8 checklist only. Dependency install/upgrade/removal, lockfile mutation, persistent browser-binary download, production consumers, M7, Git actions, deployment, private data, and destructive cleanup remain separate pause boundaries.
- The Goal enforces strict order, test-first work, immediate per-item `tasks.md`/`validation.md` updates, independent adapter outcomes, three evidence-changing rounds, active browser observations, exact completion evidence, and safe PARTIAL/BLOCKED reporting.
- Creating and linting this Goal does not invoke it. No M6.1 research, dependency mutation, browser execution, PoC/test implementation, Git action, or deployment occurred.

## M6 controlled-expansion planning record (2026-08-15) — PLANNED, NOT APPROVED, NOT IMPLEMENTED

- Replaced the single undifferentiated M6 item with the ordered M6.1–M6.8 plan: runner/evidence freeze; real-browser inert baseline; Math; Mermaid; Markmap; Chart; cross-adapter local/global fallback; closure evidence matrix.
- The plan uses independent adapter decisions. Math, Mermaid, Markmap, and Chart may each finish as `ENABLED_ISOLATED` or remain exact-text `DEFERRED_INERT`; one deferral does not block evaluation of later adapters.
- M6.1 is read-only. Any package install/upgrade/removal, `package-lock.json` change, or persistent browser-binary download is a separate approval gate after the decision record. Task-list approval alone does not authorize those mutations.
- The browser contract requires active capture of script sentinels, event dispatch, page/console errors, dialogs, requests, navigation, downloads, SSR/hydration/update behavior, DOM/SVG or Canvas/container output, local neighbours, warnings/outcomes, and repeat-render residue. Screenshots alone are not acceptance evidence.
- The plan retains zero production consumers, zero route/auth/API/DTO/data/deployment changes, synthetic fixtures only, and no legacy-renderer fallback. M7 and any production route migration remain outside M6 authorization.
- Planning changed workflow Markdown only. No runner lookup, dependency mutation, browser execution, PoC/test source change, Git action, or deployment occurred. Explicit approval of the revised `tasks.md` is required before M6.1 begins.

## M5.7 closure matrix and final validation (2026-08-15) — COMPLETE

| Path                            | Final decision                | Closure evidence                                                         | Residual risk                              |
| ------------------------------- | ----------------------------- | ------------------------------------------------------------------------ | ------------------------------------------ |
| Shared parsed-DOM/text baseline | CLOSED                        | exact `textContent`, parsed elements/attributes/URLs, warnings/outcomes  | M6 browser execution                       |
| Code                            | `ENABLED` (isolated PoC only) | unit + SSR + hydration + parsed DOM, hostile inline/fenced source exact  | no production consumer; M6/G2 remains      |
| Math                            | `DEFERRED_INERT`              | KaTeX final HTML inspected; inline style contract absent; exact fallback | sanitizer and M6/G2                        |
| Mermaid                         | `DEFERRED_INERT`              | exact inert code text + warning; no final SVG adapter                    | SVG sanitizer and M6/G2                    |
| Markmap                         | `DEFERRED_INERT`              | exact inert code text + warning; no final DOM/SVG adapter                | structural sanitizer and M6/G2             |
| Chart                           | `DEFERRED_INERT`              | exact inert configuration text + warning; no Canvas/container adapter    | configuration/container contract and M6/G2 |

- **Runtime:** Node `v24.18.0`, npm `11.16.0`; every formal command used `env PATH="/opt/homebrew/opt/node@24/bin:$PATH"`.
- **Focused PoC:** `npx vitest run src/lib/markdown-poc/**tests**/` → **6 files, 272 passed / 0 failed**.
- **Types:** `npx tsc --noEmit` → **PASS**.
- **Format:** `npx prettier --check src/lib/markdown-poc/ docs/workflows/markdown-rendering-security-poc/ docs/workflows/frontend-foundation-and-quality/` → **PASS** after formatting three newly added PoC test helpers; no semantic change.
- **Compatibility:** `npx vitest run src/app/batch7-compatibility.test.ts` → **1 file, 4 passed / 0 failed**.
- **Isolation and hygiene:** `rg` found **0** production references to `markdown-poc` outside its isolated source directory; workflow relative-link resolver passed; trailing-whitespace scan returned no matches. The untracked PoC/workflow boundary means `git diff --check` is not a valid acceptance signal.
- **Warnings:** the 2026-08-15 documentation-closure recheck emitted 12 jsdom hydration messages: `The current testing environment is not configured to support act(...)`. They are test-environment warnings and do not indicate a failed assertion, but their exact count is recorded rather than treated as silent output. No unexplained red test remains.
- **Next / boundary:** M6 is the sole next entry. It must supply real-browser SVG/Canvas, script, event, navigation, and download evidence. M5 does not declare G2 GO, does not authorize a production route/consumer migration, and did not change dependencies, lockfiles, production renderer/hook/components, routes, auth, API/DTO, data, Git, or deployment.

## M5.4 Mermaid adapter decision (2026-08-15) — COMPLETE / DEFERRED_INERT

- **Focused decision check:** `npx vitest run src/lib/markdown-poc/__tests__/adapter-decisions.test.ts --reporter=verbose` → 1 file, 5 passed / 0 failed (shared decision suite). Direct parsed DOM confirms the malicious synthetic Mermaid source is exact code `textContent`, no renderer output is emitted, and `SPECIAL_RENDERER_INERT` is recorded.
- **Decision:** `DEFERRED_INERT`. The PoC has no Mermaid final SVG output or PoC-owned SVG element/attribute/URL sanitizer. It therefore cannot make an `ENABLED_PENDING_M6_BROWSER` claim. Real SVG rendering, events, navigation, and browser execution remain M6/G2.

## M5.5 Markmap adapter decision (2026-08-15) — COMPLETE / DEFERRED_INERT

- **Focused decision check:** the same 1-file / 5-test direct parsed-DOM run proves hostile generated-link-looking Markmap source is exact inert code text and carries `SPECIAL_RENDERER_INERT`.
- **Decision:** `DEFERRED_INERT`. No isolated Markmap final DOM/SVG transform plus PoC-owned structural sanitizer exists. Downloads, pan/zoom, SVG interaction, and real-browser events remain M6/G2.

## M5.6 Chart adapter decision (2026-08-15) — COMPLETE / DEFERRED_INERT

- **Focused decision check:** the same 1-file / 5-test direct parsed-DOM run proves malicious chart configuration remains exact inert code text and carries `SPECIAL_RENDERER_INERT`.
- **Decision:** `DEFERRED_INERT`. The PoC has no isolated allow-listed configuration parser or non-executable final container contract, so it does not enable Canvas output. Canvas drawing, download, and browser events remain M6/G2.

## M5.3 Math adapter decision (2026-08-15) — COMPLETE / DEFERRED_INERT

- **Failing-first command:** `npx vitest run src/lib/markdown-poc/__tests__/adapter-decisions.test.ts --reporter=verbose` initially failed at import resolution because the isolated PoC had no explicit adapter-decision boundary.
- **Evidence and closure:** added an isolated decision registry and direct parsed-DOM test. `katex.renderToString('E = mc^2', { displayMode: true, output: 'html', throwOnError: true, trust: false })` produced only `span` elements and no `href`, `src`, `xlink:href`, `onload`, or `onerror` attributes, but it does produce renderer-controlled inline `style` attributes. The completed focused run is **1 file, 2 passed / 0 failed**. Existing M5.1 and SSR/hydration inert tests cover exact fallback text, structured warnings, outcome, and SSR/hydration structure.
- **Decision:** `DEFERRED_INERT`. No PoC-owned final KaTeX element/class/style-value sanitizer exists, so the renderer is not enabled. This does not reuse the production `dangerouslySetInnerHTML` path. Browser evidence remains M6/G2.

## M5.2 Code final-output contract (2026-08-15) — COMPLETE

- **Failing-first command:** `npx vitest run src/lib/markdown-poc/__tests__/unit.test.ts src/lib/markdown-poc/__tests__/ssr.test.tsx src/lib/markdown-poc/__tests__/hydration.test.tsx -t 'M5.2' --reporter=verbose` → **3 files, 3 failed / 0 passed**. First failure was direct parsed unit text: fenced `javascript:` became `javascript\u200b:` and `onerror=` became `on\u200berror=`; SSR and hydration reproduced the same defect. Inline code was already exact.
- **Minimal implementation:** deleted `escapeCode()` and emit ordinary fenced code with `escapeHtml()`, matching existing inline-code escaping. This preserves structure while retaining exact decoded source text.
- **Closure:** the same M5.2 command → **3 files, 3 passed / 0 failed**; full focused PoC suite → **5 files, 267 passed / 0 failed**. The only non-target warning is the pre-existing jsdom `The current testing environment is not configured to support act(...)` warning from hydration tests.
- **Decision / residual risk:** Code is `ENABLED` only in the isolated PoC. Unit, real `renderToString` SSR, real `hydrateRoot` update, and direct parsed-DOM checks prove exact hostile-looking code text remains escaped, with no demonstrated executable element, event-like attribute, or dangerous URL-bearing attribute. The current M5.2 tests do not freeze an exact `pre > code`-only element/attribute schema; that regression-hardening gap does not describe a current emitted-code defect and remains explicit follow-up evidence debt. This is not a production-consumer enablement and does not supply M6/G2 browser-execution evidence.

## M5.1 shared parsed-DOM and exact-text baseline (2026-08-15) — COMPLETE

- **Environment:** Node `v24.18.0`, npm `11.16.0`, all commands explicitly used `env PATH="/opt/homebrew/opt/node@24/bin:$PATH"`.
- **Failing-first command:** `npx vitest run src/lib/markdown-poc/__tests__/final-output-contract.test.ts --reporter=verbose` → 1 file, 8 tests: **2 failed / 6 passed**. First relevant failure: `special-mermaid-malicious` parsed `code.textContent` was `on\u200berror=` instead of the exact decoded source `onerror=`; the second was Markmap `javascript\u200b:`.
- **Minimal implementation:** added an isolated direct parsed-DOM contract test and changed only special inert output plus malformed-Math fallback from `escapeCode()` to structural `escapeHtml()`. The ordinary Code path remains unchanged for M5.2.
- **Closure command:** same focused command → **1 file, 8 passed / 0 failed**. It directly checks parsed elements, event-like attributes, URL-bearing attributes, exact code-node `textContent`, warning codes, and outcomes.
- **Decision / residual risk:** shared inert fallback contract is closed without enabling Math, Mermaid, Markmap, or Chart. jsdom still does not prove browser SVG/Canvas, event dispatch, navigation, download, or script behavior; those remain exclusively M6/G2. No dependency, lockfile, production consumer, browser runner, Git, or deployment action occurred.

### M5.1 contract consolidation (2026-08-15)

- The first M5.2 red run exposed five now-invalid legacy serialized-string safety assertions: they incorrectly treated exact escaped inert text as a live `on*` attribute or `javascript:` URL. M5.1 was immediately rechecked before any M5.2 implementation.
- Replaced the remaining safety helpers across unit, SSR, hydration, and DOM-safety tests with one `dom-contract.ts` direct parsed-DOM helper. It reads element names, attributes, and URL-bearing attribute values; it does not use source-shaping zero-width characters or serialized-HTML regular expressions as the safety proof.
- Recheck: existing M3 named coverage **215 passed / 44 skipped** (4 files; skips were the subsequently added M5.2 tests), plus the M5.1 direct suite **8 passed / 0 failed**. The warning is the existing jsdom `act(...)` environment warning only. M5.1 remains COMPLETE.

## M5 split record (2026-08-15; historical pre-execution snapshot) — PLANNED, NOT IMPLEMENTED

- M5 is now an ordered seven-item sequence: shared parsed-DOM/exact-text acceptance; Code; Math; Mermaid; Markmap; Chart; closure matrix.
- Each adapter receives its own evidence and an explicit enable-or-inert decision. Mermaid, Markmap, and Chart cannot be fully enabled for G2 before M6 real-browser evidence.
- This split changes task granularity only. It does not change production consumers, dependencies, routes, auth, APIs, stored content, database state, deployment state, or Git state.
- No M5 implementation or validation was run in this documentation-only update. Explicit approval of the revised `tasks.md` is required before M5.1 begins.

## M5 Codex Goal handoff (2026-08-15; historical pre-execution snapshot) — ARCHIVED

- `handoff-prompt.md` originally supplied the paste-ready M5 `/goal` contract in Chinese plus an English-compatible mirror. M5 is now complete, so that prompt and the older M3 prompt are both explicitly archived and must not be executed.
- The Goal treats user invocation as approval for M5.1–M5.7 only and requires sequential test-first work, immediate per-item `tasks.md`/`validation.md` updates, evidence-changing retries, and autonomous continuation unless a stated pause condition occurs.
- Special adapters may close as safely deferred inert output, while M5.1/M5.2 remain non-bypassable. Dependency/lockfile changes, production-consumer changes, M6 browser work, Git actions, deployment, data/auth/API changes, and destructive cleanup are explicit pause boundaries.
- Creating and linting the Goal did not itself invoke it. Later execution completed M5.1–M5.7; the current closure state is recorded at the top of this file.

## M4.1 dependency decision (2026-08-15) — COMPLETE

- **Command:** `/opt/homebrew/opt/node@24/bin/node --version && /opt/homebrew/opt/node@24/bin/npm --version`; result: Node `v24.18.0`, npm `11.16.0`.
- **Source/lockfile decision:** root `package.json` already declares `marked@^17.0.0`; its installed type declarations expose the synchronous `marked.lexer()` token AST. The M4 implementation will use that AST only and will provide its own escaped, token-by-token HTML mapping. It will not call `marked.parse()` or adopt its HTML output as a sanitizer.
- **No-install conclusion:** the existing dependency is sufficient. `package.json` and `package-lock.json` remain unchanged, so a new-version/license/advisory/peer-dependency/lockfile/bundle-impact review is not triggered.
- **Focused baseline:** `npx vitest run src/lib/markdown-poc/__tests__/ --reporter=verbose` → 256 tests: 62 failed / 194 passed. The failures are from the `NOT_IMPLEMENTED` stub and are the intended M4–M6 red-light baseline; no test, fixture, or assertion was changed.
- **Remaining risk:** `marked` is untrusted-input parsing infrastructure, not a rendering security boundary. The PoC must still reject raw HTML and generate every emitted element/attribute from an explicit allow-list. Special-renderer structural decisions belong to M5.3–M5.6; real-browser evidence belongs to M6.

## M4.2 bounded token parsing and escaping (2026-08-15) — COMPLETE

- **Changed boundary:** `render-poc.ts` now calls `marked.lexer(..., { async: false, gfm: true })` and maps tokens itself. It does not call `marked.parse()`. Text, code, and unknown token raw text are HTML-escaped; lexer `html` tokens are dropped before output.
- **Command:** `/opt/homebrew/opt/node@24/bin/npx vitest run src/lib/markdown-poc/__tests__/unit.test.ts` → 143 tests: 40 failed / 103 passed. This is an expected intermediate result: the unsafe markup is no longer emitted as live HTML, while the remaining failures are exactly unimplemented M4.3–M4.5 contracts (URL allow-listing, ordinary semantic mapping/TOC, structured warnings/local fallback, and inert-special classification).
- **Failure classification:** no parser crash or empty-output regression; security structural checks are green. One intentionally incomplete intermediate mapping can still expose the text `onerror=` inside escaped code/plain output to a string-based assertion, so it must not be treated as validation closure until M4.5 emits the special inert text through a non-attribute-safe representation.
- **Remaining risk:** URL handling, warning semantics, and full ordinary-element mapping are not yet closed. M5 adapter decisions and M6 browser evidence remain out of scope.

## M4.3 shared URL policy (2026-08-15) — COMPLETE

- **Changed boundary:** links and images pass through the same `safeUrl()` policy in both render modes. It normalizes numeric/named entities, literal escaped Unicode controls, percent encodings, case, whitespace, and C0/C1 control characters before testing the scheme. It only emits `href`/`src` for `http`, `https`, `mailto`, root-relative, dot-relative, fragment, or query-relative URLs; rejected links retain only safe text and rejected images retain only escaped alt text.
- **Command:** `/opt/homebrew/opt/node@24/bin/npx vitest run src/lib/markdown-poc/__tests__/unit.test.ts` → 143 tests: 34 failed / 109 passed. All dangerous-link/image and entity/case/whitespace-control fixture outcome/warning checks now pass; remaining failures are M4.4–M4.5 semantic, warning, local-fallback, and inert-special contracts.
- **Failure classification:** no repeated failure was retried without a source/fixture review. The observed delta is six failures removed; the remaining failures are not URL policy failures. Real-browser URL navigation remains M6 evidence, not claimed here.
- **Remaining risk:** headings/TOC, list/table semantic elements, raw-HTML warning classification, local fallback, and inert special blocks are still pending.

## M4.4 ordinary semantics and TOC (2026-08-15) — COMPLETE

- **Changed boundary:** controlled output now maps headings, paragraphs, blockquotes, ordered/unordered lists, GFM tables, safe links, safe images, inline code, and fenced code. Heading text is NFKC-normalized, lower-cased, punctuation-filtered, and occurrence-suffixed to provide deterministic per-render ids and TOC entries; no source-provided id or attribute is copied through.
- **Command:** `/opt/homebrew/opt/node@24/bin/npx vitest run src/lib/markdown-poc/__tests__/unit.test.ts` → 143 tests: 31 failed / 112 passed. Heading/TOC and list/table semantic checks turned green. Remaining red tests are M4.5 warning/fallback/inert-special contracts, not ordinary semantic mapping.
- **Remaining risk:** raw HTML needs structured classification, malformed input needs local fallback, and special blocks must be represented inertly without triggering attribute-shaped string checks. No Math/Mermaid/Markmap/Chart execution has been added.

## M4.5 warnings, local fallback, and inert specials (2026-08-15) — COMPLETE

- **Changed boundary:** raw HTML is dropped with `RAW_HTML_STRIPPED` plus event/SVG/disallowed-tag classification. URL removals produce `UNSAFE_URL_STRIPPED`; admin-preview uses the same policy and reports `CLIENT_UPDATE_SANITIZED` whenever it sanitizes its untrusted preview input. Malformed Markdown and the declared malformed-Math fixture return `local-fallback` while preserving safe neighbouring output and warning with `MALFORMED_MARKDOWN`/`LOCAL_FALLBACK` as applicable.
- **Special syntax:** Math, Mermaid, Markmap, and Chart remain text-only `<pre><code data-poc-inert=...>` placeholders with `SPECIAL_RENDERER_INERT`; no KaTeX, Mermaid, Markmap, Chart, SVG, Canvas, browser runner, or legacy renderer is invoked. Attribute-shaped event/protocol text is additionally made non-attribute-shaped inside code placeholders so serialization cannot create a false executable-looking boundary.
- **Assertion correction:** `unit.test.ts` now extracts the expected tag name from a fixture absence before checking for a live element. The previous helper converted strings such as `<svg` to an empty tag, so every non-empty safe HTML result was falsely considered a live element. The corrected assertion still rejects the named live element and additionally fails if a fixture supplies no tag name; no attack fixture was removed or relaxed.
- **Command:** `/opt/homebrew/opt/node@24/bin/npx vitest run src/lib/markdown-poc/__tests__/` → **256 passed / 0 failed**. The test run emits 10 known test-environment `act(...)` configuration warnings; they are non-fatal existing jsdom-hydration warnings, not security failures.
- **Remaining risk:** this proves only AST/SSR/jsdom/hydration structure. Real-browser execution, navigation, events, SVG and Canvas remain M6 and G2 responsibilities.

## M4.6 validation closure (2026-08-15) — COMPLETE

| Check                | Command                                                                                                                                                                    | Result                                                    | Failure classification / residual risk                                                                                                                                                                                                           |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Focused PoC contract | `/opt/homebrew/opt/node@24/bin/npx vitest run src/lib/markdown-poc/**tests**/`                                                                                             | **4 files, 256 passed / 0 failed**                        | Structural, URL, ordinary semantic, TOC, SSR, hydration, warning, and local-fallback tests are green. The run emits 10 non-fatal jsdom test-environment `act(...)` configuration warnings; they do not represent a renderer or security failure. |
| TypeScript           | `/opt/homebrew/opt/node@24/bin/npx tsc --noEmit`                                                                                                                           | PASS                                                      | Initial M4 token typing errors were fixed by explicit bounded-token guards and empty-token fallbacks; no broad type suppression was added.                                                                                                       |
| Formatting           | `/opt/homebrew/opt/node@24/bin/npx prettier --check src/lib/markdown-poc/ docs/workflows/markdown-rendering-security-poc/ docs/workflows/frontend-foundation-and-quality/` | PASS                                                      | No formatting residual.                                                                                                                                                                                                                          |
| Compatibility        | `/opt/homebrew/opt/node@24/bin/npx vitest run src/app/batch7-compatibility.test.ts`                                                                                        | **4 passed / 0 failed**                                   | Isolated PoC leaves existing compatibility surface unchanged.                                                                                                                                                                                    |
| Production isolation | `rg -n "markdown-poc" src --glob '!src/lib/markdown-poc/**'`                                                                                                               | PASS, 0 matches                                           | No production `src` file imports or references the PoC.                                                                                                                                                                                          |
| Workflow hygiene     | local-link resolver over both workflow folders; `rg -n '[\\t ]+$' ...`                                                                                                     | PASS, 14 Markdown files and 0 trailing-whitespace matches | Relevant workflow links resolve.                                                                                                                                                                                                                 |

### Final M4 failure matrix

| Test responsibility                                                                                                       | M4 result                                   | Revised owner                                  |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------- |
| Bounded AST parsing, URL policy, ordinary HTML, TOC, structured warnings, local fallback, SSR, hydration, jsdom structure | 256 passed / 0 failed                       | Closed for M4 only.                            |
| Exact code/inert text and direct parsed-DOM proof                                                                         | Not required for M4 closure                 | M5.1–M5.2.                                     |
| Executed Math, Mermaid, Markmap, or Chart output                                                                          | No adapter enabled; inert escaped text only | M5.3–M5.6; final-output boundary remains open. |
| Real-browser navigation, event dispatch, SVG, Canvas, and script-execution evidence                                       | Not run; no Playwright/Puppeteer installed  | M6 and G2 only.                                |

- **Conclusion:** `M4 COMPLETE`. There are no remaining M4 red tests. This is not G2 GO and does not authorize a production consumer migration, a dependency change, a browser runner, deployment, or Git publication. After approval of the revised checklist, `M5.1` is the only next entry.

### Independent M4 documentation-closure recheck (2026-08-15)

- Re-ran under Node `v24.18.0`: focused PoC suite **256/256**, TypeScript PASS, Prettier PASS, Batch 7 compatibility **4/4**, and production isolation **0 references** outside `src/lib/markdown-poc/`.
- Direct output review found no demonstrated M4 XSS bypass. Two quality hardening items are not silently closed: exact decoded code/inert-text preservation is required in M5, and direct parsed-DOM assertions are required in M5 before M6 adds real-browser execution evidence.
- The PoC and workflow files are currently untracked. Consequently, plain `git diff --check` is not evidence for those files; the current formatting evidence is Prettier plus explicit workflow link/trailing-whitespace checks. No Git action was authorized or performed.
- Closure remains `M4 COMPLETE — scoped isolated boundary`; it is not G2 GO. The residual items are recorded in `audit.md` and carried into M5.1–M5.7 and M6 in `tasks.md`.

## M1 validation (2026-08-10)

- Read this workflow after G1 and reconfirmed its isolated/no-consumer boundary.
- Recorded Node/npm versions, root lockfile authority, declared versus absent candidate packages, current consumers and final-output boundaries in `audit.md`.
- No package install, lockfile change, renderer change, source change, route change, browser run or deployment occurred.

## M2 initial validation (2026-08-10; superseded by quality correction)

- Added the isolated fixture module and confirmed by source path that it is outside all current renderer consumers.
- Fixture contents are deterministic and synthetic; no data, route, auth, renderer, lockfile or production-consumer behavior changed.

## M2 formal validation — COMPLETE (2026-08-10)

- **Node 24 environment:** `brew install node@24` installed `node@24 24.18.0` (bottle, arm64_tahoe) to `/opt/homebrew/Cellar/node@24/24.18.0`. Node `v24.18.0`, npm `11.16.0`. The prior "dangling/non-executable path" was corrected: the root cause was that `node@24` was not installed, not that the Homebrew path was corrupt.
- **TypeScript:** `env PATH="$(brew --prefix node@24)/bin:$PATH" npx tsc --noEmit` → PASS (exit 0).
- **Prettier:** `env PATH="..." npx prettier --check src/lib/markdown-poc/fixtures.ts` → PASS (after auto-fix removing a trailing comma in `markdownWarningCodes`).
- **Fixture id uniqueness:** 23 fixtures, all ids unique (programmatic check via `tsx`).
- **Requirement coverage:** All 22 security/semantic/special dimensions mapped to ≥1 fixture id.
- **Production isolation:** `rg "markdown-poc" src/ --glob '!src/lib/markdown-poc/**'` → no matches; fully isolated.
- **Workflow links:** All 7 local `.md` links in the Markdown workflow resolve to existing files.
- **Trailing whitespace:** `rg -n ' +$'` on fixtures.ts + workflow .md files → no matches.
- **`git diff --check`:** PASS.
- No dependency, lockfile, production consumer, route, auth, data, or deployment change was made.
- M2 is marked `[x]` in `tasks.md`; M3 was subsequently completed and M4 is now the only next entry.

## M3 validation — COMPLETE (2026-08-10; reverified 2026-08-15)

### 纠偏内容

| 文件                          | 变更                                                                                | 原因                               |
| ----------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------- |
| `ssr.test.tsx`                | 创建 PocRenderer 组件，调用 `renderToString`，对序列化 HTML 断言                    | 旧版导入 `renderToString` 但未调用 |
| `hydration.test.tsx`          | 创建 MarkdownDisplay 组件，执行 `renderToString` → `hydrateRoot` → `act` 更新并断言 | 旧版无 React 组件或 `hydrateRoot`  |
| `dom-safety.test.ts`          | 危险标签/协议检查 + 6 项非真空安全哨兵断言                                          | 旧版 47 项在空 stub 下真空通过     |
| `browser-candidate-review.md` | 改为 deferred；删除过期版本号和无来源断言                                           | M5/M6 前再核验浏览器 runner        |

### 真实 API 调用证据

- **SSR**: `renderToString(React.createElement(PocRenderer, ...))` 实际调用，输出含 `<div class="poc-renderer" data-outcome="local-fallback" data-toc-count="0" data-warning-count="1">`
- **Hydration**: `hydrateRoot(container, React.createElement(MarkdownDisplay, ...))` 实际调用，`hydrateRoot does not throw on valid React tree` 测试通过
- **Hydration 更新**: `act(() => root.render(...))` 实际执行更新流程

### 测试结果（Node 24）

| 文件                 | 测试数  | 红     | 绿      | 红灯原因                                                   |
| -------------------- | ------- | ------ | ------- | ---------------------------------------------------------- |
| `unit.test.ts`       | 143     | 45     | 98      | stub 返回 NOT_IMPLEMENTED → outcome/warning/content 不匹配 |
| `ssr.test.tsx`       | 61      | 7      | 54      | stub 空输出 → SSR HTML 不含 semantic 内容                  |
| `hydration.test.tsx` | 11      | 4      | 7       | stub 空输出 → hydrate 后不含 Safe heading                  |
| `dom-safety.test.ts` | 41      | 6      | 35      | stub 空输出 → 非真空哨兵（html.length>0, 含语义内容）      |
| **合计**             | **256** | **62** | **194** | **全部红灯指向 M4–M6 合同未实现**                          |

### 验收检查

| 检查          | 命令                                                  | 结果               |
| ------------- | ----------------------------------------------------- | ------------------ |
| TypeScript    | `npx tsc --noEmit`                                    | PASS               |
| Prettier      | `npx prettier --check src/lib/markdown-poc/`          | PASS               |
| 测试          | `npx vitest run src/lib/markdown-poc/__tests__/`      | 62 red / 194 green |
| 兼容测试      | `npx vitest run src/app/batch7-compatibility.test.ts` | 4 passed           |
| 生产隔离      | `rg "markdown-poc" --glob '!src/lib/markdown-poc/**'` | 0 matches          |
| 依赖/lockfile | 未修改                                                | PASS               |

### M3 时点结论与剩余风险（历史快照）

- M3 和父任务 FFQ-05 均为 COMPLETE；在该历史时点 M4 是唯一下一入口。M4 现已完成，当前入口为 M5。
- 62 个红灯是 M3 的预期失败证据，不是 M3 未完成；它们由当前 `NOT_IMPLEMENTED` stub 触发，并由 M4–M6 负责转绿。
- M3 只证明 SSR、React hydration 和 jsdom DOM/HTML 结构合同。真实浏览器中的 SVG、Canvas、事件、导航和脚本执行仍未验证，归属 M5/M6，并是 G2 的硬门。
- 当前 PoC 文件仍在工作树中，未提交、未推送，也未迁移任何生产消费者。

## M3 文档状态清理（2026-08-15；历史记录）

- 删除 M3 当前任务条目中的 252 项旧计数和重复句，统一采用纠偏后的 256 项证据。
- 将 252 项初始基线保留为明确标注的 superseded 历史记录，不再作为当前验收结论。
- 将 M3 纠偏交接 Prompt 标记为 `ARCHIVED — DO NOT EXECUTE`，防止后续代理重复执行。
- 当时同步子任务与父任务状态为 `M3 COMPLETE / FFQ-05 COMPLETE / FFQ-06-M4 NEXT`；当前状态已由本文件顶部的 M4 closure 取代。
- 仅修改工作流文档；未修改测试、PoC 实现、依赖、锁文件或生产消费者。

## FIX-02 Markdown fixture type validation (2026-08-16)

Conclusion: `PASS — strict test typecheck restored without reducing the fixture contract`.

- Reproduced baseline: `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npm run test:typecheck` reported 14 TS2339 errors in `unit.test.ts` and `ssr.test.tsx`, caused by `as const satisfies` preserving a union of individual fixture literal shapes where optional `contains`, `absent`, and `toc` are not common properties.
- Minimal type-model repair: `markdownFixtures` is now explicitly declared `readonly MarkdownFixture[]` while retaining the readonly fixture literal data. Consumers therefore see the declared `MarkdownFixtureExpectation` optional fields and retain the existing `?? []` and conditional assertion paths. No runtime renderer, production consumer, assertion, strict compiler setting, `any`, `@ts-ignore`, dependency, or lockfile changed.
- Focused validation: the same `npm run test:typecheck` command passes. `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npm test -- --run src/lib/markdown-poc/__tests__/unit.test.ts src/lib/markdown-poc/__tests__/ssr.test.tsx --reporter=dot` → `2 files / 206 passed`; this preserves both safety absence assertions and semantic/TOC assertions.
- Scope: this is an isolated test-fixture typing repair only. It does not change G2's isolated acceptance boundary, authorize M7 or a production Markdown migration, or execute F4. Current cross-workflow state synchronization and full-suite totals are FIX-03/FIX-05 work.

## FIX-04 Markdown formatting validation (2026-08-16)

- `fixtures.ts` and this repair's Markdown workflow documents pass scoped Prettier; target trailing-whitespace search and `git diff --check` have no output.
- No existing PoC renderer, Mermaid/Markmap/Chart adapter, test assertion, dependency, lockfile, or production consumer was reformatted or changed. The final full-suite and untracked-file audit remains FIX-05 work.
