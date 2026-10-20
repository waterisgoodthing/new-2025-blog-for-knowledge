/**
 * Isolated, bounded Markdown renderer.
 *
 * `marked` is used only to produce tokens. This module owns every byte of
 * emitted HTML and intentionally does not use `marked.parse()` output.
 * Production code must not import this module.
 */

import { marked, type Token, type Tokens } from 'marked'

import { renderIsolatedChartCanvas } from './chart'
import type { MarkdownRenderMode } from './fixtures'
import { renderIsolatedMath } from './math'
import { renderIsolatedMarkmapSvg } from './markmap'
import { renderIsolatedMermaidSvg } from './mermaid'
import type { PoCOutcome, PoCRenderResult, PoCWarning, TocItem } from './types'

export interface PoCRenderOptions {
	mode: MarkdownRenderMode
	/** Test-only deterministic renderer-failure seam for the PoC global fallback. */
	forceGlobalFailure?: boolean
}

type RenderState = {
	warnings: PoCWarning[]
	stripped: boolean
	inert: boolean
	localFallback: boolean
	toc: TocItem[]
	headingIds: Map<string, number>
}

function addWarning(state: RenderState, code: PoCWarning['code'], message: string): void {
	if (!state.warnings.some(warning => warning.code === code)) {
		state.warnings.push({ code, message })
	}
}

function escapeHtml(value: string): string {
	return value.replace(/[&<>'"]/g, character => {
		const entities: Record<string, string> = {
			'&': '&amp;',
			'<': '&lt;',
			'>': '&gt;',
			"'": '&#39;',
			'"': '&quot;'
		}
		return entities[character]
	})
}

