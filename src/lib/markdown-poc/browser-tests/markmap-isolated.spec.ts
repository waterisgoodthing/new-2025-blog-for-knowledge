import { expect, test } from '@playwright/test'
import React from 'react'
import { renderToString } from 'react-dom/server'

import { PoCBrowserSurface } from '../browser-harness/surface'

const harnessUrl = 'http://127.0.0.1:4179/src/lib/markdown-poc/browser-harness/index.html'
const browserClientModule = '/src/lib/markdown-poc/browser-harness/client.ts'

test('Markmap-01 requires an isolated SVG without links, navigation, download, or lifecycle residue', async ({ page }) => {
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
		for (const type of ['click', 'error', 'load', 'wheel', 'pointerdown'])
			window.addEventListener(type, () => window.__markdownPocObservedEvents.push(type), true)
	})

	const safeMarkdown = '# Safe Markmap\n\n```markmap\n# Root\n## Child\n```'
	const hostileSource = '# <a href="javascript:alert(1)">Root</a>\n## Child'
	const hostileMarkdown = `# Safe Markmap\n\n\`\`\`markmap\n${hostileSource}\n\`\`\``
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'admin-preview' }))

	expect(serverHtml).toContain('data-poc-markmap="rendered"')
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
	await expect(page.locator('.poc-content svg[data-poc-markmap="rendered"]')).toHaveCount(1)
	expect(
		await page
			.locator(
				'.poc-content foreignObject, .poc-content script, .poc-content style, .poc-content a, .poc-content image, .poc-content [href], .poc-content [xlink\\:href], .poc-content [onload], .poc-content [onerror]'
			)
			.count()
	).toBe(0)

	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: hostileMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('code[data-poc-inert="markmap"]')).toHaveText(hostileSource)
	await expect(page.locator('[data-outcome="local-fallback"]')).toHaveCount(1)
	await expect(page.locator('.poc-warnings [data-code="LOCAL_FALLBACK"]')).toHaveCount(1)

	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: safeMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('.poc-content svg[data-poc-markmap="rendered"]')).toHaveCount(1)
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: safeMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('.poc-content svg[data-poc-markmap="rendered"]')).toHaveCount(1)
	await page.evaluate(() => {
		window.__markdownPocObservedEvents = []
	})
	observations.navigations.splice(0)
	await page.locator('.poc-content svg[data-poc-markmap="rendered"]').evaluate(element => {
		for (const type of ['click', 'error', 'wheel', 'pointerdown']) element.dispatchEvent(new Event(type, { bubbles: true, cancelable: true }))
	})
	await page.evaluate(() => window.dispatchEvent(new Event('load')))
	await page.evaluate(() => window.__markdownPocBrowserHarness.unmount())

	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
	expect(await page.evaluate(() => window.__markdownPocObservedEvents)).toEqual(['click', 'error', 'wheel', 'pointerdown', 'load'])
	expect(observations.pageErrors).toEqual([])
	expect(observations.consoleErrors).toEqual([])
	expect(observations.dialogs).toEqual([])
	expect(observations.downloads).toEqual([])
	expect(observations.navigations).toEqual([])
	expect(observations.requests.every(url => new URL(url).hostname === '127.0.0.1')).toBe(true)
	await page.screenshot({ path: 'docs/workflows/markdown-special-adapter-enablement/assets/markmap-02-final-pass.png', fullPage: true })
	await expect(page.locator('[data-poc-browser-root] > *')).toHaveCount(0)
})
