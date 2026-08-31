import { describe, expect, it } from 'vitest'

import { renderMarkdownPoC } from '../render-poc'
import { parseHtml } from './dom-contract'

describe('SA-03 mixed special-adapter closure', () => {
	it('keeps three safe isolated outputs while one hostile block falls back locally with TOC and warnings intact', () => {
		const hostile = '# <a href="javascript:alert(1)">Bad</a>'
		const markdown = `# Mixed safety\n\n\`\`\`mermaid\nflowchart LR\nA[Start] --> B[End]\n\`\`\`\n\n\`\`\`markmap\n# Root\n## Child\n\`\`\`\n\n\`\`\`chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}]}\n\`\`\`\n\n\`\`\`markmap\n${hostile}\n\`\`\``
		const result = renderMarkdownPoC(markdown, { mode: 'admin-preview' })
		const document = parseHtml(result.html)

		expect(result.outcome).toBe('local-fallback')
		expect(result.toc).toEqual([{ id: 'mixed-safety', text: 'Mixed safety', level: 1 }])
		expect(document.querySelectorAll('svg[data-poc-mermaid="rendered"]')).toHaveLength(1)
		expect(document.querySelectorAll('svg[data-poc-markmap="rendered"]')).toHaveLength(1)
		expect(document.querySelectorAll('canvas[data-poc-chart="rendered"]')).toHaveLength(1)
		expect(document.querySelector('code[data-poc-inert="markmap"]')?.textContent).toBe(hostile)
		expect(result.warnings.map(warning => warning.code)).toEqual(['LOCAL_FALLBACK'])
		expect(document.querySelector('script, foreignObject, a, [href], [onerror]')).toBeNull()
	})

	it('uses the PoC-owned global fallback for a deterministic mixed-render failure', () => {
		const result = renderMarkdownPoC('```mermaid\nflowchart LR\nA --> B\n```\n\n```chart\n{}\n```', { mode: 'public', forceGlobalFailure: true })
		expect(result.outcome).toBe('local-fallback')
		expect(result.html).toContain('data-poc-global-fallback="true"')
		expect(result.html).not.toMatch(/<svg|<canvas|<script|<iframe/i)
	})
})
