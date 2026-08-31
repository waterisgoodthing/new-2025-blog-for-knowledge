# Mermaid-02 first browser failure

Command:

```sh
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/mermaid-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts
```

First adapter-related failure: the safe `flowchart LR` source reached hydration, but the final DOM was the exact local Mermaid fallback rather than one `svg[data-poc-mermaid="rendered"]`.

Observed final content:

```html
<h1 id="safe-mermaid">Safe Mermaid</h1>
<pre><code data-poc-inert="mermaid">flowchart LR
A[Start] --&gt; B[End]</code></pre>
```

The retained Playwright failure bundle is under `playwright-test-results/mermaid-isolated-Mermaid-0-0b120-ls-back-for-hostile-updates/` and contains the screenshot, error context, and trace. Raw Mermaid 11.16.1 output included `foreignObject`, HTML `div`/`span`/`p`, `style`, filter elements, and data attributes. The PoC did not add any of those to its final schema; it changed to a PoC-owned static flowchart SVG generator for the already restricted grammar.
