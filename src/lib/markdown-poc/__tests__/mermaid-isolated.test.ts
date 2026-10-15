import { describe, expect, it } from 'vitest'

import { renderIsolatedMermaidSvg } from '../mermaid'
import { renderMarkdownPoC } from '../render-poc'
import { parseHtml } from './dom-contract'

const allowedElements = new Set(['svg', 'defs', 'marker', 'path', 'g', 'rect', 'text', 'tspan', 'polygon', 'circle', 'line', 'title', 'desc'])
const allowedAttributes = new Set([
	'aria-roledescription',
	'class',
	'data-poc-mermaid',
	'd',
	'fill',
	'height',
	'id',
	'marker-end',
	'markerHeight',
	'marker-start',
	'markerWidth',
	'orient',
	'points',
	'preserveaspectratio',
	'refX',
	'refY',
	'role',
	'rx',
	'ry',
	'stroke',
	'stroke-width',
	'text-anchor',
	'transform',
	'viewBox',
	'width',
	'x',
	'x1',
	'x2',
	'y',
	'y1',
	'y2',
	'xmlns'
])

describe('Mermaid-01 final isolated SVG contract', () => {
	it('renders a bounded SVG with only the approved structure for a synthetic flowchart', () => {
		const result = renderMarkdownPoC('```mermaid\nflowchart LR\nA[Start] --> B[End]\n```', { mode: 'public' })
		const svg = parseHtml(result.html).querySelector('svg[data-poc-mermaid]')

		expect(svg).not.toBeNull()
		if (!svg) return
		expect(svg.namespaceURI).toBe('http://www.w3.org/2000/svg')
		expect(svg.querySelector('foreignObject, script, style, a, image, use, iframe, animate, set')).toBeNull()
		expect(svg.querySelector('[href], [xlink\\:href], [src], [style], [onload], [onerror], [onclick]')).toBeNull()
		for (const element of [svg, ...svg.querySelectorAll('*')]) {
			expect(allowedElements.has(element.tagName.toLowerCase())).toBe(true)
			for (const attribute of element.attributes) {
				expect(allowedAttributes.has(attribute.name)).toBe(true)
				if (attribute.name === 'id') expect(attribute.value).toMatch(/^poc-mermaid-[a-z0-9-]+$/)
				if (attribute.name === 'marker-start' || attribute.name === 'marker-end') expect(attribute.value).toMatch(/^url\(#poc-mermaid-[a-z0-9-]+\)$/)
			}
		}
	})

	it('rejects hostile Mermaid source to exact local inert text while preserving safe neighbours and TOC', () => {
		const source = 'flowchart LR\nA[<img src=x onerror="window.__markdownPocXss = true">] --> B'
		const result = renderMarkdownPoC(`# Safe Mermaid\n\n\`\`\`mermaid\n${source}\n\`\`\``, { mode: 'admin-preview' })
		const document = parseHtml(result.html)

		expect(result.outcome).toBe('local-fallback')
		expect(document.querySelector('h1')?.textContent).toBe('Safe Mermaid')
		expect(result.toc).toEqual([{ id: 'safe-mermaid', text: 'Safe Mermaid', level: 1 }])
		expect(document.querySelector('code[data-poc-inert="mermaid"]')?.textContent).toBe(source)
		expect(document.querySelector('script, foreignObject, [onerror], [href^="javascript:"]')).toBeNull()
		expect(result.warnings.map(warning => warning.code)).toContain('LOCAL_FALLBACK')
	})

	it('builds the finite final SVG schema itself, including isolated fragment ids', () => {
		const output = renderIsolatedMermaidSvg('flowchart LR\nA[Start] --> B[End]')

		expect(output).not.toBeNull()
		expect(output).toContain('data-poc-mermaid="rendered"')
		expect(output).toMatch(/id="poc-mermaid-[a-z0-9]+-arrow"/)
		expect(output).toMatch(/marker-end="url\(#poc-mermaid-[a-z0-9]+-arrow\)"/)
		expect(output).not.toContain('<style')
		expect(renderIsolatedMermaidSvg('flowchart LR\nA[<img src=x>] --> B')).toBeNull()
	})
})
