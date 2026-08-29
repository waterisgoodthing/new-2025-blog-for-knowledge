/**
 * Isolated KaTeX output boundary for the Markdown PoC.
 *
 * KaTeX is never trusted as an HTML policy. This module accepts only the
 * smallest output subset required by the M6.3 fixture and rejects everything
 * else before the renderer returns an HTML string to SSR or hydration.
 */

import katex from 'katex'

const ALLOWED_CLASSES = new Set([
	'base',
	'katex',
	'katex-display',
	'katex-html',
	'mathnormal',
	'mord',
	'mrel',
	'mspace',
	'msupsub',
	'mtight',
	'pstrut',
	'reset-size6',
	'size3',
	'sizing',
	'strut',
	'vlist',
	'vlist-r',
	'vlist-t'
])

const ALLOWED_STYLE_VALUES: Record<string, RegExp> = {
	height: /^(?:0|[0-9]+(?:\.[0-9]+)?)em$/,
	'margin-right': /^(?:0|[0-9]+(?:\.[0-9]+)?)em$/,
	top: /^-(?:0|[0-9]+(?:\.[0-9]+)?)em$/
}

function isAttributeNameCharacter(character: string): boolean {
	return /[A-Za-z-]/.test(character)
}

function styleIsAllowed(value: string): boolean {
	if (!value.endsWith(';')) return false
	const declarations = value.slice(0, -1).split(';')
	return (
		declarations.length > 0 &&
		declarations.every(declaration => {
			const separator = declaration.indexOf(':')
			if (separator <= 0 || separator !== declaration.lastIndexOf(':')) return false
			const property = declaration.slice(0, separator)
			const styleValue = declaration.slice(separator + 1)
			return ALLOWED_STYLE_VALUES[property]?.test(styleValue) ?? false
		})
	)
}

function classListIsAllowed(value: string): boolean {
	const classes = value.split(' ')
	return classes.length > 0 && classes.every(className => ALLOWED_CLASSES.has(className))
}

function attributeIsAllowed(name: string, value: string): boolean {
	if (name === 'class') return classListIsAllowed(value)
	if (name === 'style') return styleIsAllowed(value)
	return name === 'aria-hidden' && value === 'true'
}

/**
 * Parses KaTeX's emitted tag stream rather than reusing a production renderer
 * or accepting arbitrary HTML. It has no recovery path: any unexpected tag,
 * attribute, quote, or nesting shape makes the caller use local inert text.
 */
function sanitizeKaTeXHtml(html: string): string | null {
	let cursor = 0
	let depth = 0
	let sanitized = ''

	while (cursor < html.length) {
		if (html.startsWith('</span>', cursor)) {
			if (depth === 0) return null
			depth -= 1
			sanitized += '</span>'
			cursor += '</span>'.length
			continue
		}
		if (html.startsWith('<span', cursor)) {
			let attributeCursor = cursor + '<span'.length
			let tag = '<span'
			while (attributeCursor < html.length && html[attributeCursor] !== '>') {
				if (html[attributeCursor] !== ' ') return null
				attributeCursor += 1
				const nameStart = attributeCursor
				while (attributeCursor < html.length && isAttributeNameCharacter(html[attributeCursor])) attributeCursor += 1
				const name = html.slice(nameStart, attributeCursor)
				if (!name || html[attributeCursor] !== '=' || html[attributeCursor + 1] !== '"') return null
				attributeCursor += 2
				const valueStart = attributeCursor
				while (attributeCursor < html.length && html[attributeCursor] !== '"') attributeCursor += 1
				if (attributeCursor >= html.length) return null
				const value = html.slice(valueStart, attributeCursor)
				if (!attributeIsAllowed(name, value)) return null
				tag += ` ${name}="${value}"`
				attributeCursor += 1
			}
			if (html[attributeCursor] !== '>') return null
			depth += 1
			sanitized += `${tag}>`
			cursor = attributeCursor + 1
			continue
		}
		if (html[cursor] === '<') return null
		sanitized += html[cursor]
		cursor += 1
	}

	return depth === 0 ? sanitized : null
}

export function renderIsolatedMath(source: string): string | null {
	try {
		const rendered = katex.renderToString(source, { displayMode: true, output: 'html', strict: 'error', throwOnError: true, trust: false })
		const sanitized = sanitizeKaTeXHtml(rendered)
		return sanitized === null ? null : `<span data-poc-math="katex">${sanitized}</span>`
	} catch {
		return null
	}
}
