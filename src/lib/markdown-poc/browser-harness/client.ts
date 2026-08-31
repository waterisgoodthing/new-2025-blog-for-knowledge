import React from 'react'
import { hydrateRoot } from 'react-dom/client'

import { PoCBrowserSurface } from './surface'
import type { BrowserHarnessProps } from './globals'

const rootElement = document.querySelector('[data-poc-browser-root]')
const initial = window.__markdownPocBrowserInitial

if (!rootElement || !initial) {
	throw new Error('Markdown PoC browser harness requires an SSR root and initial synthetic props.')
}

const root = hydrateRoot(rootElement, React.createElement(PoCBrowserSurface, initial))

window.__markdownPocBrowserHarness = {
	update(next: BrowserHarnessProps) {
		root.render(React.createElement(PoCBrowserSurface, next))
	},
	unmount() {
		root.unmount()
	}
}
