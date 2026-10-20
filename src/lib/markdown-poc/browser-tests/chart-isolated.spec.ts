import { expect, test } from '@playwright/test'
import React from 'react'
import { renderToString } from 'react-dom/server'

import { PoCBrowserSurface } from '../browser-harness/surface'

const harnessUrl = 'http://127.0.0.1:4179/src/lib/markdown-poc/browser-harness/index.html'
const browserClientModule = '/src/lib/markdown-poc/browser-harness/client.ts'

test('Chart-01 requires an isolated Canvas with no executable configuration, network, download, or residue', async ({ page }) => {
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

	const safeMarkdown = '# Safe Chart\n\n```chart\n{"type":"bar","xAxis":["A","B"],"series":[{"name":"Synthetic","data":[1,2]}]}\n```'
	const hostileSource = '{"type":"bar","xAxis":["A"],"series":[{"data":[1]}],"formatter":"window.__markdownPocXss = true"}'
	const hostileMarkdown = `# Safe Chart\n\n\`\`\`chart\n${hostileSource}\n\`\`\``
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: safeMarkdown, mode: 'admin-preview' }))

	expect(serverHtml).toContain('data-poc-chart="rendered"')
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
	await expect(page.locator('.poc-content canvas[data-poc-chart="rendered"]')).toHaveCount(1)
	const initialCanvas = await page.locator('.poc-content canvas[data-poc-chart="rendered"]').evaluate(canvas => ({
		drawn: canvas.getAttribute('data-poc-chart-drawn'),
		source: canvas.getAttribute('data-poc-chart-source'),
		context: Boolean((canvas as HTMLCanvasElement).getContext('2d'))
	}))
	expect(initialCanvas).toEqual({ drawn: 'true', source: expect.any(String), context: true })
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: hostileMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('code[data-poc-inert="chart"]')).toHaveText(hostileSource)
	await expect(page.locator('[data-outcome="local-fallback"]')).toHaveCount(1)
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: safeMarkdown, mode: 'admin-preview' as const })
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: safeMarkdown, mode: 'admin-preview' as const })
	await expect(page.locator('.poc-content canvas[data-poc-chart="rendered"]')).toHaveCount(1)
	await page.evaluate(() => {
		window.__markdownPocObservedEvents = []
	})
	observations.navigations.splice(0)
	await page.locator('.poc-content canvas[data-poc-chart="rendered"]').evaluate(element => {
		for (const type of ['click', 'error']) element.dispatchEvent(new Event(type, { bubbles: true, cancelable: true }))
	})
	await page.evaluate(() => window.dispatchEvent(new Event('load')))
	await page.evaluate(() => window.__markdownPocBrowserHarness.unmount())

	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
	expect(await page.evaluate(() => window.__markdownPocObservedEvents)).toEqual(['click', 'error', 'load'])
	expect(observations.pageErrors).toEqual([])
	expect(observations.consoleErrors).toEqual([])
	expect(observations.dialogs).toEqual([])
	expect(observations.downloads).toEqual([])
	expect(observations.navigations).toEqual([])
	expect(observations.requests.every(url => new URL(url).hostname === '127.0.0.1')).toBe(true)
	await page.screenshot({ path: 'docs/workflows/markdown-special-adapter-enablement/assets/chart-02-final-pass.png', fullPage: true })
	await expect(page.locator('[data-poc-browser-root] > *')).toHaveCount(0)
})
