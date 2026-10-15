import { describe, expect, it } from 'vitest'
import katex from 'katex'

import { getAdapterDecision } from '../adapter-decisions'
import { markdownFixtures } from '../fixtures'
import { renderMarkdownPoC } from '../render-poc'
import { parseHtml } from './dom-contract'

describe('M5.3 Math adapter decision', () => {
	it('observes KaTeX final HTML before declining to enable it', () => {
		const fragment = parseHtml(katex.renderToString('E = mc^2', { displayMode: true, output: 'html', throwOnError: true, trust: false }))

		expect([...fragment.querySelectorAll('*')].every(element => element.tagName === 'SPAN')).toBe(true)
		expect(fragment.querySelector('[href], [src], [xlink\\:href], [onload], [onerror]')).toBeNull()
		expect(fragment.querySelector('[style]')).not.toBeNull()
	})

	it('keeps malformed Math source exact in its parsed local fallback', () => {
		const fixture = markdownFixtures.find(item => item.id === 'special-math-malformed')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })
		const decision = getAdapterDecision('math')

		expect(decision.status).toBe('ENABLED_ISOLATED')
		expect(decision.reason).toContain('KaTeX')
		expect(parseHtml(result.html).querySelector('code[data-poc-inert="math"]')?.textContent).toBe('\\htmlClass{evil}{x}\\notARealCommand')
		expect(result.warnings.map(item => item.code)).toContain('LOCAL_FALLBACK')
	})
})

describe('M5.4 Mermaid adapter decision', () => {
	it('enables only the bounded PoC-owned SVG path and locally falls back for hostile source', () => {
		const fixture = markdownFixtures.find(item => item.id === 'special-mermaid-malicious')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })

		expect(getAdapterDecision('mermaid').status).toBe('ENABLED_ISOLATED')
		expect(getAdapterDecision('mermaid').reason).toContain('bounded static flowchart')
		expect(parseHtml(result.html).querySelector('code[data-poc-inert="mermaid"]')?.textContent).toBe(
			'flowchart LR\n  A[<img src=x onerror="window.__markdownPocXss = true">] --> B'
		)
		expect(result.warnings.map(item => item.code)).toContain('LOCAL_FALLBACK')
	})
})

describe('M5.5 Markmap adapter decision', () => {
	it('enables only the bounded static SVG path and locally falls back for link-like source', () => {
		const fixture = markdownFixtures.find(item => item.id === 'special-markmap-malicious')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })

		expect(getAdapterDecision('markmap').status).toBe('ENABLED_ISOLATED')
		expect(getAdapterDecision('markmap').reason).toContain('bounded heading tree')
		expect(parseHtml(result.html).querySelector('code[data-poc-inert="markmap"]')?.textContent).toBe('# <a href="javascript:alert(1)">Root</a>')
		expect(result.warnings.map(item => item.code)).toContain('LOCAL_FALLBACK')
	})
})

describe('M5.6 Chart adapter decision', () => {
	it('enables only bounded bar JSON and locally falls back for formatter-bearing input', () => {
		const fixture = markdownFixtures.find(item => item.id === 'special-chart-malicious-or-invalid')!
		const result = renderMarkdownPoC(fixture.markdown, { mode: fixture.mode })

		expect(getAdapterDecision('chart').status).toBe('ENABLED_ISOLATED')
		expect(parseHtml(result.html).querySelector('code[data-poc-inert="chart"]')?.textContent).toContain('"formatter":"window.__markdownPocXss = true"')
		expect(result.warnings.map(item => item.code)).toContain('LOCAL_FALLBACK')
	})
})
