/**
 * Isolated synthetic contract data for the Markdown security PoC.
 * Production code must not import this module.
 */

export const markdownRenderModes = ['public', 'admin-preview'] as const
export type MarkdownRenderMode = (typeof markdownRenderModes)[number]

export const markdownFixtureOutcomes = ['allow', 'strip', 'inert', 'warn', 'local-fallback'] as const
export type MarkdownFixtureOutcome = (typeof markdownFixtureOutcomes)[number]

export const markdownWarningCodes = [
	'RAW_HTML_STRIPPED',
	'UNSAFE_TAG_STRIPPED',
	'EVENT_HANDLER_STRIPPED',
	'UNSAFE_URL_STRIPPED',
	'UNSAFE_SVG_STRIPPED',
	'MALFORMED_MARKDOWN',
	'CLIENT_UPDATE_SANITIZED',
	'SPECIAL_RENDERER_INERT',
	'LOCAL_FALLBACK'
] as const
export type MarkdownWarningCode = (typeof markdownWarningCodes)[number]

export type MarkdownFixtureExpectation = {
	outcome: MarkdownFixtureOutcome
	warnings: readonly MarkdownWarningCode[]
	/** Elements or properties that must remain observable in renderable content. */
	contains?: readonly string[]
	/** Content which must not be emitted into the final HTML/SVG/DOM. */
	absent?: readonly string[]
	/** Stable heading ids expected from the PoC's table-of-contents contract. */
	toc?: readonly { id: string; text: string; level: number }[]
	/** Enabled special renderers need an independently validated final DOM/SVG boundary. */
	finalOutput?: 'must-validate' | 'inert-until-validated'
}

export type MarkdownFixture = {
	id: string
	mode: MarkdownRenderMode
	markdown: string
	expected: MarkdownFixtureExpectation
	/** Defines a safe-to-malicious client update in a single test case. */
	updateFrom?: string
}

