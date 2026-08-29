import { expect, test } from '@playwright/test'
import React from 'react'
import { renderToString } from 'react-dom/server'

import { PoCBrowserSurface } from '../browser-harness/surface'

const harnessUrl = 'http://127.0.0.1:4179/src/lib/markdown-poc/browser-harness/index.html'
const browserClientModule = '/src/lib/markdown-poc/browser-harness/client.ts'

const candidates = [
	{
		name: 'Mermaid',
		marker: 'data-poc-mermaid',
		selector: '[data-poc-mermaid]',
		safeMarkdown: '# Safe Mermaid\n\n```mermaid\nflowchart LR\nA[Start] --> B[End]\n```',
		hostileMarkdown: '# Safe Mermaid\n\n```mermaid\nflowchart LR\nA[<img src=x onerror="window.__markdownPocXss = true">] --> B\n```'
	},
	{
		name: 'Markmap',
		marker: 'data-poc-markmap',
		selector: '[data-poc-markmap]',
		safeMarkdown: '# Safe Markmap\n\n```markmap\n# Root\n## Child\n```',
		hostileMarkdown: '# Safe Markmap\n\n```markmap\n# <a href="javascript:alert(1)">Root</a>\n## Child\n```'
	},
	{
		name: 'Chart',
		marker: 'data-poc-chart',
		selector: '[data-poc-chart]',
		safeMarkdown: '# Safe Chart\n\n```chart\n{"type":"bar","xAxis":["A","B"],"series":[{"name":"Synthetic","data":[1,2]}]}\n```',
		hostileMarkdown: '# Safe Chart\n\n```chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}],"formatter":"window.__markdownPocXss = true"}\n```'
	}
] as const

for (const candidate of candidates) {
	test(`SA-02 ${candidate.name} shared baseline requires an isolated output after SSR, hydration, hostile update, repeat render, and cleanup`, async ({
		page
	}) => {
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

		const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown: candidate.safeMarkdown, mode: 'admin-preview' }))
		const ssrContainsIsolatedOutput = serverHtml.includes(candidate.marker)

		await page.goto(harnessUrl)
		await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
			root.innerHTML = html as string
		}, serverHtml)
		await page.evaluate(
			async ({ initial, moduleUrl }) => {
				window.__markdownPocBrowserInitial = initial
				await import(/* @vite-ignore */ moduleUrl)
			},
			{ initial: { markdown: candidate.safeMarkdown, mode: 'admin-preview' as const }, moduleUrl: browserClientModule }
		)

		await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
		await expect(page.locator(`.poc-content ${candidate.selector}`)).toHaveCount(1)
		const hydratedOutputCount = await page.locator(`.poc-content ${candidate.selector}`).count()
		await page.evaluate(() => {
			window.__markdownPocObservedEvents.length = 0
		})
		observations.navigations.length = 0
		observations.requests.length = 0

		await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: candidate.hostileMarkdown, mode: 'admin-preview' as const })
		await expect(page.locator('h1')).toHaveText(`Safe ${candidate.name}`)
		expect(
			await page.locator('.poc-content script, .poc-content iframe, .poc-content [onload], .poc-content [onerror], .poc-content [href^="javascript:"]').count()
		).toBe(0)
		expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)

		await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: candidate.safeMarkdown, mode: 'admin-preview' as const })
		await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: candidate.safeMarkdown, mode: 'admin-preview' as const })
		await expect(page.locator(`.poc-content ${candidate.selector}`)).toHaveCount(1)
		const repeatedOutputCount = await page.locator(`.poc-content ${candidate.selector}`).count()
		await page.locator('.poc-content').evaluate(element => {
			for (const type of ['click', 'error']) element.dispatchEvent(new Event(type, { bubbles: true, cancelable: true }))
		})
		await page.evaluate(() => window.dispatchEvent(new Event('load')))
		await page.evaluate(() => window.__markdownPocBrowserHarness.unmount())

		expect(await page.evaluate(() => window.__markdownPocObservedEvents)).toEqual(['click', 'error', 'load'])
		expect(observations.pageErrors).toEqual([])
		expect(observations.consoleErrors).toEqual([])
		expect(observations.dialogs).toEqual([])
		expect(observations.downloads).toEqual([])
		expect(observations.navigations).toEqual([])
		expect(observations.requests.every(url => new URL(url).hostname === '127.0.0.1')).toBe(true)
		await expect(page.locator('[data-poc-browser-root] > *')).toHaveCount(0)
		expect({ ssrContainsIsolatedOutput, hydratedOutputCount, repeatedOutputCount }).toEqual({
			ssrContainsIsolatedOutput: true,
			hydratedOutputCount: 1,
			repeatedOutputCount: 1
		})
	})
}
