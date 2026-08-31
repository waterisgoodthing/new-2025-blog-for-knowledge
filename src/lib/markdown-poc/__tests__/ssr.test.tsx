/**
 * M3 SSR tests — real server-side rendering via React renderToString.
 *
 * These tests create a test-only React component that consumes
 * renderMarkdownPoC, call renderToString, and assert on the
 * serialized HTML. This is NOT a stub-function test.
 *
 * All security/semantic tests currently FAIL because the stub
 * returns empty output. Reds map to M4–M6 contracts not yet
 * implemented, not to TypeScript or module errors.
 */

import { describe, it, expect } from 'vitest'
import React from 'react'
import { renderToString } from 'react-dom/server'
import { renderMarkdownPoC } from '../render-poc'
import { markdownFixtures, type MarkdownFixture } from '../fixtures'
import { hasDangerousUrlAttribute, hasEventHandlerAttribute, hasLiveElement } from './dom-contract'

// ---------------------------------------------------------------------------
// Test-only React surface — consumes renderMarkdownPoC and produces
// serializable markup. This component is NOT production code.
// ---------------------------------------------------------------------------

function PocRenderer({ markdown, mode }: { markdown: string; mode: 'public' | 'admin-preview' }) {
	const result = renderMarkdownPoC(markdown, { mode })

	return React.createElement(
		'div',
		{
			className: 'poc-renderer',
			'data-outcome': result.outcome,
			'data-toc-count': result.toc.length,
			'data-warning-count': result.warnings.length
		},
		React.createElement('div', {
			className: 'poc-content',
			dangerouslySetInnerHTML: { __html: result.html }
		}),
		React.createElement(
			'ul',
			{ className: 'poc-toc' },
			...result.toc.map(item => React.createElement('li', { key: item.id, 'data-level': item.level }, item.text))
		),
		React.createElement(
			'ul',
			{ className: 'poc-warnings' },
			...result.warnings.map((w, i) => React.createElement('li', { key: i, 'data-code': w.code }, w.message))
		)
	)
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderSSR(markdown: string, mode: 'public' | 'admin-preview'): string {
	return renderToString(React.createElement(PocRenderer, { markdown, mode }))
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('M3 SSR (real renderToString): output is deterministic', () => {
	it('same input produces identical serialized HTML on repeated calls', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-headings-stable-toc')!
		const html1 = renderSSR(fixture.markdown, 'public')
		const html2 = renderSSR(fixture.markdown, 'public')
		expect(html1).toBe(html2)
	})
})

describe('M3 SSR (real renderToString): security fixtures produce safe SSR HTML', () => {
	const securityFixtures = markdownFixtures.filter(f => f.id.startsWith('security-'))

	for (const fixture of securityFixtures) {
		it(`fixture "${fixture.id}": no <script> element in SSR HTML`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			// Live <script> tags (not data- attrs) must not appear
			expect(hasLiveElement(html, 'script')).toBe(false)
		})

		it(`fixture "${fixture.id}": no event handler attributes in SSR HTML`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			expect(hasEventHandlerAttribute(html)).toBe(false)
		})

		it(`fixture "${fixture.id}": no dangerous URLs in SSR HTML`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			expect(hasDangerousUrlAttribute(html)).toBe(false)
		})
	}
})

