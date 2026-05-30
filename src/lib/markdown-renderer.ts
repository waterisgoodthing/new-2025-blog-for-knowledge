import { marked } from 'marked'
import type { Tokens } from 'marked'

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

export async function renderMarkdown(markdown: string): Promise<MarkdownRenderResult> {
	// Load optional renderers first so they apply on the FIRST lex/parse pass.
	// (If we lex before registering extensions, math tokens won't ever be produced on a cold refresh.)
	const codeBlockMap = new Map<string, { html: string; original: string }>()
	const [shiki, katex] = await Promise.all([loadShiki(), loadKatex()])

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
			// Add data-code attribute with original code for copy functionality
			// Escape HTML entities for attribute value
			const escapedCode = escapeHtml(codeData.original)
			if (codeData.html) {
				// Shiki highlighted code
				return `<pre data-code="${escapedCode}">${codeData.html}</pre>`
			}
			// Fallback for failed highlighting
			return `<pre data-code="${escapedCode}"><code>${codeData.original}</code></pre>`
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
		const body = marked.parser(token.tokens) as string
		const firstLineMatch = body.match(/^<p[^>]*>\[!([A-Z]+)\]<\/p>/)
		if (firstLineMatch) {
			const type = firstLineMatch[1]
			const title = ALERT_TYPES[type]
			if (title) {
				const remaining = body.replace(/^<p[^>]*>\[![A-Z]+\]<\/p>\n?/, '')
				return `<div class="markdown-alert markdown-alert-${type.toLowerCase()}" data-alert="${type.toLowerCase()}"><p class="markdown-alert-title">${escapeHtml(title)}</p>${remaining}</div>\n`
			}
		}
		return `<blockquote>${body}</blockquote>\n`
	}

	const renderMath = (content: string, displayMode: boolean) => {
		if (!katex) {
			// Keep original delimiters if katex is not available
			return displayMode ? `$$${content}$$` : `$${content}$`
		}

		try {
			return katex.renderToString(content, {
				displayMode,
				throwOnError: false,
				output: 'html',
				strict: 'ignore'
			})
		} catch {
			return displayMode ? `$$${content}$$` : `$${content}$`
		}
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
			}
		]
	})

	// Pre-process with marked lexer first (after extensions are registered)
	const tokens = marked.lexer(markdown)

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

	return { html, toc }
}
