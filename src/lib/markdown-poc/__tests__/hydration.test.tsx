/**
 * M3 Hydration tests — real React hydration via hydrateRoot.
 *
 * These tests create a React component, renderToString to get server
 * HTML, place it in a jsdom container, call hydrateRoot, and then
 * update content before asserting.  This is NOT a plain-function-call
 * comparison.
 *
 * All security/semantic tests currently FAIL because the stub returns
 * empty output.  Reds map to M4–M6 contracts not yet implemented.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import React from 'react'
import { renderToString } from 'react-dom/server'
import { hydrateRoot, createRoot, type Root } from 'react-dom/client'
import { act } from 'react'
import { renderMarkdownPoC } from '../render-poc'
import { markdownFixtures } from '../fixtures'
import { hasDangerousUrlAttribute, hasEventHandlerAttribute, hasLiveElement } from './dom-contract'

// ---------------------------------------------------------------------------
// Test-only React component — receives markdown + mode, renders PoC output.
// ---------------------------------------------------------------------------

function MarkdownDisplay({ markdown, mode }: { markdown: string; mode: 'public' | 'admin-preview' }) {
	const result = renderMarkdownPoC(markdown, { mode })

	return React.createElement(
		'div',
		{
			className: 'markdown-display',
			'data-outcome': result.outcome
		},
		React.createElement('div', {
			className: 'md-content',
			dangerouslySetInnerHTML: { __html: result.html }
		}),
		React.createElement(
			'ul',
			{ className: 'md-warnings' },
			...result.warnings.map((w, i) => React.createElement('li', { key: i, 'data-code': w.code }, w.message))
		)
	)
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Test helpers — DOM container lifecycle
// ---------------------------------------------------------------------------

let container: HTMLDivElement

beforeEach(() => {
	container = document.createElement('div')
	container.id = 'hydration-root'
	document.body.appendChild(container)
})

afterEach(() => {
	if (container.parentNode) {
		container.parentNode.removeChild(container)
	}
})

/**
 * Hydrate the container with server HTML, then re-render with updated
 * markdown.  Returns the container's innerHTML after hydration.
 */
