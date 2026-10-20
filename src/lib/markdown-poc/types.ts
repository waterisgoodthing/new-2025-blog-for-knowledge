/**
 * PoC output contract types.
 * These define the shared result returned to SSR and client test surfaces.
 * Production code must not import this module.
 */

export interface TocItem {
	id: string
	text: string
	level: number
}

export type PoCWarningCode =
	| 'RAW_HTML_STRIPPED'
	| 'UNSAFE_TAG_STRIPPED'
	| 'EVENT_HANDLER_STRIPPED'
	| 'UNSAFE_URL_STRIPPED'
	| 'UNSAFE_SVG_STRIPPED'
	| 'MALFORMED_MARKDOWN'
	| 'CLIENT_UPDATE_SANITIZED'
	| 'SPECIAL_RENDERER_INERT'
	| 'LOCAL_FALLBACK'

export interface PoCWarning {
	code: PoCWarningCode
	message: string
}

export type PoCOutcome = 'allow' | 'strip' | 'inert' | 'warn' | 'local-fallback'

export interface PoCRenderResult {
	/** Safe HTML string for SSR and client rendering. */
	html: string
	/** Stable table-of-contents entries extracted from headings. */
	toc: TocItem[]
	/** Structured warnings describing what was stripped, safely reduced, or deferred. */
	warnings: PoCWarning[]
	/** Processing outcome for this input. */
	outcome: PoCOutcome
}
