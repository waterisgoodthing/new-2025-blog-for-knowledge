/**
 * M5.1 shared final-output contract.
 *
 * jsdom verifies parsed HTML structure only. SVG/Canvas execution, events,
 * navigation, and downloads remain M6/G2 browser evidence.
 */

import { describe, expect, it } from 'vitest'

import { markdownFixtures, type MarkdownFixture } from '../fixtures'
import { renderMarkdownPoC } from '../render-poc'

const URL_ATTRIBUTES = ['href', 'src', 'xlink:href'] as const

function parsedOutput(html: string): DocumentFragment {
	const template = document.createElement('template')
	template.innerHTML = html
	return template.content
}

function fencedSource(fixture: MarkdownFixture): string {
	return fixture.markdown.split('\n').slice(1, -1).join('\n')
}

function mathSource(fixture: MarkdownFixture): string {
	return fixture.markdown.trim().slice(2, -2)
}

function assertNoExecutableDom(fragment: DocumentFragment): void {
	expect(fragment.querySelector('script, iframe, svg, foreignObject')).toBeNull()
	for (const element of fragment.querySelectorAll('*')) {
		for (const attribute of element.attributes) {
			expect(attribute.name.toLowerCase()).not.toMatch(/^on/)
		}
		for (const name of URL_ATTRIBUTES) {
			const value = element.getAttribute(name)
			if (value !== null) {
				expect(value.toLowerCase()).not.toMatch(/^(?:javascript|vbscript|data):/)
			}
		}
	}
}

describe('M5.1 shared final-output contract: inert text is exact parsed DOM text', () => {
	const specialFixtures = markdownFixtures.filter(
		fixture =>
			fixture.id.startsWith('special-') &&
			!fixture.id.startsWith('special-code-') &&
			fixture.id !== 'special-math-valid' &&
			fixture.id !== 'special-mermaid-valid' &&
			fixture.id !== 'special-markmap-valid' &&
			fixture.id !== 'special-chart-valid'
	)

	for (const fixture of specialFixtures) {
		it(`fixture "${fixture.id}" preserves decoded inert source and metadata`, () => {
			const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
			const fragment = parsedOutput(result.html)
			const code = fragment.querySelector('pre > code[data-poc-inert]')
			const expectedSource = fixture.id.startsWith('special-math-') ? mathSource(fixture) : fencedSource(fixture)

			expect(code).not.toBeNull()
			expect(code?.textContent).toBe(expectedSource)
			expect(result.outcome).toBe(fixture.expected.outcome)
			for (const warning of fixture.expected.warnings) {
				expect(result.warnings.some(item => item.code === warning)).toBe(true)
			}
			assertNoExecutableDom(fragment)
		})
	}
})
