import { describe, expect, it } from 'vitest'

import { getAdapterDecision } from '../adapter-decisions'
import { renderMarkdownPoC } from '../render-poc'

const MATH_CLASSES = new Set([
	'base',
	'katex',
	'katex-display',
	'katex-html',
	'mathnormal',
	'mord',
	'mrel',
	'mspace',
	'msupsub',
	'mtight',
	'pstrut',
	'reset-size6',
	'size3',
	'sizing',
	'strut',
	'vlist',
	'vlist-r',
	'vlist-t'
])

describe('M6.3 isolated Math final-output contract', () => {
	it('renders the smallest KaTeX subset through the PoC-owned span/class/attribute/style policy', () => {
		const result = renderMarkdownPoC('$$E = mc^2$$', { mode: 'public' })
		const template = document.createElement('template')
		template.innerHTML = result.html

		expect(getAdapterDecision('math').status).toBe('ENABLED_ISOLATED')
		expect(result.outcome).toBe('allow')
		expect(template.content.querySelector('[data-poc-math="katex"]')).not.toBeNull()
		expect(template.content.querySelector('pre > code[data-poc-inert="math"]')).toBeNull()
		for (const element of template.content.querySelectorAll('*')) {
			expect(element.tagName).toBe('SPAN')
			for (const attribute of element.attributes) {
				expect(['class', 'style', 'aria-hidden', 'data-poc-math']).toContain(attribute.name)
				expect(attribute.name).not.toMatch(/^on/i)
			}
			for (const className of element.classList) expect(MATH_CLASSES.has(className)).toBe(true)
			const style = element.getAttribute('style')
			if (style !== null) expect(style).toMatch(/^(?:(?:height|margin-right|top):(?:-?[0-9]+(?:\.[0-9]+)?em);)+$/)
		}
		expect(template.content.querySelector('[href], [src], [xlink\\:href], script, svg, foreignObject')).toBeNull()
	})

	it.each([String.raw`\htmlClass{evil}{x}`, String.raw`\href{javascript:alert(1)}{x}`, String.raw`\notARealCommand`])(
		'locally falls back when KaTeX rejects or exceeds the enabled subset: %s',
		source => {
			const result = renderMarkdownPoC(`$$${source}$$`, { mode: 'admin-preview' })
			const template = document.createElement('template')
			template.innerHTML = result.html

			expect(result.outcome).toBe('local-fallback')
			expect(result.warnings.map(warning => warning.code)).toContain('LOCAL_FALLBACK')
			expect(template.content.querySelector('pre > code[data-poc-inert="math"]')?.textContent).toBe(source)
			expect(template.content.querySelector('[href], [src], [xlink\\:href], [onload], [onerror], script, svg, foreignObject')).toBeNull()
		}
	)
})
