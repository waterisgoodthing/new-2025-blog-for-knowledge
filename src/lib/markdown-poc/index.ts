/**
 * Public entry point for the Markdown PoC.
 * Production code must not import this module.
 */

export { renderMarkdownPoC, type PoCRenderOptions } from './render-poc'
export type { PoCRenderResult, PoCWarning, PoCWarningCode, PoCOutcome, TocItem } from './types'
export {
	markdownFixtures,
	markdownFixturesById,
	type MarkdownFixture,
	type MarkdownFixtureExpectation,
	type MarkdownRenderMode,
	type MarkdownFixtureOutcome,
	type MarkdownWarningCode
} from './fixtures'
