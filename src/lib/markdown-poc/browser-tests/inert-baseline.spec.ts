import { expect, test } from '@playwright/test'
import React from 'react'
import { renderToString } from 'react-dom/server'

import { PoCBrowserSurface } from '../browser-harness/surface'
import { renderMarkdownPoC } from '../render-poc'

const harnessUrl = 'http://127.0.0.1:4179/src/lib/markdown-poc/browser-harness/index.html'
const browserClientModule = '/src/lib/markdown-poc/browser-harness/client.ts'

test('M6.2 browser surface mounts an isolated PoC root', async ({ page }) => {
	await page.goto(harnessUrl)

	await expect(page.locator('[data-poc-browser-root]')).toHaveCount(1)
})

test('M6.2 Code remains exact, inert, and observable through SSR, hydration, and update', async ({ page }) => {
	const observations = {
		consoleErrors: [] as string[],
		dialogs: [] as string[],
		downloads: [] as string[],
		navigations: [] as string[],
		pageErrors: [] as string[],
		requests: [] as string[]
	}
	page.on('console', message => {
		if (message.type() === 'error') observations.consoleErrors.push(message.text())
	})
	page.on('dialog', dialog => {
		observations.dialogs.push(dialog.message())
		void dialog.dismiss()
	})
	page.on('download', download => observations.downloads.push(download.suggestedFilename()))
	page.on('framenavigated', frame => {
		if (frame === page.mainFrame()) observations.navigations.push(frame.url())
	})
	page.on('pageerror', error => observations.pageErrors.push(error.message))
	page.on('request', request => observations.requests.push(request.url()))
	await page.addInitScript(() => {
		window.__markdownPocXss = false
		window.__markdownPocObservedEvents = []
		for (const type of ['click', 'error', 'load']) {
			window.addEventListener(type, () => window.__markdownPocObservedEvents.push(type), true)
		}
	})

	const safeMarkdown = '# Safe Code\n\n```js\nconsole.log("safe")\n```'
	const hostileCode = '<img src="javascript:alert(1)" onerror="window.__markdownPocXss = true">'
	const hostileMarkdown = `# Safe Code\n\nInline \`${hostileCode}\`.\n\n\`\`\`html\n${hostileCode}\n\`\`\``
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'admin-preview' }))

	expect(serverHtml).toContain('data-poc-phase="ssr"')
	expect(serverHtml).toContain('Safe Code')
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown: safeMarkdown, mode: 'admin-preview' as const }, moduleUrl: browserClientModule }
	)

	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	await page.evaluate(() => {
		window.__markdownPocObservedEvents.length = 0
	})
	observations.navigations.length = 0
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: hostileMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('[data-outcome="allow"]')).toHaveCount(1)
	await expect(page.locator('.poc-content script, .poc-content iframe, .poc-content svg')).toHaveCount(0)

	const codeSchema = await page.locator('.poc-content').evaluate(content =>
		[...content.querySelectorAll('code')].map(code => ({
			attributes: [...code.attributes].map(attribute => [attribute.name, attribute.value]),
			parent: code.parentElement?.tagName.toLowerCase(),
			text: code.textContent
		}))
	)
	expect(codeSchema).toEqual([
		{ attributes: [], parent: 'p', text: hostileCode },
		{ attributes: [], parent: 'pre', text: hostileCode }
	])
	await page
		.locator('.poc-content code')
		.last()
		.evaluate(element => {
			for (const type of ['click', 'error']) element.dispatchEvent(new Event(type, { bubbles: true, cancelable: true }))
		})
	await page.evaluate(() => window.dispatchEvent(new Event('load')))

	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
	expect(await page.evaluate(() => window.__markdownPocObservedEvents)).toEqual(['click', 'error', 'load'])
	expect(observations.pageErrors).toEqual([])
	expect(observations.consoleErrors).toEqual([])
	expect(observations.dialogs).toEqual([])
	expect(observations.downloads).toEqual([])
	expect(observations.navigations).toEqual([])
	expect(observations.requests.every(url => new URL(url).hostname === '127.0.0.1')).toBe(true)
})

