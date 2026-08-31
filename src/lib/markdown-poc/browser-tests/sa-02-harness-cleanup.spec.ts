import { expect, test } from '@playwright/test'
import React from 'react'
import { renderToString } from 'react-dom/server'

import { PoCBrowserSurface } from '../browser-harness/surface'

const harnessUrl = 'http://127.0.0.1:4179/src/lib/markdown-poc/browser-harness/index.html'
const browserClientModule = '/src/lib/markdown-poc/browser-harness/client.ts'

test('SA-02 browser harness exposes explicit cleanup after hydration', async ({ page }) => {
	const markdown = '# Synthetic heading\n\nSynthetic body.'
	const serverHtml = renderToString(React.createElement(PoCBrowserSurface, { markdown, mode: 'public' }))

	await page.goto(harnessUrl)
	await page.locator('[data-poc-browser-root]').evaluate((root, html) => {
		root.innerHTML = html as string
	}, serverHtml)
	await page.evaluate(
		async ({ initial, moduleUrl }) => {
			window.__markdownPocBrowserInitial = initial
			await import(/* @vite-ignore */ moduleUrl)
		},
		{ initial: { markdown, mode: 'public' as const }, moduleUrl: browserClientModule }
	)

	await expect(page.locator('[data-poc-phase="hydrated"]')).toHaveCount(1)
	expect(await page.evaluate(() => typeof window.__markdownPocBrowserHarness.unmount)).toBe('function')
	await page.evaluate(() => window.__markdownPocBrowserHarness.unmount())
	await expect(page.locator('[data-poc-browser-root] > *')).toHaveCount(0)
})
