# Requirements

- Accept Markdown plus explicit public or admin-preview mode.
- Return renderable content, table of contents, and safe structured warnings.
- Preserve the exact decoded source text of ordinary code and inert special-renderer fallbacks; safety checks must prove that text remains non-executable without inserting invisible characters or otherwise changing user content.
- Test malicious scripts, event handlers, unsafe and obfuscated URLs, raw HTML, unsafe SVG, client updates, and local failure fallback.
- For M5 final-output validation, assert parsed DOM elements, attributes, URL-bearing attributes, and `textContent` directly rather than relying only on serialized-HTML regular expressions. Apply this shared baseline first in M5.1, then close Code, Math, Mermaid, Markmap, and Chart separately in M5.2–M5.6.
- Test SSR, hydration, browser execution, semantic golden content, and final outputs of each enabled special renderer.
- **Browser execution 总要求保留，但其执行阶段统一为 M6、验收阶段为 G2。** M5 只负责隔离最终输出的结构合同、精确文本保真以及逐适配器启用/延后决定；M3/M5 均不把 jsdom 证据冒充真实浏览器执行验证。
- Record dependency license, advisory, peer, lockfile, and bundle impact before a production-integration decision.
- Keep stored Markdown, DTOs, auth, APIs, routes, and deployment unchanged.

## M6 controlled-expansion requirements (executed; evidence limitations retained)

- **M6-REQ-01 Runner decision before mutation.** Re-query current official browser-runner metadata and record version, license, advisories, peer/runtime requirements, lockfile impact, browser-binary/cache impact, and the minimum supported browser matrix before any install or lockfile change.
- **M6-REQ-02 Separate dependency approval.** Approval of M6.1–M6.8 does not authorize installing, upgrading, or removing a package, changing `package-lock.json`, or downloading a persistent browser binary. Stop after M6.1 and request explicit approval if any such mutation is required.
- **M6-REQ-03 Real-browser baseline first.** Before enabling a special adapter, prove in a real browser that ordinary Code and the current exact-text Math/Mermaid/Markmap/Chart inert fallbacks do not execute scripts, dispatch effective inline handlers, navigate to dangerous URLs, open dialogs, start downloads, or issue unexpected network requests.
- **M6-REQ-04 Test-first, one adapter at a time.** Evaluate Math, Mermaid, Markmap, and Chart strictly in that order. Add a failing browser/structural test for the current adapter, make the smallest isolated implementation, validate it, update `tasks.md` and `validation.md`, and only then begin the next adapter.
- **M6-REQ-05 Independent adapter outcomes.** Each adapter must finish as `ENABLED_ISOLATED` or `DEFERRED_INERT`. A deferral must preserve exact decoded fallback text and structured warnings; it does not block evaluation of later adapters and is not a G2 GO result for that adapter.
- **M6-REQ-06 Math boundary.** Enabled Math must use a PoC-owned allow-list for KaTeX final elements, classes, attributes, and style values. KaTeX trust commands, unsafe URLs, event attributes, unexpected MathML/HTML, and sanitizer failure must be rejected or locally reduced without using the production `dangerouslySetInnerHTML` path.
- **M6-REQ-07 Mermaid boundary.** Enabled Mermaid must sanitize its final SVG through a PoC-owned allow-list covering elements, attributes, namespaces, URL-bearing attributes, style values, `foreignObject`, links, events, and generated ids. Sanitizer or render failure must degrade locally.
- **M6-REQ-08 Markmap boundary.** Enabled Markmap must reuse only an already validated SVG baseline and independently constrain transformed links, DOM mutations, pan/zoom events, downloads, and navigation. It must not inherit Mermaid approval automatically.
- **M6-REQ-09 Chart boundary.** Enabled Chart must accept only parsed JSON data plus an explicit configuration allow-list. Function-valued formatters, arbitrary code, dynamic imports, unsafe HTML labels/tooltips, unexpected network access, and unapproved downloads must be impossible or locally rejected before Canvas/container creation.
- **M6-REQ-10 Active browser observations.** Browser tests must capture page errors, console errors, dialogs, navigation, downloads, requests, script sentinels, relevant event dispatch, DOM/SVG structure, and Canvas/container creation. Screenshots alone are not security evidence.
- **M6-REQ-11 SSR/hydration/update coverage.** Test initial SSR, hydration, and safe-to-malicious client updates for every enabled path, with no unexplained hydration mismatch or cross-render residue.
- **M6-REQ-12 Local and global fallback.** A failing block must preserve safe neighbouring blocks, TOC, warnings, and outcome metadata. A global failure must use a PoC-owned inert/safe error surface and must never import or invoke `src/lib/markdown-renderer.ts`, `use-markdown-render.tsx`, or another legacy production renderer.
- **M6-REQ-13 Exact Code structure debt.** Close the M5 evidence debt by freezing ordinary inline/fenced Code to the approved parsed element/attribute schema and proving that no extra URL-bearing or active element is introduced in SSR, hydration, or the browser surface.
- **M6-REQ-14 Isolation and data boundaries.** Use only deterministic synthetic fixtures. Keep production consumers, stored Markdown, routes, auth, APIs, DTOs, database, persistence, public content, Git publication, and deployment unchanged.
- **M6-REQ-15 G2 evidence, not migration authority.** M6 must produce a per-path browser evidence matrix with exact commands, browser/runtime versions, pass/fail counts, warnings, artifacts, adapter decisions, and residual risks. Even a complete M6 does not authorize a production route migration; M7 and a separately approved route decision remain required.

### 2026-08-16 evidence reconciliation

- The reproducible local browser command is `npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line`. The historical form using `--project=chromium` is invalid because the configuration defines no named project.
- The current workspace contains no retained M6 failure trace or report artifact. Artifact-backed claims are therefore removed from current acceptance evidence rather than reconstructed.
- Code and Math cover the full active-observation set. Deferred Mermaid, Markmap, and Chart paths currently prove inert DOM/text and the script sentinel only; they do not independently capture all page-error, console, dialog, request, navigation, download, and event-dispatch observations. This is a residual G2 limitation, not a reason to enable those adapters.