export const markdownFixtures: readonly MarkdownFixture[] = [
	{
		id: 'security-raw-html-event-attribute',
		mode: 'public',
		markdown: '<img src="https://example.test/pixel.png" onerror="window.__markdownPocXss = true">',
		expected: { outcome: 'strip', warnings: ['RAW_HTML_STRIPPED', 'EVENT_HANDLER_STRIPPED'], absent: ['<img', 'onerror', '__markdownPocXss'] }
	},
	{
		id: 'security-script-and-raw-html',
		mode: 'admin-preview',
		markdown: '<script>window.__markdownPocXss = true</script><b>not trusted</b>',
		expected: { outcome: 'strip', warnings: ['RAW_HTML_STRIPPED', 'UNSAFE_TAG_STRIPPED'], absent: ['<script', '__markdownPocXss', '<b>'] }
	},
	{
		id: 'security-iframe-srcdoc',
		mode: 'public',
		markdown: '<iframe srcdoc="<script>window.__markdownPocXss = true</script>" src="https://example.test"></iframe>',
		expected: { outcome: 'strip', warnings: ['RAW_HTML_STRIPPED', 'UNSAFE_TAG_STRIPPED'], absent: ['<iframe', 'srcdoc', '__markdownPocXss'] }
	},
	{
		id: 'security-svg-href-xlink-foreign-object',
		mode: 'admin-preview',
		markdown:
			'<svg><a href="javascript:alert(1)" xlink:href="javascript:alert(2)"><foreignObject><img onerror="window.__markdownPocXss = true"></foreignObject></a></svg>',
		expected: {
			outcome: 'strip',
			warnings: ['RAW_HTML_STRIPPED', 'UNSAFE_SVG_STRIPPED'],
			absent: ['<svg', 'xlink:href', 'foreignObject', 'javascript:', '__markdownPocXss']
		}
	},
	{
		id: 'security-link-dangerous-protocols',
		mode: 'public',
		markdown: '[js](javascript:alert(1)) [vb](vbscript:msgbox(1)) [data](data:text/html,<script>alert(1)</script>)',
		expected: { outcome: 'strip', warnings: ['UNSAFE_URL_STRIPPED'], absent: ['javascript:', 'vbscript:', 'data:text/html'] }
	},
	{
		id: 'security-image-dangerous-protocols',
		mode: 'admin-preview',
		markdown: '![js](javascript:alert(1)) ![vb](vbscript:msgbox(1)) ![data](data:image/svg+xml,<svg/onload=alert(1)>)',
		expected: { outcome: 'strip', warnings: ['UNSAFE_URL_STRIPPED'], absent: ['javascript:', 'vbscript:', 'data:image/svg+xml'] }
	},
	{
		id: 'security-url-entity-case-whitespace-control',
		mode: 'public',
		markdown: '[entity](j&#x61;vascript:alert(1)) [case](JaVaScRiPt:alert(1)) [space]( \u0000javascript:alert(1))',
		expected: { outcome: 'strip', warnings: ['UNSAFE_URL_STRIPPED'], absent: ['javascript:', 'JaVaScRiPt:', 'j&#x61;vascript:'] }
	},
	{
		id: 'security-client-update-safe-to-malicious',
		mode: 'admin-preview',
		updateFrom: '# Safe heading\n\nA safe paragraph.',
		markdown: '# Safe heading\n\n<script>window.__markdownPocXss = true</script>\n\n[bad](javascript:alert(1))',
		expected: {
			outcome: 'strip',
			warnings: ['RAW_HTML_STRIPPED', 'UNSAFE_URL_STRIPPED', 'CLIENT_UPDATE_SANITIZED'],
			contains: ['Safe heading'],
			absent: ['<script', 'javascript:', '__markdownPocXss'],
			toc: [{ id: 'safe-heading', text: 'Safe heading', level: 1 }]
		}
	},
	{
		id: 'security-malformed-local-fallback',
		mode: 'public',
		markdown: '# Keep this heading\n\n[broken](https://example.test\n\n<not-closed',
		expected: {
			outcome: 'local-fallback',
			warnings: ['MALFORMED_MARKDOWN', 'LOCAL_FALLBACK'],
			contains: ['Keep this heading'],
			absent: ['<not-closed'],
			toc: [{ id: 'keep-this-heading', text: 'Keep this heading', level: 1 }]
		}
	},
	{
		id: 'semantic-headings-stable-toc',
		mode: 'public',
		markdown: '# 安全标题\n\n## 第二节\n\n普通段落。',
		expected: {
			outcome: 'allow',
			warnings: [],
			contains: ['<h1', '<h2', '普通段落'],
			toc: [
				{ id: '安全标题', text: '安全标题', level: 1 },
				{ id: '第二节', text: '第二节', level: 2 }
			]
		}
	},
	{
		id: 'semantic-paragraph-list-table',
		mode: 'admin-preview',
		markdown: '普通段落。\n\n- 第一项\n- 第二项\n\n| 列 | 值 |\n| --- | --- |\n| A | B |',
		expected: { outcome: 'allow', warnings: [], contains: ['<p>', '<ul>', '<li>', '<table>', '<th>', '<td>'] }
	},
	{
		id: 'semantic-safe-links-relative-anchor-mail',
		mode: 'public',
		markdown: '[safe](https://example.test/docs) [relative](./guide) [anchor](#section) [mail](mailto:reader@example.test)',
		expected: { outcome: 'allow', warnings: [], contains: ['https://example.test/docs', './guide', '#section', 'mailto:reader@example.test'] }
	},
	{
		id: 'semantic-safe-image-inline-and-fenced-code',
		mode: 'admin-preview',
		markdown: '![Diagram](https://example.test/diagram.png)\n\nUse `const value = 1` safely.\n\n```ts\nconst value = 1\n```',
		expected: { outcome: 'allow', warnings: [], contains: ['https://example.test/diagram.png', 'Diagram', '<code>', 'const value = 1'] }
	},
	{
		id: 'special-code-valid',
		mode: 'public',
		markdown: '```js\nconsole.log("safe code")\n```',
		expected: { outcome: 'allow', warnings: [], contains: ['console.log', 'safe code'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-code-hostile-text-is-inert',
		mode: 'admin-preview',
		markdown: '```html\n<script>window.__markdownPocXss = true</script>\n```',
		expected: { outcome: 'allow', warnings: [], contains: ['window.__markdownPocXss'], absent: ['<script>'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-math-valid',
		mode: 'admin-preview',
		markdown: '$$E = mc^2$$',
		expected: { outcome: 'allow', warnings: [], contains: ['data-poc-math="katex"'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-math-malformed',
		mode: 'public',
		markdown: '$$\\htmlClass{evil}{x}\\notARealCommand$$',
		expected: { outcome: 'local-fallback', warnings: ['LOCAL_FALLBACK'], contains: ['notARealCommand'], finalOutput: 'inert-until-validated' }
	},
	{
		id: 'special-mermaid-valid',
		mode: 'public',
		markdown: '```mermaid\nflowchart LR\n  A[Start] --> B[End]\n```',
		expected: { outcome: 'allow', warnings: [], contains: ['data-poc-mermaid="rendered"'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-mermaid-malicious',
		mode: 'admin-preview',
		markdown: '```mermaid\nflowchart LR\n  A[<img src=x onerror="window.__markdownPocXss = true">] --> B\n```',
		expected: { outcome: 'local-fallback', warnings: ['LOCAL_FALLBACK'], absent: ['onerror', '__markdownPocXss'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-markmap-valid',
		mode: 'public',
		markdown: '```markmap\n# Root\n## Child\n```',
		expected: { outcome: 'allow', warnings: [], contains: ['data-poc-markmap="rendered"'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-markmap-malicious',
		mode: 'admin-preview',
		markdown: '```markmap\n# <a href="javascript:alert(1)">Root</a>\n```',
		expected: { outcome: 'local-fallback', warnings: ['LOCAL_FALLBACK'], absent: ['javascript:'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-chart-valid',
		mode: 'public',
		markdown: '```chart\n{"type":"bar","xAxis":["A","B"],"series":[{"name":"Synthetic","data":[1,2]}]}\n```',
		expected: { outcome: 'allow', warnings: [], contains: ['data-poc-chart="rendered"'], finalOutput: 'must-validate' }
	},
	{
		id: 'special-chart-malicious-or-invalid',
		mode: 'admin-preview',
		markdown: '```chart\n{"type":"bar","xAxis":["A"],"series":[{"data":[1]}],"formatter":"window.__markdownPocXss = true"}\n```',
		expected: { outcome: 'local-fallback', warnings: ['LOCAL_FALLBACK'], absent: ['__markdownPocXss'], finalOutput: 'must-validate' }
	}
] as const

export const markdownFixturesById: ReadonlyMap<string, MarkdownFixture> = new Map(markdownFixtures.map(fixture => [fixture.id, fixture]))