function decodeUrlEntities(value: string): string {
	const namedEntities: Record<string, string> = {
		'&colon;': ':',
		'&tab;': '\t',
		'&newline;': '\n'
	}
	return value
		.replace(/&#x([0-9a-f]+);?/gi, (_, hex: string) => String.fromCodePoint(Number.parseInt(hex, 16)))
		.replace(/&#([0-9]+);?/g, (_, decimal: string) => String.fromCodePoint(Number.parseInt(decimal, 10)))
		.replace(/&[a-z]+;/gi, entity => namedEntities[entity.toLowerCase()] ?? entity)
}

function canonicalUrl(value: string): string {
	let canonical = decodeUrlEntities(value).replace(/\\u([0-9a-f]{4})/gi, (_, hex: string) => String.fromCharCode(Number.parseInt(hex, 16)))
	for (let attempt = 0; attempt < 2; attempt += 1) {
		try {
			const decoded = decodeURIComponent(canonical)
			if (decoded === canonical) break
			canonical = decoded
		} catch {
			break
		}
	}
	return canonical.replace(/[\s\u0000-\u001f\u007f-\u009f]/g, '').toLowerCase()
}

function safeUrl(value: string): string | null {
	if (/[\u0000-\u001f\u007f-\u009f]/.test(value)) return null
	const canonical = canonicalUrl(value)
	const safeProtocol = /^(?:https?:|mailto:)/.test(canonical)
	const safeRelative = /^(?:\/(?!\/)|\.\.?\/|#|\?)/.test(canonical)
	return safeProtocol || safeRelative ? value.trim() : null
}

function textFromInline(tokens: readonly Token[] | undefined): string {
	return (tokens ?? [])
		.map(token => {
			switch (token.type) {
				case 'text':
				case 'escape':
				case 'codespan':
					return token.text
				case 'strong':
				case 'em':
				case 'del':
				case 'link':
					return textFromInline(token.tokens)
				case 'image':
					return token.text
				case 'br':
					return ' '
				default:
					return ''
			}
		})
		.join('')
}

function headingId(text: string, state: RenderState): string {
	const base =
		text
			.normalize('NFKC')
			.toLowerCase()
			.trim()
			.replace(/[^\p{L}\p{N}\s-]/gu, '')
			.replace(/[\s-]+/g, '-') || 'section'
	const occurrence = (state.headingIds.get(base) ?? 0) + 1
	state.headingIds.set(base, occurrence)
	return occurrence === 1 ? base : `${base}-${occurrence}`
}

function stripRawHtml(token: Token, state: RenderState): string {
	const text = 'text' in token && typeof token.text === 'string' ? token.text : token.raw
	state.stripped = true
	addWarning(state, 'RAW_HTML_STRIPPED', 'Removed raw HTML from untrusted Markdown.')
	if (/\s+on[a-z0-9_-]+\s*=/i.test(text)) {
		addWarning(state, 'EVENT_HANDLER_STRIPPED', 'Removed an event handler from raw HTML.')
	}
	if (/<svg\b|\b(?:xlink:href|foreignobject)\b/i.test(text)) {
		addWarning(state, 'UNSAFE_SVG_STRIPPED', 'Removed unsafe SVG markup.')
	} else if (/<(?:script|iframe)\b/i.test(text)) {
		addWarning(state, 'UNSAFE_TAG_STRIPPED', 'Removed a disallowed raw HTML element.')
	}
	return ''
}

function inertBlock(kind: string, text: string, state: RenderState): string {
	state.inert = true
	addWarning(state, 'SPECIAL_RENDERER_INERT', `Kept ${kind} as escaped inert text pending final-output validation.`)
	return `<pre><code data-poc-inert="${kind}">${escapeHtml(text)}</code></pre>`
}

function localMermaidFallback(text: string, state: RenderState): string {
	state.localFallback = true
	addWarning(state, 'LOCAL_FALLBACK', 'Rejected Mermaid input and kept the affected source as escaped local fallback text.')
	return `<pre><code data-poc-inert="mermaid">${escapeHtml(text)}</code></pre>`
}

function localMarkmapFallback(text: string, state: RenderState): string {
	state.localFallback = true
	addWarning(state, 'LOCAL_FALLBACK', 'Rejected Markmap input and kept the affected source as escaped local fallback text.')
	return `<pre><code data-poc-inert="markmap">${escapeHtml(text)}</code></pre>`
}

function localChartFallback(text: string, state: RenderState): string {
	state.localFallback = true
	addWarning(state, 'LOCAL_FALLBACK', 'Rejected Chart input and kept the affected source as escaped local fallback text.')
	return `<pre><code data-poc-inert="chart">${escapeHtml(text)}</code></pre>`
}

function renderMermaidBlock(source: string, state: RenderState): string {
	return renderIsolatedMermaidSvg(source) ?? localMermaidFallback(source, state)
}

function renderMarkmapBlock(source: string, state: RenderState): string {
	return renderIsolatedMarkmapSvg(source) ?? localMarkmapFallback(source, state)
}

function renderChartBlock(source: string, state: RenderState): string {
	return renderIsolatedChartCanvas(source) ?? localChartFallback(source, state)
}

function renderMathBlock(source: string, state: RenderState): string {
	const rendered = renderIsolatedMath(source)
	if (rendered !== null) return rendered
	state.localFallback = true
	addWarning(state, 'LOCAL_FALLBACK', 'Rejected Math output and kept the affected source as escaped local fallback text.')
	return `<pre><code data-poc-inert="math">${escapeHtml(source)}</code></pre>`
}

function hasMalformedMarkdown(markdown: string): boolean {
	return /\[[^\]\n]*\]\([^\)\n]*(?:\n|$)/.test(markdown) || /<[^>\n]*$/m.test(markdown)
}

function renderInline(tokens: readonly Token[] | undefined, state: RenderState): string {
	return (tokens ?? [])
		.map(token => {
			switch (token.type) {
				case 'text':
				case 'escape':
					return escapeHtml(token.text)
				case 'codespan':
					return `<code>${escapeHtml(token.text)}</code>`
				case 'strong':
					return `<strong>${renderInline(token.tokens, state)}</strong>`
				case 'em':
					return `<em>${renderInline(token.tokens, state)}</em>`
				case 'del':
					return `<del>${renderInline(token.tokens, state)}</del>`
				case 'br':
					return '<br>'
				case 'link': {
					const href = safeUrl(token.href)
					if (!href) {
						state.stripped = true
						addWarning(state, 'UNSAFE_URL_STRIPPED', 'Removed a link with an unsafe URL.')
						return renderInline(token.tokens, state)
					}
					return `<a href="${escapeHtml(href)}">${renderInline(token.tokens, state)}</a>`
				}
				case 'image': {
					const src = safeUrl(token.href)
					if (!src) {
						state.stripped = true
						addWarning(state, 'UNSAFE_URL_STRIPPED', 'Removed an image with an unsafe URL.')
						return escapeHtml(token.text)
					}
					return `<img src="${escapeHtml(src)}" alt="${escapeHtml(token.text)}">`
				}
				case 'html':
					return stripRawHtml(token, state)
				default:
					return escapeHtml(token.raw)
			}
		})
		.join('')
}

function renderTokens(tokens: Token[], state: RenderState): string {
	return tokens
		.map(token => {
			switch (token.type) {
				case 'space':
					return ''
				case 'paragraph':
					if (token.text.trim().startsWith('$$') && token.text.trim().endsWith('$$')) {
						return renderMathBlock(token.text.trim().slice(2, -2), state)
					}
					return `<p>${renderInline(token.tokens, state)}</p>`
				case 'heading': {
					const text = textFromInline(token.tokens)
					const id = headingId(text, state)
					state.toc.push({ id, text, level: token.depth })
					return `<h${token.depth} id="${escapeHtml(id)}">${renderInline(token.tokens, state)}</h${token.depth}>`
				}
				case 'blockquote':
					return `<blockquote>${renderTokens(token.tokens ?? [], state)}</blockquote>`
				case 'list': {
					const list = token as Tokens.List
					const tag = list.ordered ? 'ol' : 'ul'
					const start = list.ordered && typeof list.start === 'number' && list.start > 1 ? ` start="${list.start}"` : ''
					return `<${tag}${start}>${list.items.map(item => `<li>${renderTokens(item.tokens, state)}</li>`).join('')}</${tag}>`
				}
				case 'table': {
					const table = token as Tokens.Table
					const header = table.header.map(cell => `<th>${renderInline(cell.tokens, state)}</th>`).join('')
					const rows = table.rows.map(row => `<tr>${row.map(cell => `<td>${renderInline(cell.tokens, state)}</td>`).join('')}</tr>`).join('')
					return `<table><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table>`
				}
				case 'code': {
					const language = token.lang?.toLowerCase()
					if (language === 'mermaid') return renderMermaidBlock(token.text, state)
					if (language === 'markmap') return renderMarkmapBlock(token.text, state)
					if (language === 'chart') return renderChartBlock(token.text, state)
					return `<pre><code>${escapeHtml(token.text)}</code></pre>`
				}
				case 'html':
					return stripRawHtml(token, state)
				default:
					return `<p>${escapeHtml(token.raw)}</p>`
			}
		})
		.join('')
}

function outcomeFor(state: RenderState): PoCOutcome {
	if (state.localFallback) return 'local-fallback'
	if (state.inert) return 'inert'
	return state.stripped ? 'strip' : 'allow'
}

export function renderMarkdownPoC(markdown: string, options: PoCRenderOptions = { mode: 'public' }): PoCRenderResult {
	if (options.forceGlobalFailure) {
		return {
			html: '<pre data-poc-global-fallback="true"><code>Markdown rendering is safely unavailable.</code></pre>',
			toc: [],
			warnings: [{ code: 'LOCAL_FALLBACK', message: 'Used the PoC-owned safe global error surface after a renderer failure.' }],
			outcome: 'local-fallback'
		}
	}
	const state: RenderState = { warnings: [], stripped: false, inert: false, localFallback: false, toc: [], headingIds: new Map() }
	const malformed = hasMalformedMarkdown(markdown)
	if (malformed) {
		state.localFallback = true
		addWarning(state, 'MALFORMED_MARKDOWN', 'Malformed Markdown was safely reduced to local output.')
		addWarning(state, 'LOCAL_FALLBACK', 'Used a safe local fallback for the affected Markdown block.')
	}
	const tokens = marked.lexer(markdown, { async: false, gfm: true })
	const html = renderTokens(tokens, state)

	if (state.stripped && options.mode === 'admin-preview') {
		addWarning(state, 'CLIENT_UPDATE_SANITIZED', 'Applied the same untrusted-input policy during admin preview rendering.')
	}

	return {
		html,
		toc: state.toc,
		warnings: state.warnings,
		outcome: outcomeFor(state)
	}
}
