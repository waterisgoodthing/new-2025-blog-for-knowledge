# Markdown Rendering Security PoC

Status: M1–M6.9 are historical isolated-PoC evidence; the separate special-adapter workflow has G2 `PASS` in its isolated scope; FIX-02～05 are complete, F4 input is ready for separate approval, M7 and production migration remain unauthorized.

Goal: prove an isolated, project-owned Markdown rendering security boundary before any production consumer changes. Public, administrator-authored, and AI-generated Markdown are all untrusted.

Current production source uses marked, HTML strings, html-react-parser, dynamic special renderers, and KaTeX HTML insertion. The isolated M4 PoC uses the already installed `marked` lexer only as an input tokenizer and owns all emitted escaped/allow-listed HTML. M6 later added the test-only Playwright dev dependency under separate approval; neither phase changes stored content, routes, auth, APIs, database schema, or production consumers.

M5 closure evidence is 6 focused test files / 272 tests, TypeScript, Prettier, Batch 7 compatibility (4/4), zero production references outside the isolated module, resolved workflow links, and no trailing whitespace. Code is enabled only in the isolated PoC; Math, Mermaid, Markmap, and Chart are deferred as exact inert fallbacks. This is a scoped M5 completion, not G2 GO. Real-browser navigation, event, script, SVG, and Canvas evidence remains M6/G2 work. The PoC and workflow currently remain untracked workspace files, so `git diff --check` is not treated as evidence for those files; Prettier and explicit content checks provide the current formatting evidence.

M6 used a controlled expansion: runner/evidence freeze, inert browser baseline, then Math, Mermaid, Markmap, Chart, fallback closure, and a matrix. Code is structurally frozen; Math is `ENABLED_ISOLATED` only in the PoC, while Mermaid/Markmap/Chart remain exact inert fallbacks. The reproducible browser invocation is `npx playwright test --config=src/lib/markdown-poc/browser-tests/playwright.config.ts --reporter=line`; the historical `--project=chromium` command is invalid because this config has no named project. The current workspace does not contain the historical failure traces previously claimed by the matrix, and deferred-adapter tests do not capture the full Code/Math event/network observation set. These are explicit M6 evidence limitations, so G2 remains PARTIAL / NOT GO. No M6 item may change a production consumer.

The separate [Markdown special-adapter enablement workflow](../markdown-special-adapter-enablement/README.md) subsequently closed Mermaid, Markmap, and Chart as `ENABLED_ISOLATED`, so G2 is current `PASS` only for the isolated scope. This workflow preserves M1–M6.9 as historical evidence, does not repurpose M7, and does not authorize a production consumer.

Documents: [audit](./audit.md), [design](./design.md), [requirements](./requirements.md), [tasks](./tasks.md), [validation](./validation.md), [current M6 Goal prompt and archived handoffs](./handoff-prompt.md).
