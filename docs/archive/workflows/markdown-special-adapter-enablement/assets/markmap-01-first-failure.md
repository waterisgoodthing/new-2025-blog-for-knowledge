# Markmap-01 first failing evidence

Commands:

```sh
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx vitest run src/lib/markdown-poc/__tests__/markmap-isolated.test.ts --reporter=verbose
env PATH="/opt/homebrew/opt/node@24/bin:$PATH" npx playwright test src/lib/markdown-poc/browser-tests/markmap-isolated.spec.ts --config=src/lib/markdown-poc/browser-tests/playwright.config.ts
```

The structural test failed twice: safe `# Root / ## Child` had no `svg[data-poc-markmap="rendered"]`, and hostile link-like source remained outcome `inert` rather than exact `local-fallback`.

The browser SSR failure showed the current inert surface:

```html
<div data-outcome="inert" data-poc-phase="ssr" data-warning-count="1">
	<div class="poc-content">
		<h1 id="safe-markmap">Safe Markmap</h1>
		<pre><code data-poc-inert="markmap"># Root
## Child</code></pre>
	</div>
</div>
```

The first browser failure bundle is retained at `playwright-test-results/markmap-isolated-Markmap-0-c17a3-wnload-or-lifecycle-residue/` with screenshot, error context, and trace. No renderer, DOM/SVG transformation, link, navigation, download, or production consumer was invoked by this failing run.
