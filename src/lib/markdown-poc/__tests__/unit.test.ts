/**
 * M3 Unit tests — red-light tests for the Markdown PoC.
 *
 * These tests consume every fixture id and assert that the PoC renderer
 * (once implemented in M4–M6) produces safe, correct output.
 *
 * Current state: all tests FAIL because renderMarkdownPoC is a stub
 * that returns empty output with NOT_IMPLEMENTED.
 */

import { describe, it, expect } from 'vitest'
import { renderMarkdownPoC } from '../render-poc'
import { markdownFixtures } from '../fixtures'
import { hasDangerousUrlAttribute, hasEventHandlerAttribute, hasLiveElement } from './dom-contract'

describe('M3 Unit: PoC renderer consumes all fixtures', () => {
	for (const fixture of markdownFixtures) {
		it(`fixture "${fixture.id}" produces expected outcome`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(result.outcome).toBe(fixture.expected.outcome)
		})

		it(`fixture "${fixture.id}" produces expected warning codes`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			const expectedCodes = fixture.expected.warnings
			for (const code of expectedCodes) {
				expect(
					result.warnings.some(w => w.code === code),
					`expected warning code ${code} for fixture ${fixture.id}`
				).toBe(true)
			}
		})
	}
})

describe('M3 Unit: dangerous elements are blocked', () => {
	const securityFixtures = markdownFixtures.filter(f => f.id.startsWith('security-'))

	for (const fixture of securityFixtures) {
		it(`fixture "${fixture.id}" has no live <script> element`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'script')).toBe(false)
		})

		it(`fixture "${fixture.id}" has no live <iframe> element`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'iframe')).toBe(false)
		})

		it(`fixture "${fixture.id}" has no live <svg> element`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'svg')).toBe(false)
		})

		it(`fixture "${fixture.id}" has no event handler attributes`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasEventHandlerAttribute(result.html)).toBe(false)
		})

		it(`fixture "${fixture.id}" has no dangerous protocols in href/src`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasDangerousUrlAttribute(result.html)).toBe(false)
		})

		it(`fixture "${fixture.id}" does not set __markdownPocXss via script or event`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'script')).toBe(false)
			expect(hasEventHandlerAttribute(result.html)).toBe(false)
		})
	}
})

describe('M3 Unit: absent assertions check DOM, not source text', () => {
	const fixturesWithAbsent = markdownFixtures.filter(f => f.expected.absent)

	for (const fixture of fixturesWithAbsent) {
		it(`fixture "${fixture.id}": absent items do not appear as live DOM`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })

			for (const absent of fixture.expected.absent ?? []) {
				if (absent.startsWith('<')) {
					const tag = absent.match(/^<\s*([a-z][\w-]*)/i)?.[1]
					expect(tag, `expected a tag name in fixture absence ${absent}`).toBeTruthy()
					expect(hasLiveElement(result.html, tag!)).toBe(false)
				}
				if (absent.includes('javascript:') || absent.includes('vbscript:') || absent.includes('data:text/html') || absent.includes('data:image/svg+xml')) {
					expect(hasDangerousUrlAttribute(result.html)).toBe(false)
				}
				if (absent.includes('onerror') || absent.includes('onload')) {
					expect(hasEventHandlerAttribute(result.html)).toBe(false)
				}
				if (absent === '__markdownPocXss') {
					expect(hasLiveElement(result.html, 'script')).toBe(false)
					expect(hasEventHandlerAttribute(result.html)).toBe(false)
				}
				if (absent.includes('xlink:href') || absent.includes('foreignObject') || absent.includes('srcdoc')) {
					expect(result.html.toLowerCase()).not.toContain(absent.toLowerCase())
				}
			}
		})
	}
})

describe('M3 Unit: safe semantic content is preserved', () => {
	const semanticFixtures = markdownFixtures.filter(f => f.id.startsWith('semantic-'))

	for (const fixture of semanticFixtures) {
		it(`fixture "${fixture.id}": expected content is present`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			for (const expected of fixture.expected.contains ?? []) {
				expect(
					result.html.includes(expected) || result.toc.some(t => t.text.includes(expected)),
					`expected "${expected}" in output for fixture ${fixture.id}`
				).toBe(true)
			}
		})

		it(`fixture "${fixture.id}": TOC matches expected entries`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			if (fixture.expected.toc) {
				expect(result.toc).toHaveLength(fixture.expected.toc.length)
				for (let i = 0; i < fixture.expected.toc.length; i++) {
					expect(result.toc[i].level).toBe(fixture.expected.toc[i].level)
					expect(result.toc[i].text).toBe(fixture.expected.toc[i].text)
				}
			}
		})
	}
})

describe('M3 Unit: special renderers remain inert until validated', () => {
	const specialFixtures = markdownFixtures.filter(f => f.id.startsWith('special-'))

	for (const fixture of specialFixtures) {
		it(`fixture "${fixture.id}": outcome is inert, local-fallback, or allow`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(['inert', 'local-fallback', 'allow']).toContain(result.outcome)
		})

		it(`fixture "${fixture.id}": no dangerous elements in output`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			expect(hasLiveElement(result.html, 'script')).toBe(false)
			expect(hasLiveElement(result.html, 'iframe')).toBe(false)
			expect(hasEventHandlerAttribute(result.html)).toBe(false)
			expect(hasDangerousUrlAttribute(result.html)).toBe(false)
		})
	}
})

describe('M5.2 Code final-output contract: hostile source remains exact inert text', () => {
	it('preserves fenced hostile source as parsed code text with no executable DOM', () => {
		const hostileCode = '<img src="javascript:alert(1)" onerror="window.__markdownPocXss = true">'
		const result = renderMarkdownPoC(`Inline \`${hostileCode}\`.\n\n\`\`\`html\n${hostileCode}\n\`\`\``, { mode: 'admin-preview' })
		const template = document.createElement('template')
		template.innerHTML = result.html
		const codeTexts = [...template.content.querySelectorAll('code')].map(code => code.textContent)

		expect(codeTexts).toEqual([hostileCode, hostileCode])
		expect(template.content.querySelector('script, iframe, svg')).toBeNull()
		for (const element of template.content.querySelectorAll('*')) {
			for (const attribute of element.attributes) {
				expect(attribute.name.toLowerCase()).not.toMatch(/^on/)
			}
		}
	})
})

describe('M3 Unit: client update safe-to-malicious', () => {
	const fixture = markdownFixtures.find(f => f.id === 'security-client-update-safe-to-malicious')!
	it('safe content from updateFrom is preserved after update to malicious', () => {
		const safeResult = renderMarkdownPoC(fixture.updateFrom!, { mode: fixture.mode })
		const maliciousResult = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })

		expect(maliciousResult.html).toContain('Safe heading')
		expect(hasLiveElement(maliciousResult.html, 'script')).toBe(false)
		expect(hasDangerousUrlAttribute(maliciousResult.html)).toBe(false)
		expect(maliciousResult.warnings.some(w => w.code === 'CLIENT_UPDATE_SANITIZED')).toBe(true)
	})
})

describe('M3 Unit: malformed input produces local fallback', () => {
	const fixture = markdownFixtures.find(f => f.id === 'security-malformed-local-fallback')!
	it('malformed markdown produces local-fallback outcome', () => {
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		expect(result.outcome).toBe('local-fallback')
		expect(result.warnings.some(w => w.code === 'LOCAL_FALLBACK')).toBe(true)
		expect(result.html).toContain('Keep this heading')
		expect(hasLiveElement(result.html, 'not-closed')).toBe(false)
	})
})
