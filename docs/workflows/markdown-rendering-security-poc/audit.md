# Current Renderer Audit

## Current M6 status (2026-08-16 documentation cleanup)

M6 is closed only as a historical limited isolated-PoC assessment: Math was `ENABLED_ISOLATED`; Mermaid, Markmap, and Chart were then `DEFERRED_INERT`; M7 was not authorized. The separate special-adapter workflow subsequently supplied its own current `ENABLED_ISOLATED` evidence for all three and G2 is now `PASS` only in that isolated scope. The reproducible historical M6 browser command is `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line`; the older `--project=chromium` command is invalid because the checked-in config has no named project. The dated sections below are historical execution records, not current next-step instructions.

## M6.1 browser-runner and evidence-contract decision (2026-08-15, read-only)

### Historical M6.1 local state

- Formal runtime: `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" node --version` -> `v24.18.0`; npm -> `11.16.0`. This satisfies the project `package.json` contract (`node: 24.x`, `npm: >=11 <12`).
- At the M6.1 snapshot, the root dependency graph resolved `vitest@3.2.7` only. `@playwright/test`, `playwright`, `playwright-core`, `puppeteer`, and `@vitest/browser` were absent from both `node_modules` resolution and `package-lock.json` package records. `next@16.2.12` mentioned `@playwright/test@^1.51.1` only as an optional peer; Vitest 3.2.7 similarly mentioned `@vitest/browser@3.2.7` only as an optional peer. M6.2 subsequently added the approved test-only Playwright runner.
- Shared macOS cache inventory exists outside the repository at `~/Library/Caches/ms-playwright/`: Chromium revisions `1228` and `1234`, corresponding headless-shell revisions, and `ffmpeg-1011` (about 1.09 GiB total). No repository-resolved Playwright package exists with which to establish those cache revisions' compatibility. This cache is not evidence that the project can run a browser test and was not changed, downloaded, or removed.
- No `playwright`/`puppeteer` config exists. The current `vitest.config.ts` explicitly runs jsdom and does not enable browser mode.

### Fresh candidate metadata and advisories

All package metadata below was read from the official npm registry on 2026-08-15 using the formal Node 24 path; no `npm install`, `npx` package acquisition, lockfile write, or browser command was used.