test('M6.3 Math keeps its enabled KaTeX subset bounded through SSR, hydration, and a hostile update fallback', async ({ page }) => {
	const observations = {
		consoleErrors: [] as string[],
		dialogs: [] as string[],
		downloads: [] as string[],
		navigations: [] as string[],
		pageErrors: [] as string[],
		requests: [] as string[]
	}
	page.on('console', message => {
		if (message.type() === 'error') observations.consoleErrors.push(message.text())
	})
	page.on('dialog', dialog => {
		observations.dialogs.push(dialog.message())
		void dialog.dismiss()
	})
	page.on('download', download => observations.downloads.push(download.suggestedFilename()))
	page.on('framenavigated', frame => {
		if (frame === page.mainFrame()) observations.navigations.push(frame.url())
	})
	page.on('pageerror', error => observations.pageErrors.push(error.message))
	page.on('request', request => observations.requests.push(request.url()))
	await page.addInitScript(() => {
		window.__markdownPocXss = false
		window.__markdownPocObservedEvents = []
		for (const type of ['click', 'error', 'load']) window.addEventListener(type, () => window.__markdownPocObservedEvents.push(type), true)
	})
	const safeMarkdown = '# Safe neighbour\n\n$$E = mc^2$$'
	const hostileMath = '\\href{javascript:alert(1)}{x}'
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'public' }))

	expect(serverHtml).toContain('data-poc-math="katex"')
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown: safeMarkdown, mode: 'public' as const }, moduleUrl: browserClientModule }
	)

	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	await expect(page.locator('[data-poc-math="katex"]')).toHaveCount(1)
	await expect(page.locator('h1')).toHaveText('Safe neighbour')
	await expect(page.locator('.poc-toc')).toHaveText('Safe neighbour')
	await page.evaluate(() => {
		window.__markdownPocObservedEvents.length = 0
	})
	observations.navigations.length = 0
	observations.requests.length = 0
	await page.locator('[data-poc-math="katex"]').evaluate(element => {
		for (const type of ['click', 'error']) element.dispatchEvent(new Event(type, { bubbles: true, cancelable: true }))
	})
	await page.evaluate(() => window.dispatchEvent(new Event('load')))
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: `# Safe neighbour\n\n$$${hostileMath}$$`, mode: 'public' as const })
	await expect(page.locator('code[data-poc-inert="math"]')).toHaveText(hostileMath)
	expect(await page.locator('[data-outcome="local-fallback"]').count()).toBe(1)
	expect(await page.locator('.poc-warnings [data-code="LOCAL_FALLBACK"]').count()).toBe(1)
	expect(
		await page.locator('.poc-content script, .poc-content iframe, .poc-content svg, .poc-content [href], .poc-content [onload], .poc-content [onerror]').count()
	).toBe(0)
	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
	expect(await page.evaluate(() => window.__markdownPocObservedEvents)).toEqual(['click', 'error', 'load'])
	expect(observations.pageErrors).toEqual([])
	expect(observations.consoleErrors).toEqual([])
	expect(observations.dialogs).toEqual([])
	expect(observations.downloads).toEqual([])
	expect(observations.navigations).toEqual([])
	expect(observations.requests).toEqual([])
})

test('M6.2 Mermaid hostile source locally falls back while safe neighbours and TOC survive update', async ({ page }) => {
	const safeMarkdown = '# Initial safe neighbour\n\nSafe text.'
	const mermaidSource = 'flowchart LR\n  A[<img src=x onerror="window.__markdownPocXss = true">] --> B'
	const updatedMarkdown = `# Safe neighbour\n\n\`\`\`mermaid\n${mermaidSource}\n\`\`\``
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'admin-preview' }))

	await page.addInitScript(() => {
		window.__markdownPocXss = false
	})
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown: safeMarkdown, mode: 'admin-preview' as const }, moduleUrl: browserClientModule }
	)

	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: updatedMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('h1')).toHaveText('Safe neighbour')
	await expect(page.locator('.poc-toc')).toHaveText('Safe neighbour')
	await expect(page.locator('code[data-poc-inert="mermaid"]')).toHaveText(mermaidSource)
	expect(await page.locator('[data-outcome="local-fallback"]').count()).toBe(1)
	expect(await page.locator('.poc-warnings [data-code="LOCAL_FALLBACK"]').count()).toBe(1)
	expect(
		await page.locator('.poc-content svg, .poc-content script, .poc-content iframe, .poc-content [onerror], .poc-content [href^="javascript:"]').count()
	).toBe(0)
	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
})

test('M6.4 Mermaid uses only the PoC-owned final SVG boundary', async ({ page }) => {
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: '```mermaid\nflowchart LR\nA --> B\n```', mode: 'public' }))

	expect(serverHtml).toContain('data-poc-mermaid="rendered"')
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await expect(page.locator('.poc-content svg[data-poc-mermaid="rendered"]')).toHaveCount(1)
	await expect(
		page.locator('.poc-content foreignObject, .poc-content style, .poc-content a, .poc-content [href], .poc-content [onload], .poc-content [onerror]')
	).toHaveCount(0)
})

