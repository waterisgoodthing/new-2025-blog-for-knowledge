import { describe, expect, it } from 'vitest'

import { getAdapterDecision } from '../adapter-decisions'
import { renderMarkdownPoC } from '../render-poc'

describe('M6.4 Mermaid candidate boundary', () => {
	it('uses only the PoC-owned finite SVG boundary for accepted static flowcharts', () => {
		const result = renderMarkdownPoC('```mermaid\nflowchart LR\nA --> B\n```')

		expect(getAdapterDecision('mermaid').status).toBe('ENABLED_ISOLATED')
		expect(result.outcome).toBe('allow')
		expect(result.html).toContain('data-poc-mermaid="rendered"')
		expect(result.html).not.toMatch(/foreignObject|style=|href=|onerror=/)
	})
})

describe('M6.5 Markmap candidate boundary', () => {
	it('uses only the PoC-owned finite static SVG boundary for accepted heading trees', () => {
		const result = renderMarkdownPoC('```markmap\n# Root\n## Child\n```')

		expect(getAdapterDecision('markmap').status).toBe('ENABLED_ISOLATED')
		expect(result.outcome).toBe('allow')
		expect(result.html).toContain('data-poc-markmap="rendered"')
		expect(result.html).not.toMatch(/foreignObject|style=|href=|onerror=/)
	})
})

describe('M6.6 Chart candidate boundary', () => {
	it('uses only the PoC-owned bounded Canvas boundary for accepted bar JSON', () => {
		const result = renderMarkdownPoC('```chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}]}\n```')

		expect(getAdapterDecision('chart').status).toBe('ENABLED_ISOLATED')
		expect(result.outcome).toBe('allow')
		expect(result.html).toContain('data-poc-chart="rendered"')
		expect(result.html).not.toMatch(/formatter|onerror=|href=|style=/)
	})
})

describe('M6.7 local and global fallback closure', () => {
	it.each(['$$E = mc^2$$', '```mermaid\nA-->B\n```', '```markmap\n# Root\n```', '```chart\n{}\n```'])(
		'returns only the PoC-owned global inert error surface for a deterministic renderer failure: %s',
		markdown => {
			const result = renderMarkdownPoC(markdown, { mode: 'public', forceGlobalFailure: true })

			expect(result.outcome).toBe('local-fallback')
			expect(result.html).toContain('data-poc-global-fallback="true"')
			expect(result.html).not.toMatch(/<script|<svg|<canvas|<iframe/i)
		}
	)
})
