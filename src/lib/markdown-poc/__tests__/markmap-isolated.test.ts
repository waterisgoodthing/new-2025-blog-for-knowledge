import { describe, expect, it } from 'vitest'

import { renderMarkdownPoC } from '../render-poc'
import { parseHtml } from './dom-contract'

describe('Markmap-01 isolated final SVG contract', () => {
	it('requires a finite static SVG mind-map for safe Markdown headings', () => {
		const result = renderMarkdownPoC('```markmap\n# Root\n## Child\n```', { mode: 'public' })
		const svg = parseHtml(result.html).querySelector('svg[data-poc-markmap="rendered"]')

		expect(svg).not.toBeNull()
		expect(result.outcome).toBe('allow')
		expect(result.warnings).toEqual([])
		if (!svg) return
		expect(svg.namespaceURI).toBe('http://www.w3.org/2000/svg')
		expect(svg.querySelector('foreignObject, script, style, a, image, use, iframe, animate, set')).toBeNull()
		expect(svg.querySelector('[href], [xlink\\:href], [src], [style], [onload], [onerror], [onclick]')).toBeNull()
		expect(svg.textContent).toContain('Root')
		expect(svg.textContent).toContain('Child')
	})

	it('requires hostile link-like source to retain exact local fallback while preserving safe neighbours and TOC', () => {
		const source = '# <a href="javascript:alert(1)">Root</a>\n## Child'
		const result = renderMarkdownPoC(`# Safe Markmap\n\n\`\`\`markmap\n${source}\n\`\`\``, { mode: 'admin-preview' })
		const document = parseHtml(result.html)

		expect(result.outcome).toBe('local-fallback')
		expect(result.toc).toEqual([{ id: 'safe-markmap', text: 'Safe Markmap', level: 1 }])
		expect(document.querySelector('code[data-poc-inert="markmap"]')?.textContent).toBe(source)
		expect(document.querySelector('svg[data-poc-markmap], script, a, [href], [onerror]')).toBeNull()
		expect(result.warnings.map(warning => warning.code)).toContain('LOCAL_FALLBACK')
	})
})
