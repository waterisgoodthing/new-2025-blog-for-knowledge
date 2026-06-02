import type { Tokens } from 'marked'

let markedModule: typeof import('marked') | null = null

async function loadMarked() {
	if (markedModule) return markedModule
	const mod = await import('marked')
	markedModule = mod
	return mod
}

export type TocItem = { id: string; text: string; level: number }

export interface MarkdownRenderResult {
	html: string
	toc: TocItem[]
}

export function slugify(text: string): string {
	return text
		.toLowerCase()
		.replace(/[^a-z0-9\u4e00-\u9fa5\s-]/g, '')
		.trim()
		.replace(/\s+/g, '-')
}

function escapeHtml(text: string): string {
	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;')
}

function stripAlertPrefix(tokens: any[], _type: string): any[] {
	const first = tokens[0]
	if (!first || first.type !== 'paragraph') return tokens

	const inlineTokens = first.tokens
	if (!inlineTokens || inlineTokens.length === 0) return tokens

	const firstInline = inlineTokens[0]
	if (!firstInline?.text) return tokens

	const alertTagMatch = firstInline.text.match(/^\[![A-Z]+\](?:\s*\n?\s*)?/)
	if (!alertTagMatch) return tokens

	const remainingText = firstInline.text.slice(alertTagMatch[0].length)

	if (!remainingText && inlineTokens.length === 1) {
		return tokens.slice(1)
	}

	const newFirstInline = { ...firstInline, text: remainingText || '' }
	const newParagraph = {
		...first,
		tokens: [newFirstInline, ...inlineTokens.slice(1)],
	}
	return [newParagraph, ...tokens.slice(1)]
}

const ALLOWED_PROTOCOLS = ['http:', 'https:', 'mailto:']

function isAllowedUrl(url: string): boolean {
	if (!url) return false
	if (url.startsWith('/') || url.startsWith('./') || url.startsWith('#')) return true
	try {
		const u = new URL(url)
		return ALLOWED_PROTOCOLS.includes(u.protocol)
	} catch {
		return /^[a-z][a-z0-9+\-.]*:/i.test(url) === false
	}
}

// Lazy load shiki to handle environments where it's not available (e.g., Cloudflare Workers)
let shikiModule: typeof import('shiki') | null = null
let shikiLoadAttempted = false

async function loadShiki() {
	if (shikiLoadAttempted) {
		return shikiModule
	}
	shikiLoadAttempted = true

	try {
		shikiModule = await import('shiki')
		return shikiModule
	} catch (error) {
		console.warn('Failed to load shiki module:', error)
		return null
	}
}

// Lazy load katex to handle environments where it's not available (e.g., Cloudflare Workers)
let katexModule: typeof import('katex') | null = null
let katexLoadAttempted = false

async function loadKatex() {
	if (katexModule) return katexModule
	if (katexLoadAttempted) return null
	katexLoadAttempted = true

	try {
		// katex is published as CJS; depending on bundler/runtime the dynamic import
		// may return either the exports object directly or as `default`.
		const mod: any = await import('katex')
		katexModule = (mod?.default ?? mod) as any
		return katexModule
	} catch (error) {
		console.warn('Failed to load katex module:', error)
		return null
	}
}

const ALERT_TYPES: Record<string, string> = {
	NOTE: '注意',
	TIP: '技巧',
	WARNING: '警告',
	CAUTION: '危险',
	IMPORTANT: '重要',
}

const COLOR_PALETTE: Record<string, string> = {
	red: '#ef4444',
	blue: '#3b82f6',
	green: '#10b981',
	yellow: '#f59e0b',
	purple: '#8b5cf6',
	orange: '#f97316',
	gray: '#6b7280',
	pink: '#ec4899',
}