async function hydrateAndUpdate(initialMarkdown: string, updatedMarkdown: string, mode: 'public' | 'admin-preview'): Promise<string> {
	// 1. Generate server HTML from the initial markdown
	const serverHtml = renderToString(
		React.createElement(MarkdownDisplay, {
			markdown: initialMarkdown,
			mode
		})
	)

	// 2. Place server HTML in jsdom container
	container.innerHTML = serverHtml

	// 3. Hydrate
	let root: Root
	await act(async () => {
		root = hydrateRoot(
			container,
			React.createElement(MarkdownDisplay, {
				markdown: initialMarkdown,
				mode
			})
		)
	})

	// 4. Update to malicious markdown
	await act(async () => {
		root.render(
			React.createElement(MarkdownDisplay, {
				markdown: updatedMarkdown,
				mode
			})
		)
	})

	return container.innerHTML
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('M3 Hydration (real hydrateRoot): safe-to-malicious update does not introduce danger', () => {
	const fixture = markdownFixtures.find(f => f.id === 'security-client-update-safe-to-malicious')!

	it('safe content survives update to malicious markdown', async () => {
		const html = await hydrateAndUpdate(fixture.updateFrom!, fixture.markdown, fixture.mode)

		// Safe heading must be preserved after malicious update
		expect(html).toContain('Safe heading')
		// Dangerous elements must not appear
		expect(hasLiveElement(html, 'script')).toBe(false)
		expect(hasDangerousUrlAttribute(html)).toBe(false)
		expect(hasEventHandlerAttribute(html)).toBe(false)
	})

	it('update produces CLIENT_UPDATE_SANITIZED warning', async () => {
		const html = await hydrateAndUpdate(fixture.updateFrom!, fixture.markdown, fixture.mode)
		expect(html).toContain('CLIENT_UPDATE_SANITIZED')
	})
})

describe('M3 Hydration (real hydrateRoot): failure is local, not global', () => {
	const malformedFixture = markdownFixtures.find(f => f.id === 'security-malformed-local-fallback')!

	it('malformed input preserves safe heading after hydration', async () => {
		const html = await hydrateAndUpdate('# Safe heading\n\nA safe paragraph.', malformedFixture.markdown, malformedFixture.mode)

		expect(html).toContain('Keep this heading')
		expect(html.length).toBeGreaterThan(0)
	})

	it('malformed input does not introduce dangerous elements', async () => {
		const html = await hydrateAndUpdate('# Safe heading\n\nA safe paragraph.', malformedFixture.markdown, malformedFixture.mode)

		expect(hasLiveElement(html, 'not-closed')).toBe(false)
		expect(hasEventHandlerAttribute(html)).toBe(false)
		expect(hasDangerousUrlAttribute(html)).toBe(false)
	})
})

describe('M3 Hydration (real hydrateRoot): repeated renders are stable (no residue)', () => {
	const fixture = markdownFixtures.find(f => f.id === 'security-script-and-raw-html')!

	it('rendering malicious markdown multiple times does not accumulate danger', async () => {
		const html1 = await hydrateAndUpdate('# Safe start', fixture.markdown, fixture.mode)

		const container2 = document.createElement('div')
		container2.id = 'root-2'
		document.body.appendChild(container2)
		const serverHtml = renderToString(
			React.createElement(MarkdownDisplay, {
				markdown: '# Safe start',
				mode: fixture.mode
			})
		)
		container2.innerHTML = serverHtml

		let root2: Root
		await act(async () => {
			root2 = hydrateRoot(
				container2,
				React.createElement(MarkdownDisplay, {
					markdown: '# Safe start',
					mode: fixture.mode
				})
			)
		})
		await act(async () => {
			root2.render(
				React.createElement(MarkdownDisplay, {
					markdown: fixture.markdown,
					mode: fixture.mode
				})
			)
		})
		const html2 = container2.innerHTML

		expect(html1).toBe(html2)
		expect(hasLiveElement(html1, 'script')).toBe(false)
		expect(hasEventHandlerAttribute(html1)).toBe(false)

		document.body.removeChild(container2)
	})
})

describe('M3 Hydration (real hydrateRoot): special renderer inert fallback does not leak', () => {
	const mermaidMalicious = markdownFixtures.find(f => f.id === 'special-mermaid-malicious')!
	const markmapMalicious = markdownFixtures.find(f => f.id === 'special-markmap-malicious')!
	const chartMalicious = markdownFixtures.find(f => f.id === 'special-chart-malicious-or-invalid')!

	it('malicious mermaid does not produce onerror or __markdownPocXss', async () => {
		const html = await hydrateAndUpdate('# Safe start', mermaidMalicious.markdown, mermaidMalicious.mode)
		expect(hasEventHandlerAttribute(html)).toBe(false)
		expect(hasLiveElement(html, 'script')).toBe(false)
	})

	it('malicious markmap does not produce javascript: protocol', async () => {
		const html = await hydrateAndUpdate('# Safe start', markmapMalicious.markdown, markmapMalicious.mode)
		expect(hasDangerousUrlAttribute(html)).toBe(false)
	})

	it('malicious chart does not introduce script or event handlers', async () => {
		const html = await hydrateAndUpdate('# Safe start', chartMalicious.markdown, chartMalicious.mode)
		expect(hasLiveElement(html, 'script')).toBe(false)
		expect(hasEventHandlerAttribute(html)).toBe(false)
	})
})

describe('M5.2 Code final-output contract: hydration preserves exact hostile code text', () => {
	it('updates to hostile code as exact parsed text without executable DOM', async () => {
		const hostileCode = '<img src="javascript:alert(1)" onerror="window.__markdownPocXss = true">'
		const html = await hydrateAndUpdate('# Safe start', `Inline \`${hostileCode}\`.\n\n\`\`\`html\n${hostileCode}\n\`\`\``, 'admin-preview')
		const template = document.createElement('template')
		template.innerHTML = html
		const codeTexts = [...template.content.querySelectorAll('.md-content code')].map(code => code.textContent)

		expect(codeTexts).toEqual([hostileCode, hostileCode])
		expect(template.content.querySelector('.md-content script, .md-content iframe, .md-content svg')).toBeNull()
		for (const element of template.content.querySelectorAll('.md-content *')) {
			for (const attribute of element.attributes) {
				expect(attribute.name.toLowerCase()).not.toMatch(/^on/)
			}
		}
	})
})

describe('M3 Hydration (real hydrateRoot): stub produces meaningful red-light', () => {
	// The stub returns empty html.  These tests prove that hydrateRoot
	// MUST produce expected content; empty output = red light.

	it('hydrated output contains safe heading (red for stub)', async () => {
		const html = await hydrateAndUpdate('# Safe heading\n\nA safe paragraph.', '# Safe heading\n\nStill safe.', 'public')
		// Stub returns empty → this assertion FAILS (correct red)
		expect(html).toContain('Safe heading')
	})

	it('hydrated output is non-empty (red for stub)', async () => {
		const html = await hydrateAndUpdate('# Any heading', '# Any heading\n\nMore text.', 'public')
		expect(html.length).toBeGreaterThan(100)
	})

	it('hydrateRoot does not throw on valid React tree', async () => {
		const serverHtml = renderToString(
			React.createElement(MarkdownDisplay, {
				markdown: '# Test',
				mode: 'public'
			})
		)
		container.innerHTML = serverHtml

		// hydrateRoot should not throw for a valid React tree
		await act(async () => {
			const root = hydrateRoot(
				container,
				React.createElement(MarkdownDisplay, {
					markdown: '# Test',
					mode: 'public'
				})
			)
			// Verify we got a root back (performs initial render)
			expect(root).toBeDefined()
		})
	})
})
