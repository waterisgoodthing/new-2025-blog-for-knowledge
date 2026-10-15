import { expect, test } from '@playwright/test'
import React from 'react'
import { renderToString } from 'react-dom/server'
import { PoCBrowserSurface } from '../browser-harness/surface'

const harnessUrl = 'http://127.0.0.1:4179/src/lib/markdown-poc/browser-harness/index.html'
const browserClientModule = '/src/lib/markdown-poc/browser-harness/client.ts'

test('SA-03 keeps mixed isolated outputs, local/global fallback, and cleanup bounded', async ({ page }) => {
	const errors: string[] = []
	const dialogs: string[] = []
	const downloads: string[] = []
	const requests: string[] = []
	const navigations: string[] = []
	page.on('console', message => {
		if (message.type() === 'error') errors.push(message.text())
	})
	page.on('pageerror', error => errors.push(error.message))
	page.on('dialog', dialog => {
		dialogs.push(dialog.message())
		void dialog.dismiss()
	})
	page.on('download', download => downloads.push(download.suggestedFilename()))
	page.on('request', request => requests.push(request.url()))
	page.on('framenavigated', frame => {
		if (frame === page.mainFrame()) navigations.push(frame.url())
	})
	await page.addInitScript(() => {
		window.__markdownPocXss = false
		window.__markdownPocObservedEvents = []
		for (const type of ['click', 'error', 'load']) window.addEventListener(type, () => window.__markdownPocObservedEvents.push(type), true)
	})
	const safe =
		'# Mixed\n\n```mermaid\nflowchart LR\nA --> B\n```\n\n```markmap\n# Root\n## Child\n```\n\n```chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}]}\n```'
	const hostile =
		'# Mixed\n\n```mermaid\nflowchart LR\nA[<img src=x onerror="window.__markdownPocXss=true">] --> B\n```\n\n```markmap\n# <a href="javascript:alert(1)">Root</a>\n```\n\n```chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}],"formatter":"x"}\n```'
	const html = renderToString(React.createElement(PoCBrowserSurface, { markdown: safe, mode: 'admin-preview' }))
	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, value) => {
		root.innerHTML = value as string
	}, html)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown: safe, mode: 'admin-preview' as const }, moduleUrl: browserClientModule }
	)
	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	await expect(page.locator('[data-poc-mermaid="rendered"]')).toHaveCount(1)
	await expect(page.locator('[data-poc-markmap="rendered"]')).toHaveCount(1)
	await expect(page.locator('[data-poc-chart-drawn="true"]')).toHaveCount(1)
	await page.evaluate(next => window.__markdownPocBrowserHarness.update(next), { markdown: hostile, mode: 'admin-preview' as const })
	await expect(page.locator('code[data-poc-inert]')).toHaveCount(3)
	await expect(page.locator('[data-outcome="local-fallback"]')).toHaveCount(1)
	await page.evaluate(() => window.__markdownPocBrowserHarness.unmount())
	expect(await page.evaluate(() => window.__markdownPocXss)).toBe(false)
	expect(errors).toEqual([])
	expect(dialogs).toEqual([])
	expect(downloads).toEqual([])
	expect(navigations.slice(1)).toEqual([])
	expect(requests.every(url => new URL(url).hostname === '127.0.0.1')).toBe(true)
	await expect(page.locator('[data-poc-browser-root] > *')).toHaveCount(0)
})