export async function renderMarkdown(markdown: string): Promise<MarkdownRenderResult> {
	// Load optional renderers first so they apply on the FIRST lex/parse pass.
	// (If we lex before registering extensions, math tokens won't ever be produced on a cold refresh.)
	const codeBlockMap = new Map<string, { html: string; original: string }>()
	const [markedMod, shiki, katex] = await Promise.all([loadMarked(), loadShiki(), loadKatex()])
	const { marked } = markedMod

	// Render HTML with heading ids
	const renderer = new marked.Renderer()

	// T-06: Drop all user raw HTML
	renderer.html = () => ''

	// T-06: Link protocol whitelist
	renderer.link = (token: Tokens.Link) => {
		const href = token.href || ''
		if (!isAllowedUrl(href)) {
			return `<span>${escapeHtml(token.text)}</span>`
		}
		return `<a href="${escapeHtml(href)}"${token.title ? ` title="${escapeHtml(token.title)}"` : ''}>${token.text}</a>`
	}

	// T-06: Image src protocol whitelist
	renderer.image = (token: Tokens.Image) => {
		const src = token.href || ''
		if (!isAllowedUrl(src)) {
			return `<span>[图片: 协议不安全]</span>`
		}
		return `<img src="${escapeHtml(src)}" alt="${escapeHtml(token.text || '')}"${token.title ? ` title="${escapeHtml(token.title)}"` : ''} loading="lazy" />`
	}

	renderer.heading = (token: Tokens.Heading) => {
		const id = slugify(token.text || '')
		return `<h${token.depth} id="${id}">${token.text}</h${token.depth}>`
	}

	renderer.code = (token: Tokens.Code) => {
		// Check if this code block was pre-processed
		const codeData = codeBlockMap.get(token.text)
		if (codeData) {
			const escapedCode = escapeHtml(codeData.original)
			const contentHtml = codeData.html || `<pre><code>${escapeHtml(codeData.original)}</code></pre>`
			return `<div class="ag-code-block" data-code="${escapedCode}">${contentHtml}</div><!--ag-code-block-end-->`
		}
		// Fallback to default (inline code, not code block)
		return `<code>${escapeHtml(token.text)}</code>`
	}

	renderer.listitem = (token: Tokens.ListItem) => {
		// Render inline markdown inside list items (e.g. links, emphasis)
		let inner = token.text
		let tokens = token.tokens

		if (token.task) tokens = tokens.slice(1)
		inner = marked.parser(tokens) as string

		if (token.task) {
			const checkbox = token.checked ? '<input type="checkbox" checked disabled />' : '<input type="checkbox" disabled />'
			return `<li class="task-list-item">${checkbox} ${inner}</li>\n`
		}

		return `<li>${inner}</li>\n`
	}

	// T-07: GitHub Alerts blockquote
	renderer.blockquote = (token: Tokens.Blockquote) => {
		const firstToken = token.tokens?.[0] as any
		if (firstToken?.type === 'paragraph') {
			const inlineTokens = firstToken.tokens
			const firstText = inlineTokens?.[0]?.text || firstToken.text || ''
			const alertMatch = firstText.match(/^\[!([A-Z]+)\]/)
			if (alertMatch) {
				const type = alertMatch[1]
				const title = ALERT_TYPES[type]
				if (title) {
					const remainingTokens = stripAlertPrefix(token.tokens as any[], type)
					const body = marked.parser(remainingTokens) as string
					return `<div class="markdown-alert markdown-alert-${type.toLowerCase()}" data-alert="${type.toLowerCase()}"><p class="markdown-alert-title">${escapeHtml(title)}</p>${body}</div>\n`
				}
			}
		}

		const body = marked.parser(token.tokens) as string
		const fallbackMatch = body.match(/^<p[^>]*>\[!([A-Z]+)\]/)
		if (fallbackMatch) {
			const type = fallbackMatch[1]
			const title = ALERT_TYPES[type]
			if (title) {
				let remaining = body
				const tagOnlyPattern = /^<p[^>]*>\[![A-Z]+\]<\/p>\n?/
				const tagWithContentPattern = /^<p[^>]*>\[![A-Z]+\](?:<br\s*\/?>|\s)*/
				if (tagOnlyPattern.test(body)) {
					remaining = body.replace(tagOnlyPattern, '')
				} else {
					remaining = body.replace(tagWithContentPattern, '<p>')
				}
				return `<div class="markdown-alert markdown-alert-${type.toLowerCase()}" data-alert="${type.toLowerCase()}"><p class="markdown-alert-title">${escapeHtml(title)}</p>${remaining}</div>\n`
			}
		}
		return `<blockquote>${body}</blockquote>\n`
	}

	const renderMath = (content: string, displayMode: boolean) => {
		const tag = displayMode ? 'div' : 'span'
		let html = ''
		if (!katex) {
			html = displayMode ? `$$${content}$$` : `$${content}$`
		} else {
			try {
				html = katex.renderToString(content, {
					displayMode,
					throwOnError: false,
					output: 'html',
					strict: 'ignore'
				})
			} catch {
				html = displayMode ? `$$${content}$$` : `$${content}$`
			}
		}
		return `<${tag} class="ag-math-container"><!--ag-math-start-->${html}<!--ag-math-end--></${tag}>`
	}

	// Register extensions BEFORE lexing so math gets tokenized on cold refresh.
	marked.use({
		renderer,
		extensions: [
			// Block math: $$ ... $$
			{
				name: 'mathBlock',
				level: 'block',
				start(src: string) {
					return src.indexOf('$$')
				},
				tokenizer(src: string) {
					const match = src.match(/^\$\$([\s\S]+?)\$\$(?:\n+|$)/)
					if (!match) return
					return {
						type: 'mathBlock',
						raw: match[0],
						text: match[1].trim()
					} as any
				},
				renderer(token: any) {
					return `${renderMath(token.text || '', true)}\n`
				}
			},
			// Inline math: $ ... $
			{
				name: 'mathInline',
				level: 'inline',
				start(src: string) {
					const idx = src.indexOf('$')
					return idx === -1 ? undefined : idx
				},
				tokenizer(src: string) {
					// Avoid $$ (block) and escaped dollars
					if (src.startsWith('$$')) return
					if (src.startsWith('\\$')) return

					const match = src.match(/^\$([^\n$]+?)\$/)
					if (!match) return

					const inner = match[1]
					// Heuristic: require some non-space content
					if (!inner || !inner.trim()) return

					return {
						type: 'mathInline',
						raw: match[0],
						text: inner.trim()
					} as any
				},
				renderer(token: any) {
					return renderMath(token.text || '', false)
				}
			},
			// T-08: Highlight ==text==
			{
				name: 'highlight',
				level: 'inline',
				start(src: string) {
					return src.indexOf('==')
				},
				tokenizer(src: string) {
					const match = src.match(/^==([^=\n]+)==/)
					if (!match) return
					return {
						type: 'highlight',
						raw: match[0],
						text: match[1]
					} as any
				},
				renderer(token: any) {
					return `<mark>${token.text || ''}</mark>`
				}
			},
			// T-303: Color {color|text}
			{
				name: 'textColor',
				level: 'inline',
				start(src: string) {
					return src.indexOf('{')
				},
				tokenizer(src: string) {
					const match = src.match(/^\{([a-z]+)\|([^}]+)\}/)
					if (!match) return
					const colorKey = match[1]
					if (!COLOR_PALETTE[colorKey]) return
					return {
						type: 'textColor',
						raw: match[0],
						color: colorKey,
						text: match[2]
					} as any
				},
				renderer(token: any) {
					const hex = COLOR_PALETTE[token.color] || '#000000'
					return `<span style="color:${hex}">${token.text || ''}</span>`
				}
			},
			// T-19: Footnote reference [^id]
			{
				name: 'footnoteRef',
				level: 'inline',
				start(src: string) {
					return src.indexOf('[^')
				},
				tokenizer(src: string) {
					const match = src.match(/^\[\^([a-zA-Z0-9\u4e00-\u9fa5_-]+)\]/)
					if (!match) return
					return {
						type: 'footnoteRef',
						raw: match[0],
						id: match[1]
					} as any
				},
				renderer(token: any) {
					const id = slugify(token.id || '')
					if (!footnoteDefs.has(id)) return token.raw
					const index = footnoteOrder.indexOf(id) + 1
					return `<sup><a href="#fn-${id}" id="fnref-${id}">${index}</a></sup>`
				}
			},
			// T-301: Compare block :::compare ... :::
			{
				name: 'compareBlock',
				level: 'block',
				start(src: string) {
					return src.indexOf(':::compare')
				},
				tokenizer(src: string) {
					const match = src.match(/^:::compare\n([\s\S]*?)\n:::(?:\n|$)/)
					if (!match) return
					return {
						type: 'compareBlock',
						raw: match[0],
						text: match[1]
					} as any
				},
				renderer(token: any) {
					const lines = (token.text || '').split('\n')
					let title = ''
					let leftLabel = 'A'
					let rightLabel = 'B'
					const items: string[] = []
					for (const line of lines) {
						const titleMatch = line.match(/^title:\s*(.+)/)
						const leftMatch = line.match(/^left:\s*(.+)/)
						const rightMatch = line.match(/^right:\s*(.+)/)
						const itemMatch = line.match(/^-\s+(.+)/)
						if (titleMatch) title = escapeHtml(titleMatch[1].trim())
						else if (leftMatch) leftLabel = escapeHtml(leftMatch[1].trim())
						else if (rightMatch) rightLabel = escapeHtml(rightMatch[1].trim())
						else if (itemMatch) items.push(itemMatch[1].trim())
					}
					const mid = Math.ceil(items.length / 2)
					const leftItems = items.slice(0, mid).map(i => `<li>${escapeHtml(i)}</li>`).join('')
					const rightItems = items.slice(mid).map(i => `<li>${escapeHtml(i)}</li>`).join('')
					const titleHtml = title ? `<div class="compare-title">${title}</div>` : ''
					return `<div class="compare-block">${titleHtml}<div class="compare-grid"><div class="compare-col"><div class="compare-label">${leftLabel}</div><ul>${leftItems}</ul></div><div class="compare-col"><div class="compare-label">${rightLabel}</div><ul>${rightItems}</ul></div></div></div>\n`
				}
			}
		]
	})

	// T-19: Collect footnote definitions before lexing
	const footnoteDefs = new Map<string, string>()
	const footnoteOrder: string[] = []
	const footnoteDefRegex = /^\[\^([a-zA-Z0-9\u4e00-\u9fa5_-]+)\]:\s*(.+)$/gm
	let fnMatch: RegExpExecArray | null
	let cleanMarkdown = markdown
	while ((fnMatch = footnoteDefRegex.exec(markdown)) !== null) {
		const id = slugify(fnMatch[1])
		if (!footnoteDefs.has(id)) {
			footnoteDefs.set(id, fnMatch[2].trim())
			footnoteOrder.push(id)
		}
		cleanMarkdown = cleanMarkdown.replace(fnMatch[0], '')
	}

	// Pre-process with marked lexer first (after extensions are registered)
	const tokens = marked.lexer(cleanMarkdown)

	// Extract TOC from parsed tokens (this correctly skips code blocks)
	const toc: TocItem[] = []
	function extractHeadings(tokenList: typeof tokens) {
		for (const token of tokenList) {
			if (token.type === 'heading' && token.depth <= 3) {
				// Use the parsed text (markdown syntax like links/code already stripped)
				const text = token.text
				const id = slugify(text)
				toc.push({ id, text, level: token.depth })
			}
			// Recursively check nested tokens (e.g., in blockquotes, lists)
			if ('tokens' in token && token.tokens) {
				extractHeadings(token.tokens as typeof tokens)
			}
		}
	}
	extractHeadings(tokens)

	// Pre-process code blocks with Shiki
	for (const token of tokens) {
		if (token.type === 'code') {
			const codeToken = token as Tokens.Code
			const originalCode = codeToken.text
			const key = `__SHIKI_CODE_${codeBlockMap.size}__`

			if (codeToken.lang === 'mermaid') {
				// T-20: Mermaid placeholder (P3, but safe to prepare)
				const escaped = escapeHtml(originalCode)
				codeBlockMap.set(key, { html: `<div class="mermaid">${escaped}</div>`, original: originalCode })
				codeToken.text = key
			} else if (shiki) {
				try {
					const html = await shiki.codeToHtml(originalCode, {
						lang: codeToken.lang || 'text',
						theme: 'one-light'
					})
					codeBlockMap.set(key, { html, original: originalCode })
					codeToken.text = key
				} catch {
					// Keep original if highlighting fails
					codeBlockMap.set(key, { html: '', original: originalCode })
					codeToken.text = key
				}
			} else {
				// Fallback when shiki is not available
				codeBlockMap.set(key, { html: '', original: originalCode })
				codeToken.text = key
			}
		}
	}
	const html = (marked.parser(tokens) as string) || ''

	// T-19: Append footnotes section
	let finalHtml = html
	if (footnoteOrder.length > 0) {
		const footnotesHtml = footnoteOrder
			.map((id, i) => {
				const text = footnoteDefs.get(id) || ''
				return `<li id="fn-${id}">${escapeHtml(text)} <a href="#fnref-${id}">↩</a></li>`
			})
			.join('\n')
		finalHtml += `\n<section class="footnotes"><ol>${footnotesHtml}</ol></section>`
	}

	return { html: finalHtml, toc }
}