| Candidate                                                | Current registry version / license                           | Runtime and peer result                                                                                                                                                                       | Advisory result                                                                                                                                                                                                                                         | Mutation / artifact consequence                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@playwright/test` / `playwright`                        | `1.62.1`, Apache-2.0                                         | `node >=20`; compatible with Node 24.18.0; no peer returned by registry query.                                                                                                                | `npm audit --package-lock-only --omit=dev --json` has no Playwright entry because it is not locked. GitHub Advisory Database package query could not be completed anonymously because the API rate limit was exhausted; no advisory-free claim is made. | Requires a direct dev dependency and `package-lock.json` update. Official Playwright docs require a matching browser installation; current cache compatibility cannot be inferred. Trace/video/screenshot artifacts must remain under the allowed PoC workflow `assets/` path if later enabled. |
| `puppeteer`                                              | `25.7.0`, Apache-2.0                                         | `node >=22.12.0`; compatible with Node 24.18.0; no peer returned by registry query.                                                                                                           | Same current-lock audit result and GitHub anonymous-query limitation; no advisory-free claim.                                                                                                                                                           | Requires a direct dev dependency and lockfile update. Official docs state its default behaviour downloads a specific Chrome; use of a different executable is an explicit configuration choice, so this route does not avoid a browser compatibility decision.                                  |
| Vitest Browser (`vitest` + `@vitest/browser-playwright`) | registry `vitest@4.1.10`, MIT; `@vitest/browser@4.1.10`, MIT | The project has `vitest@3.2.7`; current browser package requires matching Vitest `4.1.10`. Current Vitest supports Node 24, but selecting this candidate entails a coordinated major upgrade. | Same current-lock audit result and GitHub anonymous-query limitation; no advisory-free claim.                                                                                                                                                           | Requires replacing/upgrading the existing test runner, adding a browser provider, lockfile change, and browser configuration; rejected as larger than the minimum controlled M6 change.                                                                                                         |

Primary-source facts used for the decision: Playwright documents that each version requires specific browser binaries and instructs use of its install CLI; it stores macOS binaries in `~/Library/Caches/ms-playwright`. Puppeteer documents its default Chrome download and explicit executable-path alternative. Vitest Browser documents that a provider is required, recommends Playwright for local/CI browser tests, and installs `@vitest/browser-playwright` with Vitest.

### Selected minimum and frozen M6 evidence contract

`@playwright/test@1.62.1` is selected **only as the pending minimum runner**, not installed or enabled. It avoids replacing the current Vitest suite and exposes the direct browser-page event surface needed to actively assert script sentinel, `pageerror`, console error, dialog, request, navigation, download, and `click`/`error`/`load` observations. The minimum future browser matrix is one matching headless Chromium project; Firefox/WebKit are deferred because the M6 contract requires real-browser evidence, not cross-browser conformance, and no package/browser mutation is yet approved.

At the historical decision point, the prospective command was recorded as `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/ --project=chromium --reporter=line`. It is now known to be invalid: it neither selects the nested config nor has a defined `chromium` project. The current reproducible command is recorded in the status note above. Browser traces, screenshots, videos, and reports remain opt-in failure artifacts under `docs/workflows/markdown-rendering-security-poc/assets/m6/`; none are present in the current workspace.

### M6.1 conclusion and required approval

**Historical M6.1 decision — superseded as a current status statement.** At the M6.1 decision point, the selected route required separate approval for: (1) adding direct `@playwright/test@1.62.1` (or a separately re-reviewed exact version) to `devDependencies`, (2) a `package-lock.json` update, and (3) installation of the matching persistent Chromium binary. That approval was subsequently received and is recorded in the M6.2 closure below. At that historical point M6.3 Math was next; no production consumer was authorized.

## M6.2 browser harness and inert baseline closure (2026-08-15)

- Separate approval was received for the recorded runner, lockfile, and matching Chromium installation. `@playwright/test@1.62.1` is now an exact root dev dependency; `npx playwright --version` reports `1.62.1`, and `npx playwright install --list` assigns this repository to cached `chromium-1234`, its headless shell, and `ffmpeg-1011`.

## M6.3 Math isolated decision (2026-08-15)

- **Decision: `ENABLED_ISOLATED`.** `src/lib/markdown-poc/math.ts` is a PoC-owned KaTeX final-output boundary, not a production-renderer fallback. It requests display HTML only with `trust: false`, strict errors, and `throwOnError`; its own fail-closed tag-stream parser permits only `span`, an exact required class set, `class`/`style`/`aria-hidden`, and numeric `height`/`margin-right`/`top` `em` style declarations. The outer marker is `data-poc-math="katex"`.
- Every unexpected renderer tag, nesting shape, class, attribute, style value, trust command, malformed source, or URL reduces only that block to exact escaped `code[data-poc-inert="math"]` plus `LOCAL_FALLBACK`. The previous four special adapters are not inferred from this decision: Mermaid, Markmap, and Chart remain `DEFERRED_INERT`.
- First relevant failures were the old structural decision (`DEFERRED_INERT` instead of `ENABLED_ISOLATED`) and the old browser SSR output (a `$$…$$` block after a heading became a plain paragraph). The first implementation correction widened the explicitly permitted single style declaration grammar to the actual safe two-declaration KaTeX output; a Playwright trace then showed Vite's first KaTeX dependency optimization caused a one-time full reload, and the hostile fixture was corrected from two literal backslashes to the intended KaTeX command. No production source, sanitizer, renderer, or consumer was imported or changed.
- The test-only browser surface lives entirely in `src/lib/markdown-poc/browser-harness/`; its dedicated Playwright configuration and Chromium tests live under `src/lib/markdown-poc/browser-tests/`. The Vite server and all Playwright result paths are confined to the PoC test surface and `docs/workflows/markdown-rendering-security-poc/assets/m6/`; no route, consumer, production renderer, or special-renderer component is imported.
- Code has an explicit final browser schema: hostile inline and fenced source produces only ordinary `code` elements with zero attributes, under `p` and `pre` respectively. It is real-SSR-rendered, hydrated, updated, and subjected to `click`/`error` dispatch on the code element plus `load` dispatch on `window`; no sentinel mutation, page error, console error, dialog, download, post-hydration navigation, or non-local request is observed.
- Math, Mermaid, Markmap, and Chart each remain `DEFERRED_INERT`: their exact decoded source and structured warning are observable after a real SSR→hydration→update cycle. Mermaid, Markmap, and Chart retain a safe heading and TOC across update; no final SVG/Canvas renderer, link, or special adapter is enabled. This closes browser baseline evidence only; it does not decide Math enablement, so M6.3 is the sole next item.

| Area                | Current source fact                                                                    | Planning consequence                                                       |
| ------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Structural renderer | src/lib/markdown-renderer.ts loads marked and produces HTML.                           | A PoC must be isolated; it cannot claim to replace production rendering.   |
| React mapping       | src/hooks/use-markdown-render.tsx loads html-react-parser and maps placeholder blocks. | Structural sanitization and component mapping must be separately tested.   |
| Math output         | src/components/markdown-math.tsx inserts generated HTML.                               | KaTeX requires a final-output boundary and local fallback evidence.        |
| Dynamic blocks      | Mermaid, Markmap, and Chart are client-side downstream renderers.                      | Each SVG or DOM output requires independent constraints before enablement. |
| Target packages     | unified, remark, and rehype packages are absent from package.json.                     | Dependency selection and lockfile impact are a stop-and-approve decision.  |

This table is the historical M1 static baseline. Later M2–M4 records supersede its test-state limitation; real-browser execution remains unperformed and now belongs to M6 and G2.

## M1 execution record (2026-08-10)

- Runtime and package manager: Node `v26.0.0`, npm `11.12.1`.
- Root dependency authority is `package.json` plus root `package-lock.json` (lockfile v3); no root pnpm/yarn lockfile exists. The nested `.kilo/package-lock.json` is not a project dependency authority and will not be changed.
- Current declared/locked renderer stack includes `marked` (`^17.0.0`, locked `17.0.6`), `html-react-parser`, KaTeX, Mermaid, Markmap and ECharts/react-ECharts dependencies. `unified`, `remark-parse`, `remark-rehype`, `rehype-sanitize` and `rehype-react` are not declared.
- Current consumers are `BlogPreview`, `RichText`, note detail, note preview and about content through `useMarkdownRender`; no production consumer is moved by this PoC.
- Final-output boundaries needing individual proof: KaTeX produces HTML inserted via `dangerouslySetInnerHTML`; Mermaid returns SVG after client rendering; Markmap mutates an SVG; Chart parses input and creates a client chart. Source-only review does not prove any final DOM/SVG safe.
- Candidate PoC packages are `unified`, `remark-parse`, `remark-rehype` and `rehype-sanitize`; exact versions, licenses, advisories, peers and bundle impact are `UNKNOWN` until a later no-install dependency review. M1 does not authorize installation or lockfile modification.

## M2 fixture quality correction and formal validation (2026-08-10)

### Fixture module

`src/lib/markdown-poc/fixtures.ts` is an isolated, non-production fixture module with 23 deterministic synthetic fixtures. Each fixture has a stable `id`, explicit `public` or `admin-preview` mode, expected outcome, structured warning codes, and required semantic/TOC or final-output assertions. The public and admin-preview sets share the same security baseline; neither treats administrator or AI Markdown as trusted.

| Requirement coverage                                | Fixture ids                                                               |
| --------------------------------------------------- | ------------------------------------------------------------------------- |
| raw HTML, scripts, event handlers                   | `security-raw-html-event-attribute`, `security-script-and-raw-html`       |
| iframe / srcdoc                                     | `security-iframe-srcdoc`                                                  |
| unsafe SVG href, xlink, foreignObject               | `security-svg-href-xlink-foreign-object`                                  |
| link/image unsafe protocols                         | `security-link-dangerous-protocols`, `security-image-dangerous-protocols` |
| entity, case, whitespace/control URL confusion      | `security-url-entity-case-whitespace-control`                             |
| safe-to-malicious client update                     | `security-client-update-safe-to-malicious`                                |
| malformed input and local fallback                  | `security-malformed-local-fallback`                                       |
| headings/TOC, paragraphs, list, table               | `semantic-headings-stable-toc`, `semantic-paragraph-list-table`           |
| safe link, relative, anchor, mail                   | `semantic-safe-links-relative-anchor-mail`                                |
| safe image, inline code, fenced code                | `semantic-safe-image-inline-and-fenced-code`                              |
| normal code and hostile text that must remain inert | `special-code-valid`, `special-code-hostile-text-is-inert`                |
| math valid and failed                               | `special-math-valid`, `special-math-malformed`                            |
| Mermaid valid and hostile                           | `special-mermaid-valid`, `special-mermaid-malicious`                      |
| Markmap valid and hostile                           | `special-markmap-valid`, `special-markmap-malicious`                      |
| Chart valid and hostile/invalid                     | `special-chart-valid`, `special-chart-malicious-or-invalid`               |

`finalOutput: 'inert-until-validated'` freezes the M3/M4 rule for Math, Mermaid, Markmap and Chart: until a renderer's ultimate HTML, DOM, or SVG output is independently validated, it must remain inert rather than be enabled. Code blocks have `must-validate` because hostile text must be escaped in their final output. The future common output contract is renderable content, stable TOC, structured warnings, and local fallback.

### M2 formal validation — COMPLETE (2026-08-10)

**Node 24 environment:** Homebrew `node@24` was not installed; `brew install node@24` installed `node@24 24.18.0` (bottle, arm64_tahoe) to `/opt/homebrew/Cellar/node@24/24.18.0`. The prior dangling/non-executable path has been corrected: the root cause was that `node@24` was not installed, not that the Homebrew path was corrupt. Node 24 is now keg-only; all project commands use explicit `env PATH="$(brew --prefix node@24)/bin:$PATH"`.

| Check                   | Command                                                                | Result                       |
| ----------------------- | ---------------------------------------------------------------------- | ---------------------------- |
| Node version            | `env PATH="/opt/homebrew/opt/node@24/bin:$PATH" node --version`        | `v24.18.0`                   |
| npm version             | `env PATH="..." npm --version`                                         | `11.16.0`                    |
| TypeScript              | `env PATH="..." npx tsc --noEmit`                                      | PASS (exit 0)                |
| Prettier format         | `env PATH="..." npx prettier --check src/lib/markdown-poc/fixtures.ts` | PASS (exit 0 after auto-fix) |
| Fixture id uniqueness   | 23 fixtures, all ids unique via `tsx` scripted check                   | PASS                         |
| Requirement coverage    | All 22 security/semantic/special dimensions mapped to ≥1 fixture id    | PASS                         |
| Production isolation    | `rg "markdown-poc" src/ --glob '!src/lib/markdown-poc/**'`             | No matches; fully isolated   |
| Workflow Markdown links | All 7 local `.md` links resolve to existing files                      | PASS                         |
| Trailing whitespace     | `rg -n ' +$'` on fixtures.ts + workflow .md files                      | No trailing whitespace       |
| `git diff --check`      | Whitespace-error check on tracked changes                              | PASS                         |

- No dependency, lockfile, production consumer, route, auth, data, or deployment change was made.
- The Prettier auto-fix only removed a trailing comma in the `markdownWarningCodes` array literal; no semantic change.

## M3 execution record (2026-08-10; COMPLETE)

### Contract types and stub renderer

- `src/lib/markdown-poc/types.ts` defines the future output contract: `PoCRenderResult` (html, toc, warnings, outcome), `PoCWarning`, `PoCWarningCode`, `PoCOutcome`, `TocItem`.
- `src/lib/markdown-poc/render-poc.ts` is a minimal stub that returns empty output with a `NOT_IMPLEMENTED` warning. It is a deliberate placeholder; M4 will replace it with a real bounded parser + sanitizer.
- `src/lib/markdown-poc/index.ts` is the public barrel.

### Final test architecture

- **Unit tests** (143 tests): consume all 23 fixtures; assert outcome, warning codes, dangerous-element blocking, semantic preservation, TOC stability, special-renderer inertness, client-update safety, and malformed local fallback.
- **SSR tests** (61 tests): call `renderToString` on a test-only React surface; assert deterministic serialized output, contract metadata, structural safety, semantic content, and inert special-renderer boundaries.
- **Hydration tests** (11 tests): call `hydrateRoot`, perform a safe-to-malicious React update with `act`, and assert update safety, local failure containment, repeat stability, and special-renderer leak prevention.
- **DOM-safety tests** (41 tests): validate HTML/DOM structure in jsdom and include six non-vacuum semantic sentinels so an empty stub cannot pass vacuously.
- **Current total**: 256 tests (62 red / 194 green). All red tests are expected M3 red lights caused by the unimplemented M4–M6 contract.

### Assertion and environment semantics

- `absent` assertions distinguish dangerous DOM/attributes (must not exist) from escaped source text (allowed in code blocks).
- jsdom does not execute scripts, render SVG/Canvas, or prove navigation and real event behavior. M3 therefore claims only structural DOM/HTML evidence.
- `finalOutput: 'inert-until-validated'` fixtures assert that Math/Mermaid/Markmap/Chart remain inert.
- `finalOutput: 'must-validate'` fixtures (code blocks) assert that hostile text is escaped but visible.

### Browser runner decision

- No browser runner was installed in M3.
- Runner selection is deferred to M6 and must use fresh official package metadata before any dependency or lockfile change.
- Real-browser SVG, Canvas, event, navigation, and script-execution evidence is mandatory before G2 can return GO.
- The deferred decision is recorded in `src/lib/markdown-poc/__tests__/browser-candidate-review.md`.

### Production isolation

- `rg "markdown-poc" src/ --glob '!src/lib/markdown-poc/**'` → no matches; fully isolated.
- No production consumer, route, auth, dependency, or lockfile change.

### Superseded baseline and correction

The initial 252-test draft did not exercise real SSR or React hydration and used a misleading browser-test name. It is superseded and is not current acceptance evidence.

SSR/hydration/browser test correction applied:

- `ssr.test.tsx`: real `renderToString` with React surface; 61 tests (7 red from stub)
- `hydration.test.tsx`: real `hydrateRoot` + `act` updates; 11 tests (4 red from stub)
- `dom-safety.test.ts`: renamed from browser.test.ts; 6 non-vacuum sentinel assertions; 41 tests (6 red from stub)
- `browser-candidate-review.md`: deferred decision, no expired version claims
- Total: 256 tests (62 red / 194 green); all reds point to M4–M6 contracts not yet implemented
- Real browser execution (SVG/Canvas/events/navigation) deferred to M6; G2 is hard gate

## M4 implementation and documentation closure (2026-08-15)

- The isolated renderer now uses `marked.lexer()` as an input-only tokenizer and emits only project-owned, escaped/allow-listed HTML for the bounded ordinary subset.
- Independent recheck: Node `v24.18.0`; focused PoC tests 256/256; TypeScript PASS; Prettier PASS; Batch 7 compatibility 4/4; production references outside `src/lib/markdown-poc/` are zero.
- No production consumer, route, auth, API, persistence, dependency, lockfile, deployment, Git staging, commit, push, or release boundary changed.
- No demonstrated M4 XSS bypass was found. M4 is complete only within its isolated ordinary-content boundary; it is not G2 GO.

### Residual risks converted to M5.1–M5.7 and M6 requirements

| Risk                                                                                                                                                                                                  | Current evidence                                                                                                           | Required next action                                                                                                                               | Owner             |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| Code/inert text is made non-attribute-shaped by inserting zero-width characters into strings such as `onerror=` and `javascript:`. This is structurally safe but does not preserve exact source text. | Direct output inspection of `render-poc.ts`; current tests prove inert structure but do not require decoded text equality. | Establish exact decoded-text and parsed-node proof in M5.1, then close ordinary code in M5.2 and each special fallback in M5.3–M5.6.               | M5.1–M5.6         |
| Most DOM-safety checks are string/serialization assertions rather than direct parsed-DOM element and attribute assertions.                                                                            | Test-source review; hydration does parse HTML but returns `innerHTML` for the final assertions.                            | Add the shared direct-DOM harness in M5.1, apply it to every adapter decision in M5.2–M5.6, and reserve real-browser behavior for M6.              | M5.1–M5.6 / M6    |
| The PoC and workflow are currently untracked, so plain `git diff --check` does not inspect them.                                                                                                      | `git ls-files` returns no tracked PoC/workflow paths.                                                                      | Keep Prettier, link, and whitespace checks as current evidence; do not claim versioned acceptance until a separately authorized Git action occurs. | Handoff/Git scope |

Closure decision: `M4 COMPLETE — scoped isolated boundary`. Remaining structural uncertainty is owned by M5.1–M5.7 and browser-execution uncertainty by M6/G2. M5.1 is now complete; M5.2 is the only next implementation entry.

## M5.1 shared parsed-DOM and exact-text baseline (2026-08-15) — COMPLETE

- The new isolated `final-output-contract.test.ts` uses jsdom's parsed nodes rather than serialized-string regular expressions to inspect elements, event-like attributes, URL-bearing attributes, exact `textContent`, warning codes, and outcome metadata for Math, Mermaid, Markmap, and Chart inert output.
- Failing-first evidence: the first direct test run produced 2 failures of 8. Malicious Mermaid source text had `on\u200berror=` and malicious Markmap source text had `javascript\u200b:` after parsing. This was an output-fidelity defect, not a live-DOM safety finding.
- Minimal correction: special inert blocks and malformed Math fallback now use structural HTML escaping without zero-width source rewriting. The direct suite is 8/8 green; no special adapter is enabled by this evidence.
- A subsequent Code red run found five legacy serialized-string checks that falsely classified the now-exact inert text as active attributes/URLs. They were replaced by one parsed-DOM helper and the M5.1 plus existing M3 checks re-passed; no contract was weakened.
- M5.2 retains ownership of ordinary fenced and inline Code exact-text closure. M6/G2 retains real-browser SVG/Canvas/event/navigation/script evidence.

## M5.3 Math decision (2026-08-15) — DEFERRED_INERT

- Direct parsed-DOM review of synthetic KaTeX final HTML found no URL or event attributes, but did find renderer-controlled inline styles. In the absence of a PoC-owned style-value allow-list/sanitizer, this does not satisfy the final-output enablement contract.
- The Math syntax remains exact escaped inert text with its existing warning/outcome contract. M6/G2 browser validation is still unstarted.

## M5 closure matrix (2026-08-15) — COMPLETE, NOT G2 GO

| Path            | Decision                    | Final-output evidence                                                                                | Residual risk / owner                                                        |
| --------------- | --------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Shared baseline | CLOSED                      | parsed nodes, attributes, URL-bearing values, warning/outcome metadata, exact decoded text           | browser execution is M6/G2                                                   |
| Code            | ENABLED (isolated PoC only) | unit, `renderToString`, `hydrateRoot`, and parsed DOM preserve hostile inline/fenced text exactly    | no production consumer is enabled; browser execution is M6/G2                |
| Math            | DEFERRED_INERT              | KaTeX final HTML direct inspection has no URL/event attributes but renderer-controlled inline styles | PoC-owned style sanitizer and M6/G2 evidence required before reconsideration |
| Mermaid         | DEFERRED_INERT              | exact parsed inert fallback and warning; no final SVG emitted by PoC                                 | final SVG sanitizer plus M6 browser evidence required                        |
| Markmap         | DEFERRED_INERT              | exact parsed inert fallback and warning; no transformed DOM/SVG emitted by PoC                       | structural sanitizer plus M6 browser evidence required                       |
| Chart           | DEFERRED_INERT              | exact parsed inert fallback and warning; no Canvas/container adapter emitted by PoC                  | allow-listed configuration/container and M6 browser evidence required        |

Final validation is 6 test files / 272 tests, TypeScript, Prettier, Batch 7 compatibility 4/4, zero production references outside `src/lib/markdown-poc/`, resolved local workflow links, and no trailing whitespace. The known jsdom `act(...)` environment messages are non-target warnings only. M6 is the sole next entry; G2 is not GO.
