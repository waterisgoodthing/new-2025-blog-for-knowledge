import { describe, expect, it } from 'vitest'

import { renderMarkdownPoC } from '../render-poc'
import { parseHtml } from './dom-contract'

describe('Chart-01 isolated Canvas contract', () => {
	it('requires a finite Canvas container for a safe JSON bar chart', () => {
		const result = renderMarkdownPoC('```chart\n{"type":"bar","xAxis":["A","B"],"series":[{"name":"Synthetic","data":[1,2]}]}\n```', { mode: 'public' })
		const canvas = parseHtml(result.html).querySelector('canvas[data-poc-chart="rendered"]')

		expect(canvas).not.toBeNull()
		expect(result.outcome).toBe('allow')
		expect(result.warnings).toEqual([])
		if (!canvas) return
		expect(canvas.getAttribute('width')).toBe('320')
		expect(canvas.getAttribute('height')).toBe('180')
		expect(canvas.hasAttribute('style')).toBe(false)
		expect(canvas.hasAttribute('onload')).toBe(false)
	})

	it('requires functions, formatter keys and HTML-like JSON values to retain exact local fallback', () => {
		const source = '{"type":"bar","xAxis":["A"],"series":[{"data":[1]}],"formatter":"window.__markdownPocXss = true"}'
		const result = renderMarkdownPoC(`# Safe Chart\n\n\`\`\`chart\n${source}\n\`\`\``, { mode: 'admin-preview' })
		const document = parseHtml(result.html)

		expect(result.outcome).toBe('local-fallback')
		expect(result.toc).toEqual([{ id: 'safe-chart', text: 'Safe Chart', level: 1 }])
		expect(document.querySelector('code[data-poc-inert="chart"]')?.textContent).toBe(source)
		expect(document.querySelector('canvas[data-poc-chart], script, [onerror], [href]')).toBeNull()
		expect(result.warnings.map(warning => warning.code)).toContain('LOCAL_FALLBACK')
	})
})