test('M6.2 Markmap hostile link-like source locally falls back after update', async ({ page }) => {
	const safeMarkdown = '# Initial safe neighbour\n\nSafe text.'
	const markmapSource = '# <a href="javascript:alert(1)">Root</a>\n## Child'
	const updatedMarkdown = `# Safe neighbour\n\n\`\`\`markmap\n${markmapSource}\n\`\`\``
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'public' }))

	await page.addInitScript(() => {
		window.__markdownPocXss = false
	})
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown: safeMarkdown, mode: 'public' as const }, moduleUrl: browserClientModule }
	)

	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: updatedMarkdown, mode: 'public' as const })
	await expect(page.locator('h1')).toHaveText('Safe neighbour')
	await expect(page.locator('.poc-toc')).toHaveText('Safe neighbour')
	await expect(page.locator('code[data-poc-inert="markmap"]')).toHaveText(markmapSource)
	expect(await page.locator('[data-outcome="local-fallback"]').count()).toBe(1)
	expect(await page.locator('.poc-warnings [data-code="LOCAL_FALLBACK"]').count()).toBe(1)
	expect(await page.locator('.poc-content a, .poc-content svg, .poc-content script, .poc-content [href^="javascript:"]').count()).toBe(0)
	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
})

test('M6.5 Markmap uses only the PoC-owned finite static SVG boundary', async ({ page }) => {
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: '```markmap\n# Root\n## Child\n```', mode: 'public' }))

	expect(serverHtml).toContain('data-poc-markmap="rendered"')
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await expect(page.locator('.poc-content svg[data-poc-markmap="rendered"]')).toHaveCount(1)
	await expect(
		page.locator('.poc-content a, .poc-content foreignObject, .poc-content style, .poc-content [href], .poc-content [onload], .poc-content [onerror]')
	).toHaveCount(0)
})

test('M6.2 Chart formatter-bearing source locally falls back on update', async ({ page }) => {
	const safeMarkdown = '# Initial safe neighbour\n\nSafe text.'
	const chartSource = '{"type":"bar","xAxis":["A"],"series":[{"data":[1]}],"formatter":"window.__markdownPocXss = true"}'
	const updatedMarkdown = `# Safe neighbour\n\n\`\`\`chart\n${chartSource}\n\`\`\``
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'admin-preview' }))

	await page.addInitScript(() => {
		window.__markdownPocXss = false
	})
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown: safeMarkdown, mode: 'admin-preview' as const }, moduleUrl: browserClientModule }
	)

	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: updatedMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('h1')).toHaveText('Safe neighbour')
	await expect(page.locator('.poc-toc')).toHaveText('Safe neighbour')
	await expect(page.locator('code[data-poc-inert="chart"]')).toHaveText(chartSource)
	expect(await page.locator('[data-outcome="local-fallback"]').count()).toBe(1)
	expect(await page.locator('.poc-warnings [data-code="LOCAL_FALLBACK"]').count()).toBe(1)
	expect(await page.locator('.poc-content canvas, .poc-content script, .poc-content iframe, .poc-content [onload], .poc-content [onerror]').count()).toBe(0)
	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
})

test('M6.6 Chart uses only the PoC-owned bounded Canvas boundary', async ({ page }) => {
	const serverHtml = renderToString(
		React.createElement(PoCBrowserSurface, { markdown: '```chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}]}\n```', mode: 'public' })
	)

	expect(serverHtml).toContain('data-poc-chart="rendered"')
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await expect(page.locator('.poc-content canvas[data-poc-chart="rendered"]')).toHaveCount(1)
	await expect(page.locator('.poc-content script, .poc-content iframe, .poc-content [onload], .poc-content [onerror]')).toHaveCount(0)
})

test('M6.7 global fallback uses only the PoC-owned inert error surface', async ({ page }) => {
	const result = renderMarkdownPoC('```chart\n{}\n```', { mode: 'public', forceGlobalFailure: true })

	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, `<div class="poc-content">${result.html}</div>`)
	await expect(page.locator('[data-poc-global-fallback="true"]')).toHaveCount(1)
	await expect(
		page.locator('.poc-content script, .poc-content svg, .poc-content canvas, .poc-content iframe, .poc-content [onload], .poc-content [onerror]')
	).toHaveCount(0)
})