describe('M3 SSR (real renderToString): safe content expectation produces red for stub', () => {
	// The stub returns empty html.  These assertions prove that a real renderer
	// MUST populate html — otherwise the SSR output is vacuous.  Every one of
	// these tests is RED for the stub, GREEN only after M4–M6 implement real
	// bounded parsing + sanitization.

	const semanticFixtures = markdownFixtures.filter(f => f.id.startsWith('semantic-'))

	for (const fixture of semanticFixtures) {
		it(`fixture "${fixture.id}": SSR HTML contains expected semantic elements`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			for (const expected of fixture.expected.contains ?? []) {
				expect(html.includes(expected), `SSR output for ${fixture.id} should contain "${expected}"`).toBe(true)
			}
		})

		it(`fixture "${fixture.id}": TOC entries present in SSR HTML`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			if (fixture.expected.toc && fixture.expected.toc.length > 0) {
				for (const entry of fixture.expected.toc) {
					expect(html).toContain(entry.text)
				}
			}
		})
	}

	// Additional explicit red-light: security-sentinel fixture
	it('security-client-update-safe-to-malicious: safe heading present in SSR HTML', () => {
		const fixture = markdownFixtures.find(f => f.id === 'security-client-update-safe-to-malicious')!
		const html = renderSSR(fixture.markdown, fixture.mode)
		expect(html).toContain('Safe heading')
	})

	it('security-malformed-local-fallback: safe heading survives malformed input', () => {
		const fixture = markdownFixtures.find(f => f.id === 'security-malformed-local-fallback')!
		const html = renderSSR(fixture.markdown, fixture.mode)
		expect(html).toContain('Keep this heading')
	})
})

describe('M3 SSR (real renderToString): contract metadata in SSR HTML', () => {
	it('SSR HTML contains outcome as data attribute', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-headings-stable-toc')!
		const html = renderSSR(fixture.markdown, 'public')
		// The PocRenderer uses data-outcome on the root div
		expect(html).toContain('data-outcome=')
	})

	it('SSR HTML contains TOC count as data attribute', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-headings-stable-toc')!
		const html = renderSSR(fixture.markdown, 'public')
		expect(html).toContain('data-toc-count=')
	})

	it('SSR HTML contains warning count as data attribute', () => {
		const fixture = markdownFixtures.find(f => f.id === 'semantic-headings-stable-toc')!
		const html = renderSSR(fixture.markdown, 'public')
		expect(html).toContain('data-warning-count=')
	})
})

describe('M3 SSR (real renderToString): special renderers produce inert fallback in SSR', () => {
	const specialFixtures = markdownFixtures.filter(f => f.id.startsWith('special-'))

	for (const fixture of specialFixtures) {
		it(`fixture "${fixture.id}": no live script/iframe/svg in SSR HTML`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			expect(hasLiveElement(html, 'script')).toBe(false)
			expect(hasLiveElement(html, 'iframe')).toBe(false)
			expect(hasEventHandlerAttribute(html)).toBe(false)
			expect(hasDangerousUrlAttribute(html)).toBe(false)
		})

		it(`fixture "${fixture.id}": SSR outcome is inert, local-fallback, or allow`, () => {
			const html = renderSSR(fixture.markdown, fixture.mode)
			const hasInert = html.includes('data-outcome="inert"')
			const hasFallback = html.includes('data-outcome="local-fallback"')
			const hasAllow = html.includes('data-outcome="allow"')
			expect(hasInert || hasFallback || hasAllow).toBe(true)
		})
	}
})

describe('M5.2 Code final-output contract: SSR preserves exact hostile code text', () => {
	it('renders hostile code as exact parsed text without executable elements or attributes', () => {
		const hostileCode = '<img src="javascript:alert(1)" onerror="window.__markdownPocXss = true">'
		const template = document.createElement('template')
		template.innerHTML = renderSSR(`Inline \`${hostileCode}\`.\n\n\`\`\`html\n${hostileCode}\n\`\`\``, 'admin-preview')
		const codeTexts = [...template.content.querySelectorAll('.poc-content code')].map(code => code.textContent)

		expect(codeTexts).toEqual([hostileCode, hostileCode])
		expect(template.content.querySelector('.poc-content script, .poc-content iframe, .poc-content svg')).toBeNull()
		for (const element of template.content.querySelectorAll('.poc-content *')) {
			for (const attribute of element.attributes) {
				expect(attribute.name.toLowerCase()).not.toMatch(/^on/)
			}
		}
	})
})
